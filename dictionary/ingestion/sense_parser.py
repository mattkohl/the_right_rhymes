from typing import Dict, List, Set, Optional, Tuple
from django.core.exceptions import ObjectDoesNotExist

from dictionary.ingestion.collocate_parser import CollocateParser
from dictionary.ingestion.synset_parser import SynSetParser
from dictionary.ingestion.region_parser import RegionParser
from dictionary.ingestion.semantic_class_parser import SemanticClassParser
from dictionary.ingestion.domain_parser import DomainParser
from dictionary.ingestion.example_parser import ExampleParser
from dictionary.models import SenseParsed, Sense, SenseRelations, SynSet, SemanticClass, Region, Domain, DomainParsed, \
    SemanticClassParsed, SynSetParsed, ExampleParsed, Example, ExampleRelations, RegionParsed, CollocateParsed, \
    Collocate
from dictionary.utils import slugify


class SenseParser:

    @staticmethod
    def parse(d: Dict, headword: str, pos: str, publish: bool) -> SenseParsed:
        try:
            notes = '; '.join([note['#text'].strip() for note in d['note']]) if 'notes' in d else ""
            etymology = '; '.join([etymology['text'] for etymology in d['etym']]) if 'etym' in d else ""
            nt = SenseParsed(
                headword=headword,
                slug=f"{slugify(headword)}#{d['@id']}",
                publish=publish,
                xml_id=d['@id'],
                part_of_speech=pos,
                xml_dict=d,
                definition='; '.join([definition['text'] for definition in d['definition']]),
                notes=notes,
                etymology=etymology
            )
        except Exception as e:
            raise KeyError(f"Sense parse failed: {e}")
        else:
            return nt

    @staticmethod
    def persist(nt: SenseParsed) -> Tuple[Sense, SenseRelations]:
        try:
            sense = Sense.objects.get(xml_id=nt.xml_id)
            sense.json = nt.xml_dict
            sense.headword = nt.headword
            sense.part_of_speech = nt.part_of_speech
            sense.definition = nt.definition
            sense.etymology = nt.etymology
            sense.notes = nt.notes
            sense.slug = nt.slug
            sense.publish = nt.publish
            sense.save()
        except ObjectDoesNotExist:
            sense = Sense.objects.create(
                xml_id=nt.xml_id,
                json=nt.xml_dict,
                headword=nt.headword,
                part_of_speech=nt.part_of_speech,
                definition=nt.definition,
                etymology=nt.etymology,
                notes=nt.notes,
                slug=nt.slug,
                publish=nt.publish,
            )
        return SenseParser.update_relations(sense, nt)

    @staticmethod
    def update_relations(sense: Sense, nt: SenseParsed) -> Tuple[Sense, SenseRelations]:
        purged = SenseParser.purge_relations(sense)
        relations = SenseRelations(
            examples=SenseParser.process_examples(nt, purged),
            domains=SenseParser.process_domains(nt, purged),
            regions=SenseParser.process_regions(nt, purged),
            semantic_classes=SenseParser.process_semantic_classes(nt, purged),
            synset=SenseParser.process_synsets(nt, purged),
            xrefs=[],
            sense_rhymes=[],
            collocates=SenseParser.process_collocates(nt, purged),
            features_entities=[],
            cites_artists=[]
        )
        return purged, relations

    @staticmethod
    def purge_relations(sense: Sense) -> Sense:
        sense.examples.clear()
        sense.domains.clear()
        sense.regions.clear()
        sense.semantic_classes.clear()
        sense.synset.clear()
        sense.xrefs.clear()
        sense.sense_rhymes.clear()
        sense.collocates.clear()
        sense.features_entities.clear()
        sense.cites_artists.clear()
        return sense

    @staticmethod
    def extract_synsets(d: Dict) -> List[SynSetParsed]:
        try:
            return [SynSetParser.parse(synset_name['@target']) for synset_name in d['synSetRef']]
        except KeyError as _:
            return list()

    @staticmethod
    def process_synsets(nt, sense) -> List[SynSet]:
        def process_synset(synset: SynSet) -> SynSet:
            sense.synset.add(synset)
            return synset
        return [process_synset(SynSetParser.persist(d)) for d in SenseParser.extract_synsets(nt.xml_dict)]

    @staticmethod
    def extract_collocates(d: Dict, sense_id: str) -> List[CollocateParsed]:
        try:
            return [CollocateParser.parse(collocate, sense_id) for collocate in d['collocates']['collocate']]
        except KeyError as _:
            return list()

    @staticmethod
    def process_collocates(nt, sense) -> List[Collocate]:
        def process_collocate(collocate: Collocate) -> Collocate:
            sense.collocates.add(collocate)
            return collocate
        return [process_collocate(CollocateParser.persist(d)) for d in SenseParser.extract_collocates(nt.xml_dict, nt.xml_id)]

    @staticmethod
    def extract_semantic_classes(d: Dict) -> List[SemanticClassParsed]:
        try:
            return [SemanticClassParser.parse(semantic_class_name['@type']) for semantic_class_name in d['semanticClass']]
        except KeyError as _:
            return list()

    @staticmethod
    def process_semantic_classes(nt, sense):
        def process_semantic_class(semantic_class: SemanticClass) -> SemanticClass:
            sense.semantic_classs.add(semantic_class)
            return semantic_class
        return [process_semantic_class(SemanticClassParser.persist(d)) for d in SenseParser.extract_semantic_classes(nt.xml_dict)]

    @staticmethod
    def extract_regions(d: Dict) -> List[RegionParsed]:
        try:
            return [RegionParser.parse(region_name['@type']) for region_name in d['region']]
        except KeyError as _:
            return list()

    @staticmethod
    def process_regions(nt, sense):
        def process_region(region: Region) -> Region:
            sense.regions.add(region)
            return region
        return [process_region(RegionParser.persist(d)) for d in SenseParser.extract_regions(nt.xml_dict)]

    @staticmethod
    def extract_domains(d: Dict) -> List[DomainParsed]:
        try:
            return [DomainParser.parse(domain_name['@type']) for domain_name in d['domain']]
        except KeyError as _:
            return list()

    @staticmethod
    def process_domains(nt: SenseParsed, sense: Sense) -> List[Domain]:
        def process_domain(domain: Domain) -> Domain:
            sense.domains.add(domain)
            return domain
        return [process_domain(DomainParser.persist(d)) for d in SenseParser.extract_domains(nt.xml_dict)]

    @staticmethod
    def extract_examples(d: Dict) -> List[ExampleParsed]:
        try:
            examples = d['examples']['example']
            return [ExampleParser.parse(example) for example in examples]
        except KeyError as _:
            return list()

    @staticmethod
    def process_examples(nt: SenseParsed, sense: Sense):
        def process_example(example: Example, example_relations: ExampleRelations) -> Tuple[Example, ExampleRelations]:
            sense.examples.add(example)
            return example, example_relations
        return [process_example(*ExampleParser.persist(d)) for d in SenseParser.extract_examples(nt.xml_dict)]

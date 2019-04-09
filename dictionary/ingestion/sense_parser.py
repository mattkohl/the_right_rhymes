from typing import Dict, List

from dictionary.ingestion.synset_parser import SynSetParser
from dictionary.ingestion.region_parser import RegionParser
from dictionary.ingestion.semantic_class_parser import SemanticClassParser
from dictionary.ingestion.domain_parser import DomainParser
from dictionary.ingestion.example_parser import ExampleParser
from dictionary.models import SenseParsed, Sense, SenseRelations, SynSet, SemanticClass, Region, Domain, DomainParsed, \
    SemanticClassParsed, SynSetParsed, ExampleParsed, Example
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
    def persist(nt: SenseParsed) -> Sense:
        sense, _ = Sense.objects.get_or_create(xml_id=nt.xml_id)
        purged = SenseParser.purge_relations(sense)
        purged.json = nt.xml_dict
        purged.headword = nt.headword
        purged.part_of_speech = nt.part_of_speech
        purged.definition = nt.definition
        purged.etymology = nt.etymology
        purged.notes = nt.notes
        purged.slug = nt.slug
        purged.publish = nt.publish
        purged.save()
        return purged

    @staticmethod
    def update_relations(sense: Sense, nt: SenseParsed) -> (Sense, SenseRelations):
        _ = SenseParser.purge_relations(sense)
        relations = SenseRelations(
            examples=SenseParser.process_examples(nt, sense),
            domains=SenseParser.process_domains(nt, sense),
            regions=SenseParser.process_regions(nt, sense),
            semantic_classes=SenseParser.process_semantic_classes(nt, sense),
            synset=SenseParser.process_synsets(nt, sense),
            xrefs=[],
            sense_rhymes=[],
            collocates=[],
            features_entities=[],
            cites_artists=[]
        )
        return sense, relations

    @staticmethod
    def extract_synsets(d: Dict) -> List[SynSetParsed]:
        try:
            return [SynSetParser.parse(synset_name['@target']) for synset_name in d['synSetRef']]
        except KeyError as _:
            return list()

    @staticmethod
    def process_synsets(nt, sense):
        def process_synset(synset: SynSet) -> SynSet:
            sense.synset.add(synset)
            return synset
        return [process_synset(SynSetParser.persist(d)) for d in SenseParser.extract_synsets(nt.xml_dict)]

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
    def extract_regions(d: Dict) -> List[DomainParsed]:
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
    def process_examples(nt: SenseParsed, sense: Sense) -> List[Example]:
        def process_example(example: Example) -> Example:
            sense.examples.add(example)
            return example
        return [process_example(ExampleParser.persist(d)) for d in SenseParser.extract_examples(nt.xml_dict)]

from django.contrib import admin

from .models import Entry, Editor, Artist, Sense, \
    Example, Domain, SynSet, NamedEntity, Xref, Collocate, \
    SenseRhyme, ExampleRhyme, LyricLink, Place, Song, SemanticClass


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Collocate)
class CollocateAdmin(admin.ModelAdmin):
    list_display = ['collocate_lemma', 'target_slug']


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Editor)
class EditorAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ['headword', 'publish', 'pub_date']


@admin.register(Example)
class ExampleAdmin(admin.ModelAdmin):
    list_display = ['release_date_string', 'artist_name', 'song_title', 'album', 'lyric_text']


@admin.register(ExampleRhyme)
class ExampleRhymeAdmin(admin.ModelAdmin):
    list_display = ['word_one', 'word_two']


@admin.register(LyricLink)
class LyricLinkAdmin(admin.ModelAdmin):
    list_display = ['id', 'link_type', 'target_lemma']


@admin.register(NamedEntity)
class NamedEntityAdmin(admin.ModelAdmin):
    list_display = ['name', 'pref_label', 'entity_type']


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(SemanticClass)
class SemanticClassAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Sense)
class SenseAdmin(admin.ModelAdmin):
    list_display = ['headword', 'part_of_speech', 'xml_id', 'definition']


@admin.register(SenseRhyme)
class SenseRhymeAdmin(admin.ModelAdmin):
    list_display = ['rhyme']


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['artist_name', 'title', 'album']


@admin.register(SynSet)
class SynSetAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Xref)
class XrefAdmin(admin.ModelAdmin):
    list_display = ['xref_word', 'xref_type', 'target_id']




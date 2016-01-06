from django.contrib import admin

from .models import Entry, Editor, Artist, Image, Sense, \
    Example, Domain, SynSet, NamedEntity, Xref


class EntryAdmin(admin.ModelAdmin):
    list_display = ['headword', 'publish', 'pub_date']


class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'origin']


class SenseAdmin(admin.ModelAdmin):
    list_display = ['headword', 'part_of_speech', 'xml_id', 'definition']


class ExampleAdmin(admin.ModelAdmin):
    list_display = ['release_date_string', 'artist_name', 'song_title', 'album', 'lyric_text']


class NamedEntityAdmin(admin.ModelAdmin):
    list_display = ['name', 'pref_label', 'entity_type']


class XrefAdmin(admin.ModelAdmin):
    list_display = ['xref_word', 'xref_type', 'target_id']


admin.site.register(Entry, EntryAdmin)
admin.site.register(Editor)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Image)
admin.site.register(Sense, SenseAdmin)
admin.site.register(Example, ExampleAdmin)
admin.site.register(Domain)
admin.site.register(SynSet)
admin.site.register(NamedEntity, NamedEntityAdmin)
admin.site.register(Xref, XrefAdmin)


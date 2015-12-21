from django.contrib import admin

from .models import Entry, Editor, Artist, Image, Sense, Example, Domain, SynSet, Entity

admin.site.register(Entry)
admin.site.register(Editor)
admin.site.register(Artist)
admin.site.register(Image)
admin.site.register(Sense)
admin.site.register(Example)
admin.site.register(Domain)
admin.site.register(SynSet)
admin.site.register(Entity)


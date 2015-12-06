from django.contrib import admin

from .models import Word, Editor, Artist, Image, Sense, Example, Domain, SynSet

admin.site.register(Word)
admin.site.register(Editor)
admin.site.register(Artist)
admin.site.register(Image)
admin.site.register(Sense)
admin.site.register(Example)
admin.site.register(Domain)
admin.site.register(SynSet)


from django.contrib import admin

from .models import Entry, Editor, Artist, Image, Sense, Example

admin.site.register(Entry)
admin.site.register(Editor)
admin.site.register(Artist)
admin.site.register(Image)
admin.site.register(Sense)
admin.site.register(Example)


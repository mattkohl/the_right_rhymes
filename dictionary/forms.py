from django import forms
from dictionary.models import Song, Sense


class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ("id", "xml_id", "release_date", "release_date_string", "title", "artist_name", "album", "lyrics", "release_date_verified")


class SenseForm(forms.ModelForm):
    class Meta:
        model = Sense
        fields = ("id", "xml_id", "headword", "slug", "part_of_speech", "definition", "etymology", "notes")
#
#
# class ExampleForm(forms.ModelForm):
#     class Meta:
#         model = Example
#         fields = ("id", "artist_name", "song_title", "release_date", "release_date_string", "album", "lyric_text")
from django import forms
from dictionary.models import Song, Sense


class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ("id", "xml_id", "release_date", "release_date_string", "title", "artist_name", "album", "lyrics", "release_date_verified")
        widgets = {
            "title": forms.fields.TextInput(attrs={
                "placeholder": "Enter the song title",
                "class": "form-control",
            }),
            "album": forms.fields.TextInput(attrs={
                "placeholder": "Enter the album title",
                "class": "form-control",
            }),
        }


class SenseForm(forms.ModelForm):
    class Meta:
        model = Sense
        fields = ("id", "xml_id", "headword", "slug", "part_of_speech", "definition", "etymology", "notes")

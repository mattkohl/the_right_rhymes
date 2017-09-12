from django.test import TestCase
from dictionary.forms import SongForm


class SongFormTest(TestCase):

    def test_form_title_input_has_placeholder_and_css_classes(self):
        form = SongForm()
        self.assertIn('placeholder="Enter the song title"', form.as_p())
        self.assertIn('class="form-control"', form.as_p())

    def test_form_validation_for_blank_items(self):
        form = SongForm(data={"title": ""})
        self.assertFalse(form.is_valid())

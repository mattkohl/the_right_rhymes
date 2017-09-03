import unittest
from unittest import skip
from unittest.mock import patch, Mock
from django.test import TestCase
from dictionary.models import Song, Sense
from dictionary.forms import SongForm, SenseForm


class SongFormTest(TestCase):

    def test_form_title_input_has_placeholder_and_css_classes(self):
        form = SongForm()
        self.assertIn('placeholder="Enter the song title"', form.as_p())
        self.assertIn('class="form-control"', form.as_p())

    def test_form_validation_for_blank_items(self):
        form = SongForm(data={"title": ""})
        self.assertFalse(form.is_valid())

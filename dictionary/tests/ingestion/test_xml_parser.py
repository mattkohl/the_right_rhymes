# class TestTRRExample(BaseTest):
#
#     @mock.patch("dictionary.management.commands.xml_handler.TRRExample.update_example")
#     def test_construct(self, mock_update_example):
#         mock_update_example.return_value = None
#         example_dict = {
#             "@id": "someId",
#             "date": "2017-05-05",
#             "songTitle": "Jammin",
#             "album": "Foo",
#             "artist": "Bar",
#             "lyric": {"text": "Baz"}
#         }
#         result = TRRExample(self.mad_sense, example_dict)
#         self.assertIsInstance(result, TRRExample)
#
#
# class TestTRRSong(BaseTest):
#
#     def test_construct(self):
#
#         class Artist_(object):
#             def __init__(self, artist_object):
#                 self.artist_object = artist_object
#
#         es_ = Artist_(self.erick_sermon)
#
#         xml_id = "a1234"
#         release_date = "1998-01-01"
#         title = "foo"
#         album = "bar"
#         artist_name = "Erick Sermon"
#         slug = "erick-sermon-foo"
#         artist_slug = "erick-sermon"
#         result = TRRSong(xml_id=xml_id,
#                          release_date=release_date,
#                          release_date_string=release_date,
#                          song_title=title,
#                          artist_name=artist_name,
#                          artist_slug=artist_slug,
#                          primary_artists=[es_],
#                          feat_artists=[],
#                          album=album)
#         self.assertIsInstance(result, TRRSong)
#         self.assertEqual(result.slug, slug)
#
#
# class TestTRRPlace(BaseTest):
#
#     def test_construct(self):
#         result = TRRPlace("Paris, Texas, USA")
#         self.assertIsInstance(result, TRRPlace)
#         self.assertEqual(Place.objects.filter(slug="paris-texas-usa").count(), 1)
#         self.assertEqual(Place.objects.filter(slug="texas-usa").count(), 1)
#
#
# class TestTRRLyricLink(BaseTest):
#
#     bad_position_ex = {
#         'album': 'By Any Means',
#         'songTitle': 'Arm and Hammer',
#         'artist': 'Kevin Gates',
#         '@id': '51232',
#         'date': '2014-03-18',
#         'lyric': {
#             'text': 'She like, "Bae, I\'m at the store"',
#             'rf': [{'@lemma': 'bae', '@position': '12', '#text': 'Bae', '@target': 'e2667_n_1'}]
#          }
#     }
#     good_position_ex = {
#         'album': 'King Push',
#         'songTitle': 'Drug Dealers Anonymous',
#         'artist': 'Pusha T',
#         '@id': '66175',
#         'feat': ['Jay Z'],
#         'date': '2015-12-18',
#         'lyric': {
#             'text': 'He told 12, "Gimme 12"',
#             'rf': [
#                 {'@lemma': '12', '@position': '8', '#text': '12', '@target': 'e2045_n_1'},
#                 {'@lemma': '12', '@position': '19', '#text': '12', '@target': 'e2045_n_1'}
#             ]
#         }
#     }
#
#     def test_fix_bad_position(self):
#         link_dict = self.bad_position_ex['lyric']['rf'][0]
#         link_type = 'rf'
#         example_text = self.bad_position_ex['lyric']['text']
#         l1 = TRRLyricLink(link_dict=link_dict, link_type=link_type, example_text=example_text)
#         self.assertEqual(l1.position, 11)
#
#     def test_confirm_good_position(self):
#         link_dict = self.good_position_ex['lyric']['rf'][0]
#         link_type = 'rf'
#         example_text = self.good_position_ex['lyric']['text']
#         l1 = TRRLyricLink(link_dict=link_dict, link_type=link_type, example_text=example_text)
#         self.assertEqual(l1.position, 8)


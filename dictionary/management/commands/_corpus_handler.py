import sqlite3

from dictionary.models import Song, Artist
from ._xml_handler import clean_up_date
from dictionary.utils import slugify


def process_row(row):
    xml_id, artist, album, release_date, song_title, feat, lyrics, discogs_date, rel_date_verified, lyrics_verified = row

    song_object, created = get_song(xml_id)
    if created or song_object.slug is None:
        if release_date == 0:
            release_date = "0001-01-01"
        song_object.release_date = clean_up_date(str(release_date))
        song_object.release_date_string = str(release_date)
        artist_object = get_artist(artist)
        song_object.artist_name = artist_object.name
        song_object.artist_slug = artist_object.slug
        song_object.artist.add(artist_object)
        artist_object.primary_songs.add(song_object)
        if feat:
            feat_artists = [get_artist(f) for f in feat.split('; ')]
            _ = [song_object.feat_artist.add(f) for f in feat_artists]
            _ = [feat_object.featured_songs.add(song_object) for feat_object in feat_artists]
        song_object.title = song_title
        song_object.album = album
        song_object.slug = slugify(song_object.artist_name + ' ' + song_title)
    song_object.lyrics = lyrics

    if rel_date_verified == 'MBK':
        song_object.release_date_verified = True
    else:
        song_object.release_date_verified = False
    song_object.save()
    print('Processed', xml_id, artist, '- "' + song_title + '"')


def get_artist(name):
    slug = slugify(name)
    artist_object, created = Artist.objects.get_or_create(slug=slug)
    if not created or artist_object.name is None:
        artist_object.name = name
        artist_object.save()
    return artist_object


def get_song(xml_id):
    song_object, created = Song.objects.get_or_create(xml_id=xml_id)
    return song_object, created


def main(location='../corpus/dbs/HH.db'):
    conn = sqlite3.connect(location)
    cursor = conn.execute('select * from Songs')
    _ = [process_row(row) for row in cursor]

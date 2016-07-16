import sqlite3

from dictionary.models import Song


def process_row(row):
    xml_id, artist, album, \
    release_date, song_title, \
    feat, lyrics, discogs_date, \
    rel_date_verified, lyricsVerified = row

    song, created = get_song(xml_id)
    if not created:
        song.lyrics = lyrics
        song.release_date_verified = True
        song.save()
    else:
        #TODO write this!
        pass


def get_song(xml_id):
    song_object, created = Song.objects.get_or_create(xml_id=xml_id)
    return song_object, created


def main(location='../corpus/dbs/HH.db'):
    conn = sqlite3.connect(location)
    cursor = conn.execute('select * from Songs')
    [process_row(row) for row in cursor]
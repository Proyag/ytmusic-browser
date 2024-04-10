import logging
import argparse

from ytmusicapi import YTMusic
from flask_table import Table, Col, BoolCol, DatetimeCol
from flask_table.html import element
from flask import Flask, request, url_for, render_template

MAX_LIBRARY_SONGS = 999999

class Song:
    def __init__(self, song_info: dict):
        self.id = song_info['videoId']
        self.title = song_info['title']
        self.artists = song_info['artists']
        self.album = song_info['album']
        self.url = f"https://music.youtube.com/watch?v={self.id}"
        self.duration = song_info['duration_seconds']
        self.likeStatus = song_info['likeStatus']
        self.inLibrary = song_info['inLibrary']

    def get_id(self) -> str:
        """Get the unique ID for song"""
        return self.id

    def get_url(self) -> str:
        """Get Youtube Music URL for song"""
        return self.url

    def get_main_artist(self) -> str:
        """Get the artist"""
        return self.main_artist

    def get_title(self) -> str:
        """Get the song title"""
        return self.title

    def join_artists(self) -> str:
        """Join artists into a string"""
        return '& '.join([artist['name'] for artist in self.artists])

    def __str__(self):
        return f"{self.join_artists}; {self.title}"

    def __repr__(self):
        return f"Song: {self.title}; Artist: {self.join_artists}; ID: {self.id}"
    

class TitleCol(Col):
    def td_contents(self, item, attr_list):
        name = self.from_attr_list(item, attr_list)
        id = self.from_attr_list(item, ['id'])
        url = f"https://music.youtube.com/watch?v={id}"
        return element('a', {'href': url}, content=name)


class AlbumCol(Col):
    def td_contents(self, item, attr_list):
        id = self.from_attr_list(item, attr_list)['id']
        name = self.from_attr_list(item, attr_list)['name']
        url = f"https://music.youtube.com/browse/{id}"
        return element('a', {'href': url}, content=name)
    

class ArtistsCol(Col):
    def td_contents(self, item, attr_list):
        ids = (artist['id'] for artist in self.from_attr_list(item, attr_list))
        names = (artist['name'] for artist in self.from_attr_list(item, attr_list))

        content = []
        for id, name in zip(ids, names):
            content.append(element('a', {'href': f"https://music.youtube.com/channel/{id}"}, content=name))
        return ' & '.join(content)


class LibraryTable(Table):
    title = TitleCol('Title')
    artists = ArtistsCol('Artist')
    album = AlbumCol('Album')
    duration = DatetimeCol('Duration', datetime_format='m:ss')
    # likeStatus = Col('Like Status')
    # inLibrary = BoolCol('In Library')

    allow_sort = True

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction =  'desc'
        else:
            direction = 'asc'
        return url_for('index', sort=col_key, direction=direction)


class Library:
    def __init__(self) -> None:
        self.init_library()

    def init_library(self) -> None:
        """Get library of songs from YTMusic"""
        logging.info("Getting library from YTMusic")
        # Authenticate
        ytmusic = YTMusic('oauth.json')
        self.songs = [Song(song) for song in ytmusic.get_library_songs(limit=MAX_LIBRARY_SONGS, order='recently_added')]
        if len(self.songs) == 0:
            logging.error("No songs found in library")
            exit(1)
        logging.info(f"Got {len(self.songs)} songs in library")

    def get_sorted_by(self, sort, reverse=False):
        if sort == 'title':
            return sorted(self.get_song_list(),
                          key=lambda x: getattr(x, sort).casefold(),
                          reverse=reverse)
        elif sort == 'album':
            return sorted(
                self.get_song_list(),
                key=lambda x: getattr(x, sort)['name'].casefold(),
                reverse=reverse)
        elif sort == 'artists':
            return sorted(
                self.get_song_list(),
                key=lambda x: getattr(x, sort)[0]['name'].casefold(),
                reverse=reverse)
        return sorted(
            self.get_song_list(),
            key=lambda x: getattr(x, sort),
            reverse=reverse)
    
    def get_song_list(self) -> list:
        """Get list of songs"""
        return self.songs

    # def search_songs(self, substr, max_results=20):
    #     """Find songs (artist + title) matching a substring"""
    #     n_results = 0
    #     substr = substr.lower()
    #     logging.info(f"Suggesting songs matching {substr}")
    #     for (_, song) in self.songs.items():
    #         if substr in str(song).lower():
    #             n_results += 1
    #             yield song
    #             if n_results >= max_results:
    #                 break

app = Flask(__name__)

@app.route('/')
@app.route('/library')
def index():
    sort = request.args.get('sort', 'title')
    reverse = (request.args.get('direction', 'asc') == 'desc')
    table = LibraryTable(lib.get_sorted_by(sort=sort, reverse=reverse),
                          sort_by=sort,
                          sort_reverse=reverse)
    return render_template('library.html', libtable=table)

if __name__ == '__main__':
    logging.basicConfig(
        format='[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S',
        level=logging.INFO
    )

    parser = argparse.ArgumentParser(description='YTMusic library viewer',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--port', type=int, default=5000, help='Port to run the web server')
    args = parser.parse_args()

    lib = Library()
    app.run(debug=True, port=args.port)

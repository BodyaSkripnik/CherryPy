import json
import cherrypy
import sqlite3
import os


def db_request(query):
    data_base = os.environ['db_name']
    con = sqlite3.connect(data_base)
    # con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    result = cur.fetchall()
    # result = [dict(i) for i in cur.fetchall]
    con.close()
    return result

class Router(object):
    def __init__(self):
        self.albums = Album()
        self.song = Song()
        self.band = Band()
        self.search = Search()

    def _cp_dispatch(self, vpath):

        if len(vpath) == 1:  # /search
            resource_type = vpath.pop(0)
            if resource_type == 'search':
                return self.search
            else:
                return self

        elif len(vpath) == 2:  # /artist/<artist>
            vpath.pop(0)
            cherrypy.request.params['name'] = vpath.pop()
            return self.band

        elif len(vpath) == 4:  # /artist/<artist>/song/<song>
            vpath.pop(0)
            cherrypy.request.params['artist'] = vpath.pop(0)  # artist name
            resource_type = vpath.pop(0)

            if resource_type == 'song':
                cherrypy.request.params['name'] = vpath.pop(0)  # /song name/
                return self.song

            elif resource_type == 'album':
                cherrypy.request.params['title'] = vpath.pop(0)  # /album title/
                return self.albums

            else:
                return self
        else:
            vpath = []
            return self


    @cherrypy.expose
    def index(self):
        return 'bad request'


class Band(object):
    @cherrypy.expose
    def index(self, name):
        query = f"""select DISTINCT
	                    artist.artist_name, album.album_name, album.album_id
                    FROM track_list
                    JOIN artist on track_list.artist_id = artist.id_artist
                    JOIN album on track_list.album_id = album.album_id
                    WHERE artist.artist_name = '{name}'"""
        result = db_request(query)
        print(result)
        spisok = []
        for row in result:
            print(row[0])
            text = row[0]
            text1 = row[1]
            text2 = row[2]
            spisok.append([text,text1,text2])
            print(spisok)
            newlist = []
            for el in spisok:
                print(el[0],'hello')
                songs = {'artist_name':el[0],
                    'album_name':el[1],
                    'album_id':el[2]}
                newlist.append(songs)
        return json.dumps(newlist)


class Album(object):
    @cherrypy.expose
    def index(self, artist, title):
        data_base = os.environ['db_name']
        con = sqlite3.connect(data_base)
        cur = con.cursor()
        cur.execute(f""" select DISTINCT
	                song.song_name,song.song_year
                    FROM track_list
                    JOIN album on track_list.album_id = album.album_id
					JOIN artist on track_list.artist_id = artist.id_artist
					JOIN song on track_list.song_id = song.song_id
                    WHERE album.album_name = '{title}' and artist.artist_name = '{artist}'""")
        spisok = []
        for row in cur.fetchall():
            text = row[0]
            text1= row[1]
            spisok.append([text,text1])
            newlist = []
            for el in spisok:
                print(el[0],'hello')
                songs = {'song_name':el[0],
                    'song_year':el[1]}
                newlist.append(songs)

        return json.dumps(newlist)


class Song(object):
    @cherrypy.expose
    def index(self, artist, name):
        data_base = os.environ['db_name']
        con = sqlite3.connect(data_base)
        cur = con.cursor()
        cur.execute(f"""SELECT artist.artist_name,album.album_name,album.album_year FROM track_list
                    JOIN album on track_list.album_id = album.album_id
					JOIN artist on track_list.artist_id = artist.id_artist
					JOIN song on track_list.song_id = song.song_id
                    WHERE song.song_name = '{name}' and artist.artist_name = '{artist}'""")
        spisok = []
        for row in cur.fetchall():
            text = row[0]
            text1 = row[1]
            text2 = row[2]
            spisok.append([text,text1,text2])
            newlist = []
            for el in spisok:
                print(el[0],'hello')
                songs = {'artist_name':el[0],
                    'album_name':el[1],
                    'album_year':el[2]}
                newlist.append(songs)
        return json.dumps(newlist)


class Search(object):
    @cherrypy.expose
    def index(self, search_string):
        search_dict = {
            'artist': db_request(f""" SELECT artist.artist_name
                FROM artist
                WHERE artist.artist_name like '%{search_string}%' """),
            'album': db_request(f""" SELECT album.album_name
                FROM album
                WHERE album.album_name like '%{search_string}%' """),
            'song': db_request(f""" SELECT song.song_name
                FROM song
                WHERE song.song_name like '%{search_string}%' """)
        }
        return json.dumps(search_dict)

if __name__ == '__main__':
    cherrypy.quickstart(Router())
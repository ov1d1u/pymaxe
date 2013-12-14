import urllib
import urllib2
import json
import gobject
import threading


API_KEY = 'GC6OGUMVC4BYZUBY7'


def searchArtist(query, callback):
    artists = []
    url = 'http://developer.echonest.com/api/v4/artist/search?api_key={0}&name={1}'.format(API_KEY, urllib.quote_plus(query))
    f = urllib2.urlopen(url)
    data = json.loads(f.read())
    if 'response' in data:
        response = data['response']
        for artist in response['artists']:
            artists.append(artist['name'])

    threading.Thread(target=searchTitles, args=(query, artists, callback)).start()


def searchTitles(query, artists, callback):
    url = 'http://developer.echonest.com/api/v4/song/search?api_key={0}&title={1}'.format(API_KEY, urllib.quote_plus(query))
    titles = artists
    f = urllib2.urlopen(url)
    data = json.loads(f.read())
    if 'response' in data:
        response = data['response']
        for song in response['songs']:
            titles.append(song['title'])

    results = titles[:5]
    gobject.idle_add(callback, results)


def suggestionsFor(query, callback):
    print 'Searching...'
    threading.Thread(target=searchArtist, args=(query, callback)).start()
    return False

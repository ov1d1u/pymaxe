#-*- coding: utf-8 -*-
import urllib, urllib2, gobject, thread2

class Album:
    def __init__(self, cb):
        self.api = '48072aa5c876eba10b3f60298afaf100'
        self.callback = cb
        self.isRetrieving = False
        self.getCover = True

    def details(self, aid, getCover = True):
        albumID = aid[8:]
        self.getCover = getCover
        if albumID == '':
            gobject.idle_add(self.callback, None)
            return
        self.thread = thread2.Thread(target=self.downloadData, args=(albumID, ))
        self.thread.start()

    def downloadData(self, albumID):
        albumData = {}
        self.isRetrieving = True
        url = 'http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key=' + self.api + '&mbid=' + albumID
        req = urllib2.Request(url)
        getdata = urllib2.urlopen(req)
        data = getdata.read()
        if not '<lfm status="ok">' in data:
            gobject.idle_add(self.callback, None)
            return
        mbid = self.extract(data, '<mbid>', '</mbid>')
        name = self.extract(data, '<name>', '</name>')
        name = name.replace('&amp;', '&')
        artist = self.extract(data, '<artist>', '</artist>')
        artist = artist.replace('&amp;', '&')
        release = self.extract(data, '<releasedate>', '</releasedate>')
        release = release.lstrip()
        url = self.extract(data, '<url>', '</url>')
        cover = self.extract(data, '<image size="large">', '</image>')
        tracks = str(data.count('</track>'))
        albumData = {
                'name' : name,
                'artist' : artist,
                'release' : release,
                'url' : url,
                'tracks' : tracks,
                'cover' : cover,
                'mbid' : mbid
        }
        self.isRetrieving = False
        gobject.idle_add(self.callback, albumData)
        return albumData

    def getAlbumTracks(self, albumID):
        self.isRetrieving = True
        url = 'http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key=' + self.api + '&mbid=' + albumID
        req = urllib2.Request(url)
        getdata = urllib2.urlopen(req)
        data = getdata.read()
        tracks = []
        gtracks = data.split('<track ')
        gtracks.pop(0)
        for x in gtracks:
            try:
                gartist = x.split('<artist>')
                artist = self.extract(gartist[1], '<name>', '</name>')
                artist = artist.replace('&amp;', '&')
                title = self.extract(gartist[0], '<name>', '</name>')
                title = title.replace('&amp;', '&')
                tracks.append([artist, title])
            except Exception, e:
                pass
        self.isRetrieving = False
        return tracks

    def cancel(self):
        if self.thread.isAlive():
            self.thread.terminate()
        self.isRetrieving = False
        gobject.idle_add(self.callback, None)

    def extract(self, string, start, end):
        try:
            gdata = string.split(start)
            gdata = gdata[1].split(end)
            data = gdata[0]
        except:
            data = ''
        return data

#-*- coding: utf-8 -*-
import thread2, gobject, urllib, urllib2, cStringIO
from PIL import Image

class coverFinder:
    def __init__(self, pymaxe, callback):
        self.pymaxe = pymaxe
        self.callback = callback
        self.api = '48072aa5c876eba10b3f60298afaf100'
        self.searching = False

    def createQuery(self, string, mbid = None):
        if not mbid:
            query = urllib.quote(string.encode('utf-8'))
            return 'http://ws.audioscrobbler.com/2.0/?method=track.search&track=' + query + '&api_key=' + self.api
        else:
            return 'http://ws.audioscrobbler.com/2.0/?method=album.getinfo&mbid=' + mbid + '&api_key=' + self.api

    def searchCover(self, string, mbid = None):
        self.searching = True
        url = self.createQuery(string, mbid)
        self.thread = thread2.Thread(target=self.getCover, args=(url,))
        self.thread.start()

    def getCover(self, url):
        try:
            req = urllib2.Request(url)
            getdata = urllib2.urlopen(req)
            data = getdata.read()
            coverUrl = self.extract(data, '<image size="large">', '</image>')
            req = urllib2.Request(coverUrl)
            getdata = urllib2.urlopen(req)
            data = getdata.read()
            img = cStringIO.StringIO(data)
            im = Image.open(img)
            im = im.resize((128, 128), Image.ANTIALIAS)
            self.searching = False
            gobject.idle_add(self.callback, im)
        except:
            self.searching = False
            gobject.idle_add(self.callback, None)

    def abort(self):
        if self.searching:
            try:
                self.thread.terminate()
            except:
                pass
            self.searching = False

    def extract(self, string, start, end):
        try:
            gdata = string.split(start)
            gdata = gdata[1].split(end)
            data = gdata[0]
        except:
            data = ''
        return data

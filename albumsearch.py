#-*- coding: utf-8 -*-
import urllib, urllib2, gobject

class AlbumSearch:
	def __init__(self, callback):
		self.api = '48072aa5c876eba10b3f60298afaf100'
		self.cb = callback
		
	def search(self, query):
		print 'album search'
		ret = []
		qquery = urllib.quote(query)
		req = urllib2.Request('http://ws.audioscrobbler.com/2.0/?method=album.search&album=' + qquery + '&api_key=' + self.api)
		getdata = urllib2.urlopen(req)
		data = getdata.read()
		albums = data.split('<album>')
		albums.pop(0)
		for x in albums:
			galbum = x.split('</album>')
			albumdata = galbum[0]
			artist = self.extract(albumdata, '<artist>', '</artist>')
			artist = artist.replace('&amp;', '&')
			name = self.extract(albumdata, '<name>', '</name>')
			name = name.replace('&amp;', '&')
			aid = self.extract(albumdata, '<mbid>', '</mbid>')
			if aid != '':
				ret.append([0x03, artist + ' - ' + name, 'album://'+aid, ''])
		return {"AlbumSearch" : ret}
			
	def extract(self, string, start, end):
		try:
			gdata = string.split(start)
			gdata = gdata[1].split(end)
			data = gdata[0]
		except:
			data = ''
		return data
		
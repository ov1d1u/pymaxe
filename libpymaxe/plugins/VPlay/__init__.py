# -*- coding: utf-8 -*-
import HTMLParser, urllib2, urllib, datetime, os
h = HTMLParser.HTMLParser()

FILE_TYPE_AUDIO = 0x01
FILE_TYPE_VIDEO = 0x02

class Plugin:
	def __init__(self):
		self.pluginName = 'VPlay Downloader'
		self.version = '0.1'
		self.author = 'Ovidiu D. Niţan'
		self.homepage = 'http://www.vplay.ro'
		self.update = ''
		self.matchurls = ['vplay.ro']
	
	def search(self, query):
		res = []
		req = urllib2.Request('http://vplay.ro/search/' + urllib.quote(query))
		getdata = urllib2.urlopen(req)
		data = getdata.read()
		results = data.split('class="article" data=')
		results.pop(0)
		for x in results:
			try:
				gid = x.split('"')
				gid = gid[1].split('">')
				url = 'http://vplay.ro' + '/watch/' + gid[0]
				gtitle = x.split('<span class="article-title">')
				gtitle = gtitle[1].split('</span>')
				title = gtitle[0]
				gtime = x.split("<b>");
				gtime = gtime[1].split("</b>");
				timp = gtime[0]
				res.append([FILE_TYPE_VIDEO, title, url, timp])
			except Exception, e:
				pass
		return res
		
	def fileData(self, url):
		req = urllib2.Request(url)
		getdata = urllib2.urlopen(req)
		data = getdata.read()
		gtitlu = data.split('<title>')
		gtitlu = gtitlu[1].split('</title>')
		titlu = gtitlu[0]
		gtimp = data.split('length_seconds=')
		gtimp = gtimp[1].split('\\')
		timp = str(datetime.timedelta(seconds=int(gtimp[0])))[2:]
		pdata = urllib.unquote(urllib.unquote(data))
		gufm = pdata.split("url_encoded_fmt_stream_map=")
		gufm = gufm[1].split('allowscriptaccess')
		gufm = gufm[0].split(',')
		gufm.pop()
		calitati = {}
		for x in gufm:
			if 'codecs' in x:
				gdu = x.split("url=")
				gdu = gdu[1].split("&fallback_host")
				du = gdu[0]
				if '&quality=' in x:
					gi = x.split("&quality=")
					gi = gi[1].split('&')
					i = gi[0]
					calitati[i] = du
		downurl = self.select_quality(calitati)
		rq = urllib2.Request(downurl)
		gtdata = urllib2.urlopen(rq)
		contentlength = gtdata.info().getheader('Content-Length')
		data = {"url" : url,
			"title" : self.unescape(titlu),
			"length" : timp,
			"type" : FILE_TYPE_VIDEO,
			"fsize" : contentlength,
			"downurl" : downurl
		}
		return data
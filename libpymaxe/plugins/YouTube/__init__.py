# -*- coding: utf-8 -*-
import HTMLParser
import urllib2
import urllib
import datetime
import os
import json
import re
import pafy
h = HTMLParser.HTMLParser()

FILE_TYPE_AUDIO = 0x01
FILE_TYPE_VIDEO = 0x02
_NO_DEFAULT = object()


class Plugin:
    def __init__(self):
        self.pluginName = 'YouTube Downloader'
        self.version = '1.0beta'
        self.author = 'Ovidiu D. Niţan'
        self.homepage = 'http://www.google.ro'
        self.update = 'http://www.google.com'
        self.matchurls = ['youtube.com']
        self.quality = 'medium'  # large, hd1080, hd720
        self.threaded_dnld = True

    def search(self, query):
        res = []
        print 'http://gdata.youtube.com/feeds/api/videos?q=' + urllib.quote(query) + '&alt=json'
        req = urllib2.Request('http://gdata.youtube.com/feeds/api/videos?q=' + urllib.quote(query) + '&alt=json')
        getdata = urllib2.urlopen(req)
        data = json.loads(getdata.read())
        results = data['feed']['entry']
        for entry in results:
            try:
                url = entry['link'][0]['href']
                title = entry['title']['$t']
                duration = str(datetime.timedelta(seconds=int(entry['media$group']['media$content'][0]['duration'])))[2:]
                res.append([FILE_TYPE_VIDEO, self.unescape(title), url, duration, False])
            except:
                pass
        return res

    def fileData(self, url):
        vcode = os.path.basename(url)
        try:
            gvcode = vcode.split('v=')
            gvcode = gvcode[1].split('&')
            vcode = gvcode[0]
        except:
            vcode = vcode
        url = 'http://www.youtube.com/watch?v=' + vcode
        video_i = pafy.new(url)
        title = video_i.title
        length = video_i.length
        downurl = self.select_quality(video_i.streams)

        rq = urllib2.Request(downurl)
        gtdata = urllib2.urlopen(rq)
        contentlength = gtdata.info().getheader('Content-Length')
        data = {"url": url,
                "title": title,
                "length": length,
                "type": FILE_TYPE_VIDEO,
                "fsize": contentlength,
                "downurl": downurl,
                "hiquality": False}
        return data

    def select_quality(self, qualities):
        qdict = {}
        for s in qualities:
            if s.vidformat != 'video/webm':
                qdict[s.itag] = s.url

        if self.quality == 'hd1080' or self.quality == 'hd720':
            if '22' in qdict:
                return qdict['22']
        if self.quality == 'large':
            if '18' in qdict:
                return qdict['18']
        if self.quality == 'medium':
            if '5' in qdict:
                return qdict['5']
        if self.quality == 'low':
            if '17' in qdict:
                return qdict['17']

        # fallback
        print 'Fallback quality selection'
        for s in qualities:
            if s.vidformat == 'video/flv':
                return s.url

    def unescape(self, s):
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        # this has to be last:
        s = s.replace("&amp;", "&")
        return s

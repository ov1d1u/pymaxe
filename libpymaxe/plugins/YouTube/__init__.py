# -*- coding: utf-8 -*-
import HTMLParser, urllib2, urllib, datetime, os
import json
h = HTMLParser.HTMLParser()

FILE_TYPE_AUDIO = 0x01
FILE_TYPE_VIDEO = 0x02

class Plugin:
    def __init__(self):
        self.pluginName = 'YouTube Downloader'
        self.version = '0.991'
        self.author = 'Ovidiu D. Niţan'
        self.homepage = 'http://www.google.ro'
        self.update = 'http://www.google.com'
        self.matchurls = ['youtube.com']
        self.quality = 'medium' # large, hd1080, hd720

    def search(self, query):
        res = []
        req = urllib2.Request('http://gdata.youtube.com/feeds/api/videos?q=' + urllib.quote(query) + '&max-results=15');
        getdata = urllib2.urlopen(req);
        data = getdata.read();
        results = data.split('<entry>')
        results.pop(0)
        for x in results:
            try:
                gid = x.split('<id>')
                gid = gid[1].split('</id>')
                url = 'http://www.youtube.com/watch?v=' + os.path.basename(gid[0])
                gtitle = x.split("<title type='text'>");
                gtitle = gtitle[1].split('</title>')
                title = urllib.unquote(gtitle[0])
                gtime = x.split("duration='");
                gtime = gtime[1].split("'");
                timp = str(datetime.timedelta(seconds=int(gtime[0])))[2:]
                res.append([FILE_TYPE_VIDEO, self.unescape(title), url, timp])
            except Exception, e:
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
        req = urllib2.Request(url);
        getdata = urllib2.urlopen(req);
        data = getdata.read();
        gjson = data.split('yt.playerConfig = ')
        gjson = gjson[1].split('};')
        json_data = json.loads(gjson[0] + '}')
        timp = str(datetime.timedelta(seconds=json_data['args']['length_seconds']))[2:]
        title = json_data['args']['title']
        itags = json_data['args']['url_encoded_fmt_stream_map'].split(',')
        qualities = {}
        for itag in itags:
            known_itags = ['5', '34', '35', '22', '37']
            itag_id_start = itag.split('itag=')[1]
            if '&' in itag_id_start:
                itag_id = itag_id_start.split('&')[0]
            else:
                itag_id = itag_id_start.split(',')[0]   # youtube is pissing me off

            if not itag_id in known_itags:
                continue

            itag_sig = itag.split('sig=')[1][:81]
            itag_url = urllib.unquote(itag.split('url=')[1].split('&')[0])
            if ',' in itag_url:
                itag_url = itag_url.split(',')[0]

            if itag_id == '5':
                qualities['low'] = itag_url + '&signature=' + itag_sig
            if itag_id == '34':
                qualities['medium'] = itag_url + '&signature=' + itag_sig
            if itag_id == '35':
                qualities['large'] = itag_url + '&signature=' + itag_sig
            if itag_id == '22':
                qualities['hd720'] = itag_url + '&signature=' + itag_sig
            if itag_id == '37':
                qualities['hd1080'] = itag_url + '&signature=' + itag_sig
        downurl = self.select_quality(qualities)

        rq = urllib2.Request(downurl)
        gtdata = urllib2.urlopen(rq)
        contentlength = gtdata.info().getheader('Content-Length')
        data = {"url" : url,
                "title" : self.unescape(title),
                "length" : timp,
                "type" : FILE_TYPE_VIDEO,
                "fsize" : contentlength,
                "downurl" : downurl
        }
        return data

    def select_quality(self, qualities):
        q = ['hd1080', 'hd720', 'large', 'medium', 'low']
        if self.quality in qualities:
            return qualities[self.quality]
        for x in q:
            if qualities.has_key(x):
                return qualities[x]
        return qualities['medium']

    def unescape(self, s):
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        # this has to be last:
        s = s.replace("&amp;", "&")
        return s

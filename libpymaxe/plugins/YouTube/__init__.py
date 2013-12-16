# -*- coding: utf-8 -*-
import HTMLParser
import urllib2
import urllib
import datetime
import os
import json
h = HTMLParser.HTMLParser()

FILE_TYPE_AUDIO = 0x01
FILE_TYPE_VIDEO = 0x02


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
            #try:
                url = entry['link'][0]['href']
                title = entry['title']['$t']
                duration = str(datetime.timedelta(seconds=int(entry['media$group']['media$content'][0]['duration'])))[2:]
                res.append([FILE_TYPE_VIDEO, self.unescape(title), url, duration, False])
            #except:
            #    pass
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
        req = urllib2.Request(url)
        getdata = urllib2.urlopen(req)
        data = getdata.read()
        gjson = data.split('ytplayer.config = ')
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

            if 'sig=' in itag:
                itag_sig = itag.split('sig=')[1][:81]
            else:
                itag_sig = self._decrypt_signature(itag.split('s=')[1].split('&')[0])

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
        data = {"url": url,
                "title": self.unescape(title),
                "length": timp,
                "type": FILE_TYPE_VIDEO,
                "fsize": contentlength,
                "downurl": downurl,
                "hiquality": False}
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

    def _decrypt_signature(self, s):
        """Decrypt the key the two subkeys must have a length of 43"""
        """Source: youtube-dl project"""
        if len(s) == 92:
            return s[25] + s[3:25] + s[0] + s[26:42] + s[79] + s[43:79] + s[91] + s[80:83]
        elif len(s) == 90:
            return s[25] + s[3:25] + s[2] + s[26:40] + s[77] + s[41:77] + s[89] + s[78:81]
        elif len(s) == 88:
            return s[48] + s[81:67:-1] + s[82] + s[66:62:-1] + s[85] + s[61:48:-1] + s[67] + s[47:12:-1] + s[3] + s[11:3:-1] + s[2] + s[12]
        elif len(s) == 87:
            return s[62] + s[82:62:-1] + s[83] + s[61:52:-1] + s[0] + s[51:2:-1]
        elif len(s) == 86:
            return s[2:63] + s[82] + s[64:82] + s[63]
        elif len(s) == 85:
            return s[2:8] + s[0] + s[9:21] + s[65] + s[22:65] + s[84] + s[66:82] + s[21]
        elif len(s) == 84:
            return s[83:36:-1] + s[2] + s[35:26:-1] + s[3] + s[25:3:-1] + s[26]
        elif len(s) == 83:
            return s[6] + s[3:6] + s[33] + s[7:24] + s[0] + s[25:33] + s[53] + s[34:53] + s[24] + s[54:]
        elif len(s) == 82:
            return s[36] + s[79:67:-1] + s[81] + s[66:40:-1] + s[33] + s[39:36:-1] + s[40] + s[35] + s[0] + s[67] + s[32:0:-1] + s[34]
        elif len(s) == 81:
            return s[6] + s[3:6] + s[33] + s[7:24] + s[0] + s[25:33] + s[2] + s[34:53] + s[24] + s[54:81]

        else:
            raise ValueError("Unable to decrypt signature, key length %d not supported; retrying might work" % (len(s)))

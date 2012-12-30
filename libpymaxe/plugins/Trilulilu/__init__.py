# -*- coding: utf-8 -*-
import urllib, urllib2
import functions, HTMLParser
import calendar, time
h = HTMLParser.HTMLParser()

FILE_TYPE_AUDIO = 0x01
FILE_TYPE_VIDEO = 0x02

class Plugin:
    def __init__(self):
        self.pluginName = 'Trilulilu Music'
        self.version = '0.99'
        self.author = 'Ovidiu D. Niţan'
        self.homepage = 'http://www.google.ro'
        self.update = 'http://www.google.com'
        self.matchurls = ['trilulilu.ro']

    def search(self, query):
        res = []
        req = urllib2.Request('http://cauta.trilulilu.ro/muzica/' + urllib.quote(query))
        req.add_header('User-Agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4')
        getdata = urllib2.urlopen(req)
        data = getdata.read()
        results = data.split('<div class="audio_item"')
        results.pop(0)
        for x in results:
            try:
                import time
                gurl = x.split('<span class="title"><a href="')
                gurl = gurl[1].split('">')
                url = gurl[0]
                gtitle = gurl[1].split('</a></span>')
                gtitle = gtitle[0]
                title = gtitle.replace('&#039;', "'")
                title = title.replace('&amp;', '&')
                title = functions.remove_html_tags(title)
                gtime = x.split('<span class="duration">')
                gtime = gtime[1].split('</span>');
                timp = gtime[0]
                if len(timp) == 4:
                    timp = '0' + timp
                res.append([FILE_TYPE_AUDIO, title, url, timp])
            except Exception, e:
                pass
        return res

    def fileData(self, url):
        print url
        eurl = url.split('/')
        eurl.insert(3, 'embed')
        eurl = '/'.join(eurl)
        req = urllib2.Request(eurl)
        req.add_header('User-Agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4')
        getdata = urllib2.urlopen(req)
        data = getdata.read()
        if data.find('Acest utilizator si-a dezactivat contul') != -1:
            return False
        gusername = data.split('userid=')
        gusername = gusername[1].split('&')
        username = gusername[0]
        gshash = data.split('hash=')
        gshash = gshash[1].split('&')
        shash = gshash[0]
        key = ''                                # WTF?
        lenusername = len(username)
        postdata = chr(0x00) + chr(0x03) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x01) + chr(0x00) + chr(0x0f) + chr(0x66) + chr(0x69) + chr(0x6c) + chr(0x65) + chr(0x2e) + chr(0x61) + chr(0x75) + chr(0x64) + chr(0x69) + chr(0x6f) + chr(0x5f) + chr(0x69) + chr(0x6e) + chr(0x66) + chr(0x6f) + chr(0x00) + chr(0x02) + chr(0x2f) + chr(0x31) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x25) + chr(0x0a) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x03) + chr(0x02) + chr(0x00) + chr(lenusername) + username + chr(0x02) + chr(0x00) + chr(0x0e) + shash + chr(0x02) + chr(0x00) + chr(0x04) + chr(0x70) + chr(0x6c) + chr(0x61) + chr(0x79)
        req = urllib2.Request("http://www.trilulilu.ro/amf", postdata)
        req.add_header("Content-Type", "application/x-amf")
        req.add_header("Referer:", "http://static.trilulilu.ro/flash/player/audioplayer2011.swf")
        getdata = urllib2.urlopen(req)
        amfdata = getdata.read()
        gartist = amfdata.split('artist' + chr(0x02) + chr(0x00))
        gartist = gartist[1].split(chr(0x00))
        artist = gartist[0][1:]
        gtitle = amfdata.split('titlu' + chr(0x02) + chr(0x00))
        gtitle = gtitle[1].split(chr(0x00))
        title = gtitle[0][1:]
        if 'Artist neidentificat' in artist:
            titlu = title
        else:
            titlu = artist + ' - ' + title
        times = getdata.info().getheader('Date')
        timp = times.split(", ")
        timp = timp[1]
        timp = timp[:-4]
        months = {"Jan" : "01", "Feb" : "02", "Mar" : "03", "Apr" : "04", "May" : "05", "Jun" : "06", "Jul" : "07", "Aug" : "08", "Sep" : "09", "Oct" : "10", "Nov" : "11", "Dec" : "12"}
        timp = timp.split()
        unixtime = int(calendar.timegm(time.strptime(timp[0] + " " + months[timp[1]] + " " + timp[2] + " " + timp[3], "%d %m %Y %H:%M:%S")))
        exp = unixtime + 60
        gserver = amfdata.split("server\x02\x00\x02")
        gserver = gserver[1].split("\x00")
        server = gserver[0]
        gsig = amfdata.split("sig\x02\x00\x16")
        gsig = gsig[1].split("\x00")
        sig = gsig[0]
        downurl = "http://fs" + server + ".trilulilu.ro/stream.php?type=audio&source=site&hash=" + shash + "&username=" + username + "&key=" + key + '&sig=' + sig + '&exp=' + str(exp)
        print downurl
        rq = urllib2.Request(downurl)
        rq.add_header('User-Agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4')
        gtdata = urllib2.urlopen(rq)
        contentlength = gtdata.info().getheader('Content-Length')
        if contentlength == '0':
            self.fileData(url)
        durata = 'N/A'
        data = {"url" : url,
                "title" : titlu,
                "length" : durata,
                "type" : FILE_TYPE_AUDIO,
                "fsize" : contentlength,
                "downurl" : downurl
        }
        return data

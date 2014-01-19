import urllib
import urllib2

FILE_TYPE_AUDIO = 0x01
FILE_TYPE_VIDEO = 0x02


class ResultItem:
    def __init__(self, url, title, downurl, length, size):
        self.url = url
        self.title = title
        self.downurl = downurl
        self.size = size
        self.length = length
        self.hiq = False


class Plugin:
    def __init__(self):
        self.pluginName = 'MP3 Juices'
        self.version = '0.01'
        self.author = 'Ovidiu D. Nitan'
        self.homepage = 'http://www.pymaxe.com'
        self.update = 'http://www.pymaxe.com'
        self.matchurls = ['mp3juices.com']
        self.threaded_dnld = True
        self.streamurls = {}

    def search(self, query):
        self.streamurls = {}
        res = []
        req = urllib2.Request('http://mp3juices.com/search/{0}'.format(urllib.quote_plus(query.replace(' ', '-'))))
        req.add_header('User-Agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/21.0')
        getdata = urllib2.urlopen(req)
        data = getdata.read()
        results = data.split('<tr class="mpres')
        results.pop(0)
        for r in results:
            try:
                gtitle = r.split('style="display:inline!important;height:auto!important;">')
                gtitle = gtitle[1].split('</span>')
                title = gtitle[0]
                title = title.replace('&#039;', "'")
                title = title.replace('&amp;', '&')

                gurl = r.split('[url]" value="')
                gurl = gurl[1].split('" class="cache"')
                url = gurl[0]

                gsize = r.split('[filesize]" value="')
                gsize = gsize[1].split('" class="cache"')
                size = float(gsize[0]) / 100 * 1024 * 1024

                gbitrate = r.split('[bitrate]" value="')
                gbitrate = gbitrate[1].split('" class="cache"')
                bitrate = int(gbitrate[0])

                gduration = r.split('Duration: ')
                gduration = gduration[1].split(' &ndash;')
                duration = gduration[0]
                if len(duration) == 4:
                    duration = '0{0}'.format(duration)

                resultItem = ResultItem(url, title, url, duration, size)

                if bitrate >= 192:
                    resultItem.hiq = True

                self.streamurls[url] = resultItem
                res.append([FILE_TYPE_AUDIO, title, url, duration, resultItem.hiq])
            except:
                pass
        return res

    def fileData(self, url):
        item = self.streamurls[url]
        data = {"url": url,
                "title": item.title,
                "length": 'N/A',
                "type": FILE_TYPE_AUDIO,
                "fsize": item.size,
                "downurl": item.downurl,
                "hiquality": item.hiq}
        return data

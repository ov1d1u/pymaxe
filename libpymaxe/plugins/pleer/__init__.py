import urllib
import urllib2
import json
import time

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
        self.pluginName = 'Pleer'
        self.version = '0.01'
        self.author = 'Ovidiu D. Nitan'
        self.homepage = 'http://www.pymaxe.com'
        self.update = 'http://www.pymaxe.com'
        self.matchurls = ['pleer.com']
        self.threaded_dnld = True
        self.streamurls = {}

    def search(self, query):
        self.streamurls = {}
        res = []
        req = urllib2.Request('http://pleer.com/browser-extension/search?q={0}&page=1'.format(urllib.quote_plus(query)))
        req.add_header('User-Agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/21.0')
        getdata = urllib2.urlopen(req)
        data = getdata.read()
        response = json.loads(data)
        for track in response['tracks']:
            try:
                title = '{0} - {1}'.format(track['artist'], track['track'])
                url = track['file']
                size = track['size']
                bitrate = int(track['bitrate'].split()[0])
                duration = time.strftime('%M:%S', time.gmtime(track['length']))

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
                "length": item.length,
                "type": FILE_TYPE_AUDIO,
                "fsize": item.size,
                "downurl": item.downurl,
                "hiquality": item.hiq}
        return data

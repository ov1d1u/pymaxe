import urllib
import urllib2
import json
import re

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
        self.pluginName = 'Yiiyn.com'
        self.version = '0.01'
        self.author = 'Ovidiu D. Nitan'
        self.homepage = 'http://www.pymaxe.com'
        self.update = 'http://www.pymaxe.com'
        self.matchurls = ['iyyin.com']
        self.threaded_dnld = True
        self.streamurls = {}

    def search(self, query):
        # this engine is currently too slow, so we disable it
        return []
        self.streamurls = {}
        res = []
        req = urllib2.Request('http://so.ard.iyyin.com/v2/songs/search?page=1&q={0}&size=20'.format(urllib.quote_plus(query)))
        req.add_header('User-Agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/21.0')
        getdata = urllib2.urlopen(req)
        data = getdata.read()
        response = json.loads(data)
        for song in response['data']:
            try:
                title = '{0} - {1}'.format(song['singer_name'], song['song_name'])
                song_id = song['song_id']
                bitrate = 0

                # select the highest bitrate
                for url in song['url_list']:
                    if url['format'] == "mp3" and url['bitrate'] > bitrate:
                        downurl = url['url']
                        size = int(re.sub("\D", "", url['size'])) / 100 * 1024 * 1024
                        duration = url['duration']

                resultItem = ResultItem('http://iyyin.com/id/{0}'.format(song_id), title, downurl, duration, size)
                if bitrate >= 192:
                    resultItem.hiq = True

                self.streamurls['http://iyyin.com/id/{0}'.format(song_id)] = resultItem
                res.append([FILE_TYPE_AUDIO, '.......' + title, 'http://iyyin.com/id/{0}'.format(song_id), duration, resultItem.hiq])
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

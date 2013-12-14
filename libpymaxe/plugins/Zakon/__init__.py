import urllib
import urllib2
import functions

FILE_TYPE_AUDIO = 0x01
FILE_TYPE_VIDEO = 0x02


class ResultItem:
    def __init__(self, url, title, downurl, length):
        self.url = url
        self.title = title
        self.downurl = downurl
        self.length = length


class Plugin:
    def __init__(self):
        self.pluginName = 'Zakon'
        self.version = '0.01'
        self.author = 'Ovidiu D. Nitan'
        self.homepage = 'http://music.zakon.kz/'
        self.update = 'http://www.pymaxe.com'
        self.matchurls = ['music.zakon.kz']
        self.threaded_dnld = True
        self.streamurls = {}

    def search(self, query):
        self.streamurls = {}
        res = []
        req = urllib2.Request('http://music.zakon.kz/search.php?q=' + urllib.quote(query))
        req.add_header('User-Agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4')
        getdata = urllib2.urlopen(req)
        data = getdata.read()
        results = data.split('<mp3>')
        for x in results:
            try:
                details = x.split('<!>')
                file_id = details[0]
                itemid = 'http://music.zakon.kz/?q=' + urllib.quote(query) + '&id=' + file_id
                title = details[1] + ' - ' + details[2]
                title = title.replace('&mdash;', '-').replace('&#039;', "'").replace('&#39;', "'") \
                    .replace('&amp;', '&').replace('&amp', '&').replace('\n', '')
                title = functions.remove_html_tags(title)
                length = details[3]
                downurl = 'http://music.zakon.kz/mp3.php?id=' + file_id
                if len(length) == 4:
                    length = '0' + length
                self.streamurls[itemid] = ResultItem(itemid, title, downurl, length)
                # add result to list
                res.append([FILE_TYPE_AUDIO, title, itemid, length, False])
            except Exception:
                print 'GetTune: Error in parsing data'
        return res

    def fileData(self, url):
        item = self.streamurls[url]
        rq = urllib2.Request(item.downurl)
        rq.add_header('User-Agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4')
        gtdata = urllib2.urlopen(rq)
        contentlength = gtdata.info().getheader('Content-Length')
        data = {"url": url,
                "title": item.title,
                "length": item.length,
                "type": FILE_TYPE_AUDIO,
                "fsize": contentlength,
                "downurl": item.downurl,
                "hiquality": False}
        return data

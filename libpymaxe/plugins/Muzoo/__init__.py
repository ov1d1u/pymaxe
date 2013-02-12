import urllib, urllib2
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
        self.pluginName = 'Muzoo'
        self.version = '0.01'
        self.author = 'Ovidiu D. Nitan'
        self.homepage = 'http://www.muzoo.ru'
        self.update = 'http://www.pymaxe.com'
        self.matchurls = ['muzoo.ru']
        self.threaded_dnld = False  # muzoo doesn't seems to support threaded downloads

        self.email = 'c400618@rmqkr.net'
        self.password = '5a74d627d0454a09d24a092be0c9ee10'
        self.streamurls = {}

    def search(self, query):
        self.streamurls = {}
        res = []
        req = urllib2.Request('http://muzoo.ru/?query=' + urllib.quote(query))
        req.add_header('User-Agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4')
        getdata = urllib2.urlopen(req)
        data = getdata.read()
        results = data.split('<li><a class="btn play"')
        results.pop(0)
        for x in results:
            try:
                itemid = 'http://muzoo.ru/id=' + x.split('<a class="infox" href="#" rel="')[1].split('" rel="nofollow">')[0]
                title = x.split('<div class="overflow">')[1].split('<div class="player inactive">')[0]
                title = title.replace('&mdash;', '-').replace('&#039;', "'").replace('&#39;', "'") \
                            .replace('&amp;', '&').replace('&amp', '&').replace('\n', '')
                title = functions.remove_html_tags(title)
                downurl = x.split('<a class="download" rel="nofollow"  href="')[1].split('">')[0]
                length = x.split('<sup>')[1].split('</sup>')[0]
                self.streamurls[itemid] = ResultItem(itemid, title, downurl, length)
                # add result to list
                res.append([FILE_TYPE_AUDIO, title, itemid, length])
            except Exception, e:
                pass
        return res

    def fileData(self, url):
        item = self.streamurls[url]
        rq = urllib2.Request(item.downurl)
        rq.add_header('User-Agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4')
        gtdata = urllib2.urlopen(rq)
        contentlength = gtdata.info().getheader('Content-Length')
        data = {"url" : url,
                "title" : item.title,
                "length" : item.length,
                "type" : FILE_TYPE_AUDIO,
                "fsize" : contentlength,
                "downurl" : item.downurl
        }
        return data


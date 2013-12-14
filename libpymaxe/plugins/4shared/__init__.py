import urllib
import urllib2
import functions

FILE_TYPE_AUDIO = 0x01
FILE_TYPE_VIDEO = 0x02


class ResultItem:
    def __init__(self, url, title, downurl, size):
        self.url = url
        self.title = title
        self.downurl = downurl
        self.size = size


class Plugin:
    def __init__(self):
        self.pluginName = '4shared'
        self.version = '0.01'
        self.author = 'Ovidiu D. Nitan'
        self.homepage = 'http://www.pymaxe.com'
        self.update = 'http://www.pymaxe.com'
        self.matchurls = ['4shared.com']
        self.threaded_dnld = True

        self.email = 'c228801@rmqkr.net'
        self.password = '5a74d627d0454a09d24a092be0c9ee10'
        self.streamurls = {}

    def search(self, query):
        self.streamurls = {}
        res = []
        req = urllib2.Request('http://search.4shared.com/network/searchXml.jsp?login=' + self.email + '&password=!!!android2.0.5!!:md5:' + self.password + '&start=10&sortType=5&sortOrder=1&sortmode=0&searchmode=3&searchName=' + urllib.quote(query) + '.mp3&searchDescription=&searchCategory=&searchExtention=&sizeCriteria=atleast&sizevalue=&origin=android2.0.5&pf=mp4')
        req.add_header('User-Agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4')
        getdata = urllib2.urlopen(req)
        data = getdata.read()
        results = data.split('<file>')
        results.pop(0)
        for x in results:
            try:
                size = int(filter(lambda s: s.isdigit(), x.split('<size>')[1].split('</size>')[0])) * 1024
                if size < 1048576:  # 1 MB
                    continue
                title = x.split('<name>')[1].split('</name>')[0]
                title = title.replace('&#039;', "'")
                title = title.replace('&#39;', "'")
                title = title.replace('&amp;', '&')
                title = functions.remove_html_tags(title)
                url = x.split('<url>')[1].split('</url>')[0]
                if '<flash-preview-url>' in x and title.endswith('.mp3'):
                    title = title.replace('.mp3', '')
                    downurl = x.split('<flash-preview-url>')[1].split('</flash-preview-url>')[0]
                    self.streamurls[url] = ResultItem(url, title, downurl, size)
                    # add result to list
                    res.append([FILE_TYPE_AUDIO, title, url, '', False])
            except Exception:
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
                "hiquality": False}
        return data

# -*- coding: utf-8 -*-
import urllib, urllib2, os
import functions, HTMLParser
h = HTMLParser.HTMLParser()

FILE_TYPE_AUDIO = 0x01
FILE_TYPE_VIDEO = 0x02

class Plugin:
    def __init__(self):
        self.pluginName = 'Unified Plugin Interface for Pymaxe'
        self.version = '0.01'
        self.author = 'Ovidiu D. Niţan'
        self.homepage = 'http://www.google.ro'
        self.update = 'http://www.google.com'
        self.matchurls = []

        self.roxes = {}
        olddir = os.getcwd()
        os.chdir(os.getcwd() + '/libpymaxe/plugins/UPIP/')
        for x in os.listdir(os.getcwd()):
            if x.endswith('.rox'):
                print "Loading " + x
                fh = open(x, 'r')
                data = fh.read()
                self.roxes[x] = data
                fh.close()
                self.matchurls.append(self.getPluginData(x, 'info', 'matchurl'))
        os.chdir(olddir)

    def getPluginData(self, rox, section, value, lower = False):
        data = self.roxes[rox]
        if not value in data:
            return None
        gdata = functions.extract(data, section + ':', ':end')
        val = functions.extract(gdata, value, '\n')
        val = val.replace('=', '', 1)
        val = val.lstrip()
        if lower:
            val = val.lower()
        return val

    def getResultsList(self, data, item_start, item_end):
        ret = []
        results = data.split(item_start)
        results.pop(0)
        for x in results:
            try:
                ret.append(x.split(item_end)[0])
            except:
                pass
        return ret

    def search(self, query):
        res = []
        for x in self.roxes:
            searchurl = self.getPluginData(x, 'search', 'url')
            searchurl = searchurl.replace('%q', urllib.quote(query))
            method = self.getPluginData(x, 'search', 'method', True)
            if method == 'get':
                req = urllib2.Request(searchurl)
            else:
                req = urllib2.Request(searchurl)
            getdata = urllib2.urlopen(req)
            data = getdata.read()
            rstart = self.getPluginData(x, 'search', 'start')
            rend = self.getPluginData(x, 'search', 'end')
            results_data = functions.extract(data, rstart, rend)
            istart = self.getPluginData(x, 'results', 'start')
            iend = self.getPluginData(x, 'results', 'end')
            results = self.getResultsList(results_data, istart, iend)
            for y in results:
                if self.getPluginData(x, 'results', 'filetype', True) == 'audio':
                    ftype = FILE_TYPE_AUDIO
                elif self.getPluginData(x, 'results', 'filetype', True) == 'video':
                    ftype = FILE_TYPE_VIDEO
                title_start = self.getPluginData(x, 'results', 'title_start')
                title_end = self.getPluginData(x, 'results', 'title_end')
                title = functions.html_unescape(functions.remove_html_tags(functions.extract(y, title_start, title_end)))
                url_start = self.getPluginData(x, 'results', 'url_start')
                url_end = self.getPluginData(x, 'results', 'url_end')
                url = functions.extract(y, url_start, url_end)
                time_format = self.getPluginData(x, 'results', 'timeformat', True)
                if time_format != 'none':
                    time_start = self.getPluginData(x, 'results', 'time_start')
                    time_end = self.getPluginData(x, 'results', 'time_end')
                    timp = functions.extract(y, time_start, time_end)
                    import time
                    if time_format == 'seconds':
                        timp = time.strftime("%M:%S", time.gmtime(int(timp)))
                    if "%S" in time_format:
                        timp = time.strptime(timp, time_format)
                        timp = time.strftime("%M:%S", timp)
                else:
                    timp = ''
                baseurl = self.getPluginData(x, 'results', 'baseurl')
                if baseurl:
                    url = functions.html_unescape(baseurl + url)
                res.append([ftype, title, url, timp])
        return res

    def fileData(self, url):
        try:
            import time
            for x in self.roxes:
                matchurl = self.getPluginData(x, 'info', 'matchurl')
                if matchurl in url:
                    plugin = x
            req = urllib2.Request(url);
            getdata = urllib2.urlopen(req);
            data = getdata.read();
            title_start = self.getPluginData(plugin, 'details', 'title_start')
            title_end = self.getPluginData(plugin, 'details', 'title_end')
            titlu = functions.extract(data, title_start, title_end)
            time_format = self.getPluginData(plugin, 'details', 'timeformat', True)
            if time_format != 'none':
                time_start = self.getPluginData(plugin, 'details', 'time_start')
                time_end = self.getPluginData(plugin, 'details', 'time_end')
                timp = functions.extract(data, time_start, time_end)
                import time
                if time_format == 'seconds':
                    timp = time.strftime("%M:%S", time.gmtime(int(timp)))
                if "%S" in time_format:
                    timp = time.strptime(timp, time_format)
                    timp = time.strftime("%M:%S", timp)
            else:
                timp = ''
            if self.getPluginData(plugin, 'results', 'filetype', True) == 'audio':
                ftype = FILE_TYPE_AUDIO
            elif self.getPluginData(plugin, 'results', 'filetype', True) == 'video':
                ftype = FILE_TYPE_VIDEO
            downurl_start = self.getPluginData(plugin, 'details', 'downurl_start')
            downurl_end = self.getPluginData(plugin, 'details', 'downurl_end')
            downurl = functions.extract(data, downurl_start, downurl_end)
            rq = urllib2.Request(downurl)
            gtdata = urllib2.urlopen(rq)
            contentlength = gtdata.info().getheader('Content-Length')
            data = {"url" : url,
                    "title" : titlu,
                    "length" : timp,
                    "type" : ftype,
                    "fsize" : contentlength,
                    "downurl" : downurl
            }
        except Exception, e:
            print e
            return None
        return data

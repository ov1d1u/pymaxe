#-*- coding: utf-8 -*-
import thread2, datetime, time, ffmpegconverter
import urllib, urllib2, gtk, os, shutil, random

class Downloader:
    def __init__(self, pymaxe, url, saveAs, conversionString):
        self.pymaxe = pymaxe
        self.url = url
        self.saveAs = saveAs
        self.gdthread = None
        self.done = False
        self.csize = 0
        self.size = -1
        self.tmp = None
        self.stopDownload = False
        self.downfile = None
        self.converting = False
        self.cvtotal = -1
        self.cvcurrent = -1
        self.ffconvert = None
        self.tagged = False
        self.coverData = None
        self.tryHD = False
        self.dthreads = 1
        self.downloaders = []
        if conversionString == 'None':
            self.convert = False
        else:
            self.convert = conversionString


    def startDownload(self):
        self.gdthread = thread2.Thread(target=self.goDownload)
        self.gdthread.start()

    def goDownload(self, onethr=False):
        selected = None
        details = None
        for x in self.pymaxe.activePlugins:
            for y in self.pymaxe.pluginObj[x].matchurls:
                if y.lower() in self.url.lower():
                    selected = x
                    break
        retry = 0
        while not details:
            if self.tryHD:
                if selected == 'YouTube':
                    self.pymaxe.pluginObj[selected].quality = 'hd1080'
            else:
                if selected == 'YouTube':
                    self.pymaxe.pluginObj[selected].quality = 'medium'
            details = self.pymaxe.getDetails(selected, self.url)
            retry += 1
            if retry > 2:
                break
        if not details:
            self.size = None
            self.csize = 0
            self.done = None
            return
        now = datetime.datetime.now()
        tmp = str(time.mktime(now.timetuple())) + str(random.randint(1, 999))
        if os.environ.get("APPDATA"):
            self.tmp = os.environ.get('TMP') + '\\' + tmp
        else:
            self.tmp = '/tmp/' + tmp
        try:
            self.size = int(details['fsize'])
        except:
            self.goDownload(onethr) #retry
        downurl = details['downurl']
        if onethr:
            self.dthreads = 1
        chunks = self.chunk_sizes(self.size, self.dthreads)
        pos = 0
        for x in chunks:
            drange = [pos, pos+x]
            djob = DownloadJob(self.tmp, downurl, drange, self.callback)
            self.downloaders.append(djob)
            thread2.Thread(target=djob.start).start()
            pos += x
        while True:
            self.csize = 0
            workers = []
            for x in self.downloaders:
                if not x.done:
                    workers.append(x)
                if x.fail:
                    if not onethr:
                        print 'Retry with one single thread...'
                        self.goDownload(True)
                    else:
                        self.size = None
                        self.csize = 0
                        self.done = None
                    return
                self.csize += x.downloaded
            if len(workers) == 0:
                break
            time.sleep(0.1)
        thread2.Thread(target=self.callback).start()

    def callback(self):
        if self.convert:
            self.ffconvert = ffmpegconverter.FFConvert(self.tmp, self.saveAs, self.convert)
            self.ffconvert.start()
            self.converting = True
            while not self.ffconvert.done:
                self.cvtotal = self.ffconvert.time_seconds
                self.cvcurrent = self.ffconvert.current
                time.sleep(0.1)
            self.done = True
            errlevel = self.ffconvert.pipe.poll()
            if errlevel:
                self.size = None
            os.remove(self.tmp)
        else:
            shutil.copyfile(self.tmp, self.saveAs)
            os.remove(self.tmp)
            self.done = True

    def saveCover(self, data):
        self.coverData = data

    def cancel(self):
        self.stopDownload = True
        if self.gdthread:
            if self.gdthread.isAlive():
                if self.downfile:
                    if not self.downfile.closed:
                        self.downfile.close()
                self.gdthread.terminate()
        if self.converting:
            if self.ffconvert:
                self.ffconvert.cancel()
        if self.tmp:
            if os.path.exists(self.tmp):
                os.remove(self.tmp)

    def chunk_sizes(self, filesize, num_chunks):
        d, r = divmod(filesize, num_chunks)
        result = [d] * num_chunks
        result[-1] += r
        return result

class DownloadJob:
    def __init__(self, tmp, url, drange, callback):
        self.tmp = tmp
        self.url = url
        self.downfile = open(self.tmp, 'wb')
        self.downfile.seek(drange[0])
        self.stopDownload = False
        self.converting = False
        self.fail = False
        self.done = False
        self.callback = callback
        self.drange = drange
        self.downloaded = 0

    def start(self):
        req = urllib2.Request(self.url)
        req.headers['Range'] = 'bytes=%s-%s' % (self.drange[0], self.drange[1])
        self.fail = False
        self.done = False
        try:
            conn = urllib2.urlopen(req)
        except:
            self.fail = True
            return

        while not self.stopDownload:
            downData = conn.read(1024)
            if not downData:
                self.downfile.close()
                self.done = True
                break
            self.downfile.write(downData)
            self.downloaded += len(downData)

    def stop(self):
        self.stopDownload = True
        self.downfile.close()

#-*- coding: utf-8 -*-
import thread2, gobject

class Details:
    def __init__(self, pymaxe, callback):
        self.pymaxe = pymaxe
        self.callback = callback
        self.isRetrieving = False
        self.retries = 0

    def getData(self, url):
        if hasattr(self, "thread"):
            if self.thread.isAlive():
                self.thread.terminate()
        self.thread = thread2.Thread(target=self.downloadData, args=(url, ))
        self.thread.start()

    def downloadData(self, url, callback = None):
        self.isRetrieving = True
        selected = None
        for x in self.pymaxe.activePlugins:
            for y in self.pymaxe.pluginObj[x].matchurls:
                if y.lower() in url.lower():
                    selected = x
                    break
            if selected:
                break
        if selected:
            retry = 0
            details = None
            while not details:
                details = self.pymaxe.getDetails(selected, url)
                retry += 1
                if retry > 2:
                    break
            if not details:
                details = False
                gobject.idle_add(self.callback, details)
                self.isRetrieving = False
                self.retries = 0
                return details
            if 'trilulilu' in details['url']:               # Trilulilu FIX
                if '- Muzică' in details['title']:
                    find = details['title'].find(' - Muzică')
                    details['title'] = details['title'][:find]
            try:
                details['fsize'] = "%.2f" % float(float(details['fsize']) / 1024.0 / 1024.0)
            except:
                if self.retries < 3:
                    gobject.idle_add(self.getData, url)
                    self.retries += 1
                    return
                else:
                    details = False
                    gobject.idle_add(self.callback, details)
                    self.isRetrieving = False
                    self.retries = 0
                    return details
            if callback:                                    # avem nevoie de date actualizate pentru player
                gobject.idle_add(callback, details)
            else:                                           # doar preia datele şi le returnează pentru afişarea în "sidebar"
                gobject.idle_add(self.callback, details)
            self.isRetrieving = False
        else:
            details = False
            self.isRetrieving = False
        self.retries = 0
        return details

    def cancel(self):
        if self.thread.isAlive():
            self.thread.terminate()
        self.isRetrieving = False
        gobject.idle_add(self.callback, None)

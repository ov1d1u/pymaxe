#-*- coding: utf-8 -*-
import thread2
import gobject
import albumsearch


class PymaxeSearch:
    def __init__(self, pymaxe, callback):
        self.pymaxe = pymaxe
        self.callback = callback
        self.isSearching = False
        self.albumsearch = albumsearch.AlbumSearch(self.callback)

    def search(self, string, albums=True):
        self.thread = {}
        plugins = self.pymaxe.activePlugins
        for x in plugins:
            self.thread[x] = thread2.Thread(target=self.doSearch, args=(string, x))
            self.thread[x].start()
        if albums:
            self.thread['AlbumSearch'] = thread2.Thread(target=self.doSearch, args=(string, 0x03))
            self.thread['AlbumSearch'].start()

    def doSearch(self, string, plugin):
        retry = 0
        data = None
        self.isSearching = True
        if plugin == 0x03:                              # searching for albums
            data = self.albumsearch.search(string)
        else:
            while not data:
                retry += 1
                data = self.pymaxe.search(string, plugin)
                if retry > 2:
                    break
        if not data:
            return
        for x in data:
            gobject.idle_add(self.callback, data[x])
        self.thread.pop(x)
        self.call_callback()

    def stop(self):
        for x in self.thread:
            try:
                self.thread[x].terminate()
            except:
                pass
        self.thread = []
        self.isSearching = False
        gobject.idle_add(self.callback, None)

    def call_callback(self):
        if len(self.thread) == 0:
            gobject.idle_add(self.callback, None)
            self.isSearching = False

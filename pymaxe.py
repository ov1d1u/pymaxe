#!/usr/bin/python2
#-*- coding: utf-8 -*-
version = '0.63'

import sys, os
path = os.getcwd()
if os.environ.get("APPDATA"):
    if os.path.exists(os.environ.get("APPDATA") + '\\roxe\\app\\lib.zip'):
        # if we ever need to update Python's libraries
        sys.path.insert(0, os.environ.get("APPDATA") + '\\roxe\\app\\lib.zip')
    osystem = 'WIN'
    userpath = os.environ.get("APPDATA")
else:
    if sys.platform == 'darwin':
        osystem = 'OSX'
    else:
        osystem = 'UNX'
        userpath = os.environ.get("HOME")
import thread2, subprocess, webbrowser, socket, urllib, gtk, gobject, pango, configure, random, time, datetime, glib
import tools, searcher, details, coverFinder, mediaPlayer, errorManager
import settingsManager, downloader, album, albumDownloader, eyeD3, lyrics
import suggest
from tools import label_set_autowrap
from dateutil import parser as timeparser
import libpymaxe
Pymaxe = libpymaxe.Pymaxe()

if not '--debug' in sys.argv:
    ErrorManager = errorManager.ErrorManager()
    sys.excepthook = ErrorManager._error
    libpymaxe.extras.output_exc = ErrorManager.exception
if '--portable' in sys.argv:
    userpath = os.getcwd()

os.chdir(path)
AUDIO_FILE = 0x01
VIDEO_FILE = 0x02
AUDIO_FILE_ICON = gtk.gdk.pixbuf_new_from_file('audio-x-wav.png')
VIDEO_FILE_ICON = gtk.gdk.pixbuf_new_from_file('video-x-generic.png')
ALBUM_FILE_ICON = gtk.gdk.pixbuf_new_from_file('tools-rip-audio-cd.png')
HIQUALITY_ICON = gtk.gdk.pixbuf_new_from_file('hq.png')

if osystem == 'WIN':
    if not '--debug' in sys.argv:
        sys.stdout = open(userpath + '/pymaxe.log', 'w')
        sys.stderr = open(userpath + '/pymaxe.log', 'w')

gtk.gdk.threads_init()


class Main:
    def __init__(self):
        self.gui = gtk.Builder()
        self.gui.add_from_file('pymaxe.glade')
        label_set_autowrap(self.gui.get_object('label3'))
        self.gui.get_object('treeviewcolumn2').clicked()
        self.gui.get_object('treemodelfilter1').set_visible_func(self.filterTree)
        self.gui.get_object('treemodelfilter1').set_modify_func(['GdkPixbuf', str, str, str], self.modify_func)
        self.gui.get_object('statusImage').set_from_file('load.png')
        self.gui.connect_signals({
            "on_mainw_destroy_event": self.quit,
            "showAbout": self.showAbout,
            "hideAbout": self.hideAbout,
            "doSearch": self.doSearch,
            "changeFilter": self.changeFilter,
            "selectSong": self.selectSong,
            "playSong": self.playSong,
            "stopSong": self.stopSong,
            "changeVolume": self.changeVolume,
            "seekSong": self.seekSong,
            "openSourcePage": self.openSourcePage,
            "openWithPlayer": self.openWithPlayer,
            "showSettings": self.showSettings,
            "donate": self.donate,
            "fblike": self.fblike,
            "facebook": self.facebook,
            "cursorPointer": self.cursorPointer,
            "cursorNormal": self.cursorNormal,
            "hoverfb": self.hoverfb,
            "unhoverfb": self.unhoverfb,
            "downloadThis": self.downloadThis,
            "hideFileChooser": self.hideFileChooser,
            "addDownload": self.addDownload,
            "updateSaveAs": self.updateSaveAs,
            "selectDownload": self.selectDownload,
            "openDownload": self.openDownload,
            "stopRemoveDownload": self.stopRemoveDownload,
            "showDebug": self.showDebug,
            "draw_background": self.draw_background,
            "changeTab": self.changeTab,
            "switchFullscreen": self.switchFullscreen,
            "copyWebpageURL": self.copyWebpageURL})
        self.gui.get_object('eventbox4').realize()
        self.gui.get_object('eventbox4').modify_bg(gtk.STATE_NORMAL, self.gui.get_object('eventbox4').get_colormap().alloc_color("black"))
        if osystem == 'WIN':
            self.gui.get_object('eventbox4').get_window().ensure_native()
            xid = self.gui.get_object('eventbox4').get_window().handle
        elif osystem == 'OSX':
            xid = self.gui.get_object('eventbox4').window.nsview
        else:
            xid = self.gui.get_object('eventbox4').window.xid
        self.config = configure.Config()
        self.Search = searcher.PymaxeSearch(Pymaxe, self.populateResults)
        self.Details = details.Details(Pymaxe, self.showDetails)
        self.coverfinder = coverFinder.coverFinder(Pymaxe, self.setCover)
        self.mp = mediaPlayer.mediaPlayer(self.config, self.setAdjustment, xid)
        self.settingsManager = settingsManager.settingsManager(self, Pymaxe, self.config)
        self.Album = album.Album(self.showAlbumDetails)
        self.Lyrics = lyrics.Lyrics(self.setLyrics)
        self.lastIter = None
        self.fileData = None
        self.loadPlayer = None
        self.downloadUpdater = None
        self.versuri = None
        self.isFullscreen = False
        self.sugsTimeout = None
        self.lastClick = 0      # for detecting double-click in Windows
        self.downloaders = {}
        self.lyricDownloads = {}
        self.lastSaveDir = self.config.getSetting('General', 'download_into_default', self.config.guessDownloadFolder())

        self.loadPlugins()
        self.populateFileTypes()
        self.populateFileFormats()
        self.gui.get_object('scalebutton1').set_value(float(self.config.getSetting('General', 'volume', 100.0)))
        self.gui.get_object('combobox2').set_active(0)
        if not self.mp.available:
            self.gui.get_object('frame1').set_sensitive(False)
        if osystem == 'WIN':
            self.gui.get_object('frame1').set_shadow_type(gtk.SHADOW_ETCHED_IN)
            if not os.path.exists('libvlc.dll'):  # No VLC - maybe old version?
                self.gui.get_object('eventbox5').modify_bg(gtk.STATE_NORMAL, self.gui.get_object('eventbox5').get_colormap().alloc_color("yellow"))
                self.gui.get_object('eventbox5').connect('button-press-event', lambda obj, event: webbrowser.open('http://pymaxe.com/index.php/downloads') and self.quit(None))
                self.gui.get_object('updateBox').show()
        if '--portable' in sys.argv:
            self.gui.get_object('mainw').set_title(self.gui.get_object('mainw').get_title() + ' (portable)')
        self.gui.get_object('cellrenderertext1').props.ellipsize = pango.ELLIPSIZE_END
        self.gui.get_object('cellrenderertext1').props.width = self.gui.get_object('treeviewcolumn2').get_width() - 50
        self.gui.get_object('cellrenderertext5').props.ellipsize = pango.ELLIPSIZE_END
        self.gui.get_object('cellrenderertext5').props.width = self.gui.get_object('treeviewcolumn5').get_width()
        self.gui.get_object('cellrenderertext6').props.ellipsize = pango.ELLIPSIZE_END
        self.gui.get_object('cellrenderertext6').props.width = self.gui.get_object('treeviewcolumn6').get_width()
        self.gui.get_object('cellrendererprogress1').props.width = 150
        self.notifyOpened()

        self.completion = gtk.EntryCompletion()
        self.completionList = gtk.ListStore(str)
        self.gui.get_object('entry1').set_completion(self.completion)
        self.completion.set_model(self.completionList)
        self.completion.set_text_column(0)

        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()
        #self.settingsManager.displayWindow(False)

    def loadPlugins(self):
        if osystem == 'WIN':
            customdir = self.config.getSetting('General', 'pymaxe_plugins_folder', 'C:\\')
        else:
            customdir = self.config.getSetting('General', 'pymaxe_plugins_folder', '/')
        Pymaxe.setPluginsDir(customdir)
        Pymaxe.readPlugins()
        for x in Pymaxe.plugins:
            if not x in self.config.getSetting('General', 'plugins_blacklist', []):
                Pymaxe.loadPlugin(x)

    def populateFileTypes(self):
        liststore = self.gui.get_object('combostore')
        liststore.append([gtk.gdk.pixbuf_new_from_file('application-x-sharedlib.png'), 'All', str(0x00)])
        liststore.append([AUDIO_FILE_ICON, 'Music', str(0x01)])
        liststore.append([VIDEO_FILE_ICON, 'Video', str(0x02)])
        liststore.append([ALBUM_FILE_ICON, 'Albums', str(0x03)])
        self.gui.get_object('combobox1').set_active(0)

    def populateFileFormats(self):
        liststore = self.gui.get_object('fileFormats')
        liststore.append(['No conversion', 'None', ''])
        liststore.append(['MP3 File', '-b 192k -i INPUT OUTPUT', '.mp3'])
        liststore.append(['AAC File', '-i INPUT -acodec aac -strict experimental -ab 128k OUTPUT', '.aac'])
        liststore.append(['OGG File', '-i INPUT -acodec libvorbis -aq 100 OUTPUT', '.ogg'])
        liststore.append(['AVI File', '-sameq -i INPUT OUTPUT', '.avi'])
        liststore.append(['MPEG File', '-sameq -i INPUT OUTPUT', '.mpg'])
        liststore.append(['MP4 File', '-sameq -i INPUT -vcodec libxvid -strict experimental OUTPUT', '.mp4'])
        liststore.append(['PSP Video', '-i INPUT -b 300 -s 320x240 -vcodec libxvid -strict experimental -ab 32 -ar 24000 -acodec aac OUTPUT', '.mp4'])
        liststore.append(['DVD-Compatible', '-i INPUT -target pal-dvd -ps 2000000000 -aspect 16:9 OUTPUT', '.mpeg'])

    def addSugestions(self, suggestions):
        for suggestion in suggestions:
            self.completionList.append([suggestion])
        self.gui.get_object('entry1').get_completion().complete()
        gobject.source_remove(self.sugsTimeout)

    def doSearch(self, obj, event=None):
        if event:
            if event.keyval == 65364 or event.keyval == 65362:
                return

            if event.keyval != 65293:
                if len(self.gui.get_object('entry1').get_text()) > 2:
                    if self.sugsTimeout:
                        gobject.source_remove(self.sugsTimeout)
                    self.completionList.clear()
                    if self.config.getSetting('General', 'showsuggestions', True):
                        self.completionList.append([self.gui.get_object('entry1').get_text()])
                        self.sugsTimeout = gobject.timeout_add(500, suggest.suggestionsFor, self.gui.get_object('entry1').get_text(), self.addSugestions)
                return
        if self.Search.isSearching:
            if (event and event.keyval != 65293) or not event:
                self.Search.stop()
                self.setIdle(None, False)
                return
        if self.Details.isRetrieving:
            self.gui.get_object('hbox5').set_sensitive(True)
            self.gui.get_object('hbox13').set_sensitive(True)
            self.gui.get_object('hbox2').set_sensitive(True)
            self.Details.cancel()
            self.setIdle(None, False)
            return
        if self.Album.isRetrieving:
            self.Album.cancel()
            self.setIdle(None, False)
            return
        if len(Pymaxe.activePlugins) == 0:
            self.gui.get_object('statusImage').set_from_file('error.png')
            self.gui.get_object('statusLabel').set_text('No active plugins. Please activate at least one plugin from settings window')
            self.gui.get_object('image1').set_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU)
            self.setIdle(None, False)
            return
        self.gui.get_object('treeview1').grab_focus()
        self.search(self.gui.get_object('entry1').get_text())

    def search(self, value):
        if value == '':
            return
        if value.startswith('http://'):
            self.stopSong(None)
            self.gui.get_object('hbox5').set_sensitive(False)
            self.gui.get_object('hbox13').set_sensitive(False)
            self.gui.get_object('hbox2').set_sensitive(False)
            self.setIdle('Getting details...')
            thread2.Thread(target=self.loadDefUrl, args=(value, )).start()
            return
        self.gui.get_object('srchstore_data').clear()
        self.setIdle('Searching...', True)
        self.Search.search(value)

    def loadDefUrl(self, url):                                      # load a URL insered by user
        self.Details.downloadData(url, self.insertResult)

    def insertResult(self, data):
        self.gui.get_object('combobox1').set_active(0)
        model = self.gui.get_object('srchstore_data')
        model.clear()
        if data['type'] == 0x01:
            icon = AUDIO_FILE_ICON
        elif data['type'] == 0x02:
            icon = VIDEO_FILE_ICON
        elif data['type'] == 0x03:
            icon = ALBUM_FILE_ICON
        if data['hiquality']:
            hiqicon = HIQUALITY_ICON
        else:
            hiqicon = gtk.gdk.gdk_pixbuf_new()
        iter = model.append([icon, data['title'], data['url'], data['length'], data['type'], hiqicon])
        path = model.get_path(iter)
        self.gui.get_object('treeview1').set_cursor(path)
        self.selectSong(None)

    def populateResults(self, data):
        if data is None:
            self.gui.get_object('image1').set_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU)
            if not self.Details.isRetrieving and not self.Album.isRetrieving:
                self.setIdle(None, False)
            return
        liststore = self.gui.get_object('srchstore_data')
        for x in data:
            if x[0] == 0x01:
                icon = AUDIO_FILE_ICON
            elif x[0] == 0x02:
                icon = VIDEO_FILE_ICON
            elif x[0] == 0x03:
                icon = ALBUM_FILE_ICON

            if x[4]:
                hiqicon = HIQUALITY_ICON
            else:
                hiqicon = gtk.Image().get_pixbuf()

            liststore.append([icon, x[1], x[2], x[3], x[0], hiqicon])

    def selectSong(self, data, event=None):
        if event:
            if event.type == gtk.gdk.KEY_RELEASE:
                if event.keyval != 65293:
                    return
            if event.type == gtk.gdk.BUTTON_RELEASE:
                if event.button == 3:
                    treeselection = self.gui.get_object('treeview1').get_selection()
                    (model, iter) = treeselection.get_selected()
                    if iter:
                        if not 'album://' in model[iter][2]:
                            if hasattr(self, 'menuitem2_handler'):
                                self.gui.get_object('menuitem2').disconnect(self.menuitem2_handler)
                            if hasattr(self, 'menuitem3_handler'):
                                self.gui.get_object('menuitem3').disconnect(self.menuitem3_handler)
                            if hasattr(self, 'menuitem7_handler'):
                                self.gui.get_object('menuitem7').disconnect(self.menuitem7_handler)
                            titlu = model[iter][1]
                            source = model[iter][2]
                            if int(model[iter][4]) == AUDIO_FILE:
                                self.menuitem2_handler = self.gui.get_object('menuitem2').connect('activate', lambda x: self.startDownload(titlu, source, self.lastSaveDir + '/' + titlu + '.mp3'))
                            elif int(model[iter][4]) == VIDEO_FILE:
                                self.menuitem2_handler = self.gui.get_object('menuitem2').connect('activate', lambda x: self.startDownload(titlu, source, self.lastSaveDir + '/' + titlu + '.avi'))
                            else:
                                self.menuitem2_handler = self.gui.get_object('menuitem2').connect('activate', lambda x: self.startDownload(titlu, source, self.lastSaveDir + '/' + titlu))
                            self.menuitem3_handler = self.gui.get_object('menuitem3').connect('activate', self.menuDownload, source, titlu, model[iter][4])
                            self.gui.get_object('menuitem2').set_label('Download to ' + (self.lastSaveDir[:25] + (self.lastSaveDir[25:] and '..'))) # ellipsize
                            self.menuitem7_handler = self.gui.get_object('menuitem7').connect('activate', self.openAlbumSourcePage, source)
                            self.gui.get_object('popupMenu').popup(None, None, None, event.button, event.time)
                    return
        treeselection = self.gui.get_object('treeview1').get_selection()
        (model, iter) = treeselection.get_selected()
        if self.lastIter == model[iter][2]:
            return
        if self.loadPlayer:
            if self.loadPlayer.isAlive():
                self.loadPlayer.terminate()
        self.stopSong(None)
        self.gui.get_object('hbox5').set_sensitive(False)
        self.gui.get_object('hbox13').set_sensitive(False)
        self.gui.get_object('hbox2').set_sensitive(False)
        self.setIdle('Getting details...')
        self.lastIter = model[iter][2]
        if model[iter][2].startswith('album://'):
            self.Album.details(model[iter][2], self.config.getSetting('General', 'download_covers', True))
            return
        self.Details.getData(model[iter][2])

    def showDetails(self, data):
        treeselection = self.gui.get_object('treeview1').get_selection()
        (model, iter) = treeselection.get_selected()
        self.fileData = data
        if not data:
            self.setIdle(None, False)
            self.gui.get_object('statusImage').set_from_file('error.png')
            self.gui.get_object('statusLabel').set_text('Error...')
            self.gui.get_object('hbox5').set_sensitive(True)
            self.gui.get_object('hbox13').set_sensitive(True)
            self.gui.get_object('hbox2').set_sensitive(True)
            return
        if not data['url'] in model[iter][2]:
            print 'URL Mismatch: {0}'.format(data['url'])
            return
        if not 'WMPlayer' in str(self.mp.backend):
            if data['type'] == VIDEO_FILE:
                self.gui.get_object('vbox15').show()
            else:
                self.gui.get_object('vbox15').hide()
        self.gui.get_object('image3').set_from_file('cd_case.png')
        self.gui.get_object('hbox5').set_sensitive(True)
        self.gui.get_object('hbox13').set_sensitive(True)
        self.gui.get_object('hbox2').set_sensitive(True)
        self.gui.get_object('hbox5').hide()
        self.gui.get_object('hbox13').hide()
        self.coverfinder.abort()
        if self.config.getSetting('General', 'download_covers', True):
            self.coverfinder.searchCover(data['title'])
            self.coverfinderJob = data['url']
        if ' - ' in data['title']:
            (artist, title) = data['title'].rsplit(' - ', 1)
            self.gui.get_object('titleLabel').set_text(title.lstrip())
            self.gui.get_object('artistLabel').set_text(artist.lstrip())
        else:
            self.gui.get_object('titleLabel').set_text(data['title'])
            self.gui.get_object('artistLabel').set_text('')
        if self.fileData['type'] == AUDIO_FILE:
            self.gui.get_object('labelType').set_text('Audio')
        elif self.fileData['type'] == VIDEO_FILE:
            self.gui.get_object('labelType').set_text('Video')
        self.gui.get_object('labelSize').set_text(str(data['fsize']) + ' MB')
        self.gui.get_object('labelSource').set_text(data['url'])
        if not self.mp.available:
            self.gui.get_object('hbox3').set_sensitive(False)
        iter = self.gui.get_object('srchstore_data').get_iter_root()
        if not iter:
            if x[0] == 0x01:
                icon = AUDIO_FILE_ICON
            elif x[0] == 0x02:
                icon = VIDEO_FILE_ICON
            self.gui.get_object('srchstore_data').append([icon, data['title'], data['url'], '', x[0]])
        self.gui.get_object('hbox13').hide()
        self.gui.get_object('hbox2').show()
        if not self.Search.isSearching:
            self.setIdle(None, False)

    def showAlbumDetails(self, data):
        treeselection = self.gui.get_object('treeview1').get_selection()
        (model, iter) = treeselection.get_selected()
        if not data:
            self.setIdle(None, False)
            self.gui.get_object('statusImage').set_from_file('error.png')
            self.gui.get_object('statusLabel').set_text('Error...')
            self.gui.get_object('hbox5').set_sensitive(True)
            self.gui.get_object('hbox13').set_sensitive(True)
            self.gui.get_object('hbox2').set_sensitive(True)
            return
        if model[iter][2] != 'album://' + data['mbid']:
            return
        self.gui.get_object('image12').set_from_file('cd_case.png')
        self.gui.get_object('hbox5').set_sensitive(True)
        self.gui.get_object('hbox13').set_sensitive(True)
        self.gui.get_object('hbox2').set_sensitive(True)
        self.gui.get_object('hbox5').hide()
        self.gui.get_object('hbox2').hide()
        if hasattr(self, "openalbum_conn"):
            self.gui.get_object('button10').disconnect(self.openalbum_conn)
        if hasattr(self, "downalbum_conn"):
            self.gui.get_object('button9').disconnect(self.downalbum_conn)
        self.openalbum_conn = self.gui.get_object('button10').connect("clicked", self.openAlbumSourcePage, data['url'])
        self.downalbum_conn = self.gui.get_object('button9').connect("clicked", self.downloadAlbum, data)
        self.coverfinder.abort()
        if self.config.getSetting('General', 'download_covers', True):
            self.coverfinder.searchCover(data['name'], data['mbid'])
        self.gui.get_object('albumLabel').set_text(data['name'])
        self.gui.get_object('artistAlbumLabel').set_text(data['artist'])
        self.gui.get_object('labelTracksNo').set_text(data['tracks'])
        self.gui.get_object('labelRelease').set_text(data['release'])
        self.gui.get_object('hbox2').hide()
        self.gui.get_object('hbox13').show()
        self.setIdle(None, False)

    def setCover(self, data):
        if not data:
            return
        if hasattr(self, "coverFindJob"):
            treeselection = self.gui.get_object('treeview1').get_selection()
            (model, iter) = treeselection.get_selected()
            url = model[iter][2]
            if self.coverfinderJob != url:
                return
        pixbuf = tools.Image_to_GdkPixbuf(data)
        if self.gui.get_object('hbox2').get_visible():
            self.gui.get_object('image3').set_from_pixbuf(pixbuf)
        if self.gui.get_object('hbox13').get_visible():
            self.gui.get_object('image12').set_from_pixbuf(pixbuf)

    def playSong(self, obj, event=None):
        if not self.mp.available:
            return
        if self.loadPlayer:
            if self.loadPlayer.isAlive():
                return
            if self.mp.isPlaying():
                self.mp.pause()
                self.gui.get_object('image5').set_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_MENU)
            else:
                self.mp.play()
                self.gui.get_object('image5').set_from_stock(gtk.STOCK_MEDIA_PAUSE, gtk.ICON_SIZE_MENU)
                self.mp.volume(self.gui.get_object('scalebutton1').get_value())
                gobject.timeout_add(250, self.mp.updateAdjustment, True)
            return
        self.versuri = None
        treeselection = self.gui.get_object('treeview1').get_selection()
        (model, iter) = treeselection.get_selected()
        url = model[iter][2]
        self.loadPlayer = thread2.Thread(target=self.preparePlayer, args=(url,))
        self.loadPlayer.start()
        self.gui.get_object('labelPlayerWait').set_markup('<b>Loading, please wait...</b>')
        self.gui.get_object('labelPlayerWait').show()
        if self.config.getSetting('General', 'download_lyrics', True):
            title = self.gui.get_object('titleLabel').get_text()
            artist = self.gui.get_object('artistLabel').get_text()
            self.Lyrics.search(artist, title)

    def preparePlayer(self, url):
        self.Details.downloadData(url, self.startPlay)

    def startPlay(self, data):
        if not data:
            self.gui.get_object('hbox3').set_sensitive(False)
            self.gui.get_object('statusImage').set_from_file('error.png')
            self.gui.get_object('statusLabel').set_text('Error...')
            self.gui.get_object('image1').set_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU)
            return
        self.gui.get_object('labelPlayerWait').set_markup('<b>Buffering...</b>')
        self.gui.get_object('image5').set_from_stock(gtk.STOCK_MEDIA_PAUSE, gtk.ICON_SIZE_MENU)
        self.mp.volume(self.gui.get_object('scalebutton1').get_value())
        self.mp.load(data['downurl'])
        gobject.timeout_add(250, self.mp.updateAdjustment, True)
        self.mp.play()

    def stopSong(self, obj, event=None):
        if not self.mp.available:
            return
        self.loadPlayer = None
        self.mp.unload()
        gobject.timeout_add(250, self.mp.updateAdjustment, False)
        self.gui.get_object('labelET').set_text('00:00')
        self.gui.get_object('labelTT').set_text('00:00')
        self.gui.get_object('adjustment1').set_value(0.0)
        self.gui.get_object('image5').set_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_MENU)

    def seekSong(self, obj, event=None, value=None):
        if not self.mp.available:
            return
        if event:
            if event.type == gtk.gdk.BUTTON_PRESS:
                self.mp.isSeeking = True
        value = obj.get_value()
        if value > 100:
            value = 100
        if event:
            if event.type == gtk.gdk.BUTTON_RELEASE:
                self.mp.isSeeking = False
                self.mp.seek(value)

    def setAdjustment(self, pos, ret):
        self.gui.get_object('labelPlayerWait').hide()
        self.adjustment = self.gui.get_object('adjustment1')
        if pos[0] > 99.0:
            if pos[1] != ' day, 23:59:59':
                self.stopSong(None)
        if not self.mp.isPlaying():
            return False
        if not self.mp.isSeeking:
            self.adjustment.set_value(pos[0])
        self.gui.get_object('labelET').set_text(pos[1])
        self.gui.get_object('labelTT').set_text(pos[2])
        self.showLyrics(pos[1])

    def setLyrics(self, data):
        print 'Lyrics found'
        self.versuri = data

    def saveLyrics(self, data, location):
        try:
            fname = os.path.splitext(location)
            fname = fname[0] + '.lrc'
            fh = open(fname, 'w')
            fh.write(data)
            fh.close()
        except:
            print 'Failed to save lyrics'

    def showLyrics(self, position):
        if self.versuri:
            timp = self.mp.getPos_precise()
            timp = timeparser.parse(timp)
            lastvers = ''
            for vers in sorted(self.versuri['lyrics'].iterkeys()):
                if vers < timp:
                    lastvers = self.versuri['lyrics'][vers]
            self.gui.get_object('labelPlayerWait').set_markup('<i>' + glib.markup_escape_text(lastvers) + '</i>')
            self.gui.get_object('labelPlayerWait').show()

    def changeVolume(self, obj, value):
        if not self.mp.available:
            return
        self.mp.volume(value)
        self.config.setSetting('General', 'volume', value)

    def openSourcePage(self, obj, event=None):
        webpage = self.gui.get_object('labelSource').get_text()
        webbrowser.open(webpage)

    def openAlbumSourcePage(self, obj, url):
        webbrowser.open(url)

    def openWithPlayer(self, obj, event=None):
        url = self.fileData['downurl']
        ftype = self.fileData['type']
        try:
            if ftype==AUDIO_FILE:
                if osystem == 'WIN':
                    command = [self.config.getSetting('General', 'audio_player', tools.getOpenWith('.mp3')[0])]
                else:
                    command = [self.config.getSetting('General', 'audio_player', tools.getOpenWith('.mp3')[0])]
            elif ftype==VIDEO_FILE:
                if osystem == 'WIN':
                    command = [self.config.getSetting('General', 'video_player', tools.getOpenWith('.mp4')[0])]
                else:
                    command = [self.config.getSetting('General', 'video_player', tools.getOpenWith('.mp4')[0])]
            else:
                command = None
            if command:
                command.append(url)
                subprocess.Popen(command)
        except Exception, e:
            print e
            self.gui.get_object('statusImage').set_from_file('error.png')
            self.gui.get_object('statusLabel').set_text('Cannot open: no application associated with this file type.')
            self.gui.get_object('image1').set_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU)

    def showSettings(self, obj, event=None):
        self.settingsManager.displayWindow()

    def changeFilter(self, obj, event=None):
        self.gui.get_object('treemodelfilter1').refilter()

    def filterTree(self, model, iter):
        combo = self.gui.get_object('combobox1')
        cmodel = combo.get_model()
        index = combo.get_active()
        active = cmodel[index][2]
        if active == str(0x00):
            return True
        if str(model[iter][4]) == str(active):
            return True

    def modify_func(self, model, iter, col, attrs):
        child_model_iter = model.convert_iter_to_child_iter(iter)
        child_model = model.get_model()
        row_obj = child_model.get_value(child_model_iter, 0)

        path = child_model.get_path(child_model_iter)
        path_str=  "-".join(str(i) for i in path)

        if col == 1: #first column
            arr = self.row[path_str][col]
        elif col == 2:
            arr = self.row[path_str][col]
        elif col == 3:
            arr = self.row[path_str][col]
        else:
            arr = "faszomat"
        return arr

    def setIdle(self, text='Idle...', activate=True):
        if activate:
            self.gui.get_object('statusImage').set_from_animation(gtk.gdk.PixbufAnimation('load.gif'))
            self.gui.get_object('statusLabel').set_text(text)
            self.gui.get_object('image1').set_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_MENU)
        else:
            self.gui.get_object('image1').set_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU)
            self.gui.get_object('statusImage').set_from_file('load.png')
            self.gui.get_object('statusLabel').set_text('Idle...')

    def downloadAlbum(self, obj, data):
        dfolder = self.config.getSetting('General', 'download_into_default', self.config.guessDownloadFolder())
        downloader = albumDownloader.AlbumDownloader(Pymaxe, self.Album, data, self.startDownload)
        downloader.gui.get_object('label4').set_text(dfolder)
        if not self.config.getSetting('General', 'download_covers', True):
            downloader.gui.get_object('checkbutton1').set_active(False)
        downloader.show()

    def downloadThis(self, obj, event=None):
        artist = self.gui.get_object('artistLabel').get_text()
        title = self.gui.get_object('titleLabel').get_text()
        if (artist == ''):
            titlu = title
        else:
            titlu = artist + ' - ' + title
        if self.fileData['type'] == AUDIO_FILE:
            ext = '.mp3'
        elif self.fileData['type'] == VIDEO_FILE:
            ext = '.avi'
        fchooser = self.gui.get_object("filechooserdialog1")
        fchooser.set_local_only(True)
        if osystem == 'WIN':
            fchooser.set_current_name(tools.strip_win32_incompat(titlu + ext))
        else:
            fchooser.set_current_name(titlu + ext)
        fchooser.set_current_folder(self.lastSaveDir)
        self.gui.get_object('combobox2').emit("changed")
        fchooser.show()

    def addDownload(self, obj):
        self.lastSaveDir = self.gui.get_object("filechooserdialog1").get_current_folder()
        filename = self.gui.get_object("filechooserdialog1").get_filename()
        if os.path.exists(filename):
            ovrw = tools.msg_warning('This file already exists. It\'s ok to overwrite?')
            if ovrw == gtk.RESPONSE_CANCEL:
                return
        self.hideFileChooser()
        artist = self.gui.get_object('artistLabel').get_text()
        title = self.gui.get_object('titleLabel').get_text()
        source = self.gui.get_object('labelSource').get_text()
        if (artist == ''):
            titlu = title
        else:
            titlu = artist + ' - ' + title
        if osystem == 'WIN':
            path, filename = os.path.split(filename)
            saveAs = path + '/' + tools.strip_win32_incompat(filename)
        else:
            saveAs = filename
        self.startDownload(titlu, source, saveAs)

    def startDownload(self, titlu, source, saveAs):
        jobID = source + '___' + str(random.randint(1, 999))
        model = self.gui.get_object('combobox2').get_model()
        iter = self.gui.get_object('combobox2').get_active_iter()
        conversionString = model[iter][1]
        self.downloaders[jobID] = downloader.Downloader(Pymaxe, source, saveAs, conversionString)
        if self.config.getSetting('General', 'threadeddownload', True):
            self.downloaders[jobID].dthreads = int(float(self.config.getSetting('General', 'downloadthreads', 5)))
        if self.config.getSetting('General', 'downloadhd', True):
            self.downloaders[jobID].tryHD = True
        else:
            self.downloaders[jobID].tryHD = False
        img = gtk.gdk.pixbuf_new_from_file('wait.png')
        coverfind = coverFinder.coverFinder(Pymaxe, self.downloaders[jobID].saveCover)
        coverfind.searchCover(titlu)
        self.gui.get_object('downloadStore').append([img, titlu, saveAs, 0, jobID])
        self.downloaders[jobID].startDownload()
        self.lyricDownloads[jobID] = lyrics.Lyrics(self.saveLyrics, saveAs)
        if self.config.getSetting('General', 'download_lyrics', True):
            if ' - ' in titlu:
                (artist, title) = titlu.rsplit(' - ', 1)
            else:
                title = titlu
                artist = ''
            self.lyricDownloads[jobID].search(artist, title)
        else:
            self.lyricDownloads[jobID].done = True
        if not self.downloadUpdater:
            self.downloadUpdater = gobject.timeout_add(500, self.updateDownloads)

    def hideFileChooser(self, obj=None, event=None):
        self.gui.get_object("filechooserdialog1").hide()
        return True

    def updateSaveAs(self, obj, event=None):
        fchooser = self.gui.get_object("filechooserdialog1")
        fname = fchooser.get_filename()
        if not fname:
            return
        fname = os.path.basename(fname)
        fname = os.path.splitext(fname)
        actual = fname[0]
        model = obj.get_model()
        iter = obj.get_active_iter()
        ext = model[iter][2]
        if ext == '':
            if self.fileData['type'] == AUDIO_FILE:
                ext = '.mp3'
            elif self.fileData['type'] == VIDEO_FILE:
                ext = '.avi'
        fchooser.set_current_name(actual + ext)

    def updateDownloads(self):
        actives = 0
        downloadStore = self.gui.get_object('downloadStore')
        iter = downloadStore.get_iter_root()
        if not iter:
            return True
        while iter:
            jobID = downloadStore[iter][4]
            downloader = self.downloaders[jobID]
            if not downloader.stopDownload:
                if not downloader.done:
                    if downloader.size:
                        actives += 1
                self.tsize = downloader.size
                if downloader.convert:
                    if downloader.converting:
                        if downloader.cvcurrent:
                            if downloader.cvtotal:
                                procent = ((float(downloader.cvcurrent/2) / float(downloader.cvtotal)) * 100) + 50
                            else:
                                downloadStore = self.gui.get_object('downloadStore')
                                procent = downloadStore.get_value(iter, 3)
                            if downloader.done:
                                procent = 100
                            self.downloadProgress(procent, downloader.done, iter)
                    else:
                        if downloader.csize:
                            procent = (float(downloader.csize) / float(downloader.size*2)) * 100
                        else:
                            procent = 0
                        if downloader.done:
                            procent = 100
                        self.downloadProgress(procent, downloader.done, iter)
                else:
                    if downloader.csize:
                        procent = (float(downloader.csize) / float(downloader.size)) * 100
                    else:
                        procent = 0
                    if downloader.done:
                        procent = 100
                    self.downloadProgress(procent, downloader.done, iter)
            iter = downloadStore.iter_next(iter)
        if actives > 0:
            self.gui.get_object('label2').set_text('Downloads (' + str(actives) + ')')
        else:
            self.gui.get_object('label2').set_text('Downloads')
        self.selectDownload()
        return True

    def downloadProgress(self, procent, done, iter):
        downloadStore = self.gui.get_object('downloadStore')
        if not self.tsize:
            downloadStore.set_value(iter, 0, gtk.gdk.pixbuf_new_from_file('error.png'))
            downloadStore.set_value(iter, 3, 0)
            return
        if done:
            jobID = downloadStore[iter][4]
            if self.lyricDownloads[jobID].done:
                downloadStore.set_value(iter, 0, gtk.gdk.pixbuf_new_from_file('ok.png'))
                downloadStore.set_value(iter, 3, 100)
            else:
                downloadStore.set_value(iter, 3, 99)
            if not self.downloaders[jobID].tagged:
                self.setTags(downloadStore[iter][1], downloadStore[iter][2], self.downloaders[jobID])
                if self.config.getSetting('General', 'opendownloaded', False):
                    self.openDownload(None, self.downloaders[jobID].saveAs)
                self.downloaders[jobID].tagged = True
        else:
            downloadStore.set_value(iter, 0, gtk.gdk.pixbuf_new_from_file('download2.png'))
            downloadStore.set_value(iter, 3, procent)

    def selectDownload(self, obj=None, event=None):
        treeselection = self.gui.get_object('treeview2').get_selection()
        (model, iter) = treeselection.get_selected()
        if not iter:
            self.gui.get_object('toolbutton2').set_sensitive(False)
            self.gui.get_object('toolbutton1').set_sensitive(False)
            return
        jobID = model[iter][4]
        downloader = self.downloaders[jobID]
        if downloader.done == True:
            if os.path.exists(downloader.saveAs):
                self.gui.get_object('toolbutton1').set_sensitive(True)
            else:
                self.gui.get_object('toolbutton1').set_sensitive(False)
            self.gui.get_object('toolbutton2').set_sensitive(True)
            self.gui.get_object('image11').set_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_MENU)
            self.gui.get_object('label7').set_text('Remove from list')
        elif downloader.stopDownload:
            self.gui.get_object('toolbutton1').set_sensitive(False)
            self.gui.get_object('toolbutton2').set_sensitive(True)
            self.gui.get_object('image11').set_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_MENU)
            self.gui.get_object('label7').set_text('Remove from list')
        elif not downloader.size:
            self.gui.get_object('toolbutton1').set_sensitive(False)
            self.gui.get_object('toolbutton2').set_sensitive(True)
            self.gui.get_object('image11').set_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_MENU)
            self.gui.get_object('label7').set_text('Remove from list')
        elif downloader.done == False:
            self.gui.get_object('toolbutton1').set_sensitive(False)
            self.gui.get_object('toolbutton2').set_sensitive(True)
            self.gui.get_object('image11').set_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_MENU)
            self.gui.get_object('label7').set_text('Cancel download')

    def openDownload(self, obj, ofile=None):
        if not ofile:
            treeselection = self.gui.get_object('treeview2').get_selection()
            (model, iter) = treeselection.get_selected()
            ofile = model[iter][2]
        gext = os.path.splitext(ofile)
        ext = gext[1]
        command = None
        try:
            if ext in ['.mp3', '.aac', '.ogg']:
                command = [self.config.getSetting('General', 'audio_player', tools.getOpenWith(ext)[0])]
            elif ext in ['.mp4', '.mpg', '.mpeg', '.avi', '.ogv', '.flv']:
                command = [self.config.getSetting('General', 'video_player', tools.getOpenWith(ext)[0])]
            if command[0]:
                command.append(ofile)
                subprocess.Popen(command)
            else:
                command = tools.getOpenWith(ext)
                command.append(ofile)
                subprocess.Popen(command)
        except Exception:
            self.gui.get_object('statusImage').set_from_file('error.png')
            self.gui.get_object('statusLabel').set_text('Cannot open: no application associated with this file type.')
            self.gui.get_object('image1').set_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU)

    def stopRemoveDownload(self, obj, event=None):
        treeselection = self.gui.get_object('treeview2').get_selection()
        (model, iter) = treeselection.get_selected()
        jobID = model[iter][4]
        downloader = self.downloaders[jobID]
        if not downloader.done:
            if downloader.stopDownload:
                model.remove(iter)
                self.downloaders.pop(jobID)
            elif not downloader.size:
                model.remove(iter)
                self.downloaders.pop(jobID)
            else:
                downloader.cancel()
                self.gui.get_object('toolbutton2').set_sensitive(True)
                self.gui.get_object('image11').set_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_MENU)
                self.gui.get_object('label7').set_text('Remove from list')
                model.set_value(iter, 0, gtk.gdk.pixbuf_new_from_file('error.png'))
        else:
            model.remove(iter)
            self.downloaders.pop(jobID)
        treeselection = self.gui.get_object('treeview2').get_selection()
        (model, iter) = treeselection.get_selected()
        if not iter:
            self.gui.get_object('toolbutton1').set_sensitive(False)
            self.gui.get_object('toolbutton2').set_sensitive(False)

    def setTags(self, name, saveAs, downloader):
        if not saveAs.endswith('.mp3'):
            return
        if ' - ' in name:
            (artist, title) = name.rsplit(' - ', 1)
        else:
            title = name
            artist = ''
        tag = eyeD3.Tag()
        tag.link(saveAs)
        tag.header.setVersion(eyeD3.ID3_V2_4)
        tag.setArtist(artist.lstrip())
        tag.setTitle(title.lstrip())
        tag.addComment('Downloaded with Pymaxe')
        if self.config.getSetting('General', 'download_covers', True):
            if osystem == 'WIN':
                now = datetime.datetime.now()
                tmp = os.environ.get('TMP') + '\\' + str(time.mktime(now.timetuple())) + str(random.randint(1, 999)) + '.png'
            else:
                now = datetime.datetime.now()
                tmp = '/tmp/' + str(time.mktime(now.timetuple())) + str(random.randint(1, 999)) + '.png'
            coverData = downloader.coverData
            if coverData:
                coverData.save(tmp)
                if open('cd_case.png', 'r').read() != open(tmp, 'r').read():
                    pixbuf = tools.Image_to_GdkPixbuf(coverData)
                    pixbuf.save(tmp, "png")
                    tag.addImage(0x03, tmp)
        tag.setTextEncoding("\x03")
        tag.update()

    def changeTab(self, obj, pointer, tab):
        if self.gui.get_object('hbox2').get_visible():
            self.lastVisible = self.gui.get_object('hbox2')
        elif self.gui.get_object('hbox13').get_visible():
            self.lastVisible = self.gui.get_object('hbox13')
        elif self.gui.get_object('hbox5').get_visible():
            self.lastVisible = self.gui.get_object('hbox5')
        if tab == 1:
            self.gui.get_object('image3').hide()
            self.gui.get_object('vbox3').hide()
            self.gui.get_object('vbox6').hide()
            self.gui.get_object('button12').show()
        else:
            self.gui.get_object('image3').show()
            self.gui.get_object('vbox3').show()
            self.gui.get_object('vbox6').show()
            self.gui.get_object('button12').hide()
            self.lastVisible.show()

    def switchFullscreen(self, obj, event=None):
        if event:
            if event.type == gtk.gdk.KEY_PRESS:
                if event.keyval == 65307:
                    tip = gtk.gdk._2BUTTON_PRESS
            else:
                tip = event.type
        else:
            tip = gtk.gdk._2BUTTON_PRESS
        full = self.gui.get_object('fullscreenWindow')
        if osystem == 'WIN':
            if tip == gtk.gdk.BUTTON_PRESS:
                if (time.time() - self.lastClick) < 0.4:
                    tip = gtk.gdk._2BUTTON_PRESS
                    self.lastClick = 0
                else:
                    self.lastClick = time.time()
        if tip == gtk.gdk._2BUTTON_PRESS:
            if self.isFullscreen:                                   # UNFULLSCREEN
                self.gui.get_object('eventbox4').reparent(self.evboxParent)
                full.hide()
                self.isFullscreen = False
            else:                                                   # FULLSCREEN
                self.evboxParent = self.gui.get_object('eventbox4').get_parent()
                full.show()
                full.fullscreen()
                self.gui.get_object('eventbox4').reparent(full)
                self.isFullscreen = True
        return True

    def menuDownload(self, obj, source, titlu, tip):
        if int(tip) == AUDIO_FILE:
            ext = '.mp3'
        elif int(tip) == VIDEO_FILE:
            ext = '.avi'
        fchooser = gtk.FileChooserDialog(title='Save as...',
                                         action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                         buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        fchooser.set_local_only(True)
        if osystem == 'WIN':
            fchooser.set_current_name(tools.strip_win32_incompat(titlu + ext))
        else:
            fchooser.set_current_name(titlu + ext)
        fchooser.set_current_folder(self.lastSaveDir)
        self.gui.get_object('combobox2').emit("changed")
        response = fchooser.run()
        if response == gtk.RESPONSE_OK:
            fname = fchooser.get_filename()
            self.lastSaveDir = fchooser.get_current_folder()
            self.startDownload(titlu, source, fname)
        fchooser.destroy()

    def copyWebpageURL(self, obj):
        treeselection = self.gui.get_object('treeview1').get_selection()
        (model, iter) = treeselection.get_selected()
        url = model[iter][2]
        clipboard = gtk.Clipboard()
        clipboard.set_text(url)

    def fblike(self, obj, event=None):
        url = self.fileData['url']
        webbrowser.open_new('https://www.facebook.com/sharer/sharer.php?u=' + urllib.quote(url))

    def donate(self, obj, event=None):
        webbrowser.open('https://www.paypal.com/ro/cgi-bin/webscr?cmd=_flow&SESSION=7WNGJgHPkuV5-u5RQKh9orLUotbw15zWpKuAQXx7ueMgI4MXBA1z7cdSndC&dispatch=5885d80a13c0db1f8e263663d3faee8db2b24f7b84f1819390b7e2d9283d70f1')

    def facebook(self, obj, event=None):
        webbrowser.open('https://www.facebook.com/Pymaxe')

    def cursorPointer(self, obj, event=None):
        obj.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND2))

    def cursorNormal(self, obj, event=None):
        obj.window.set_cursor(None)

    def hoverfb(self, obj, event=None):
        self.gui.get_object('image9').set_from_file('like_h.png')

    def unhoverfb(self, obj, event=None):
        self.gui.get_object('image9').set_from_file('like.png')

    def showAbout(self, obj):
        self.gui.get_object('label15').set_text('Pymaxe ' + str(version))
        self.gui.get_object('labelPymaxe').set_text('Using libPymaxe v.' + str(Pymaxe.version))
        self.gui.get_object('labelPython').set_text('Running using Python ' + sys.version)
        self.gui.get_object('aboutdialog').show()

    def hideAbout(self, obj, event=None):
        self.gui.get_object('aboutdialog').hide()
        return True

    def draw_background(self, obj, event):
        return False                                                    # hide mini-logo
        size = self.gui.get_object('mainw').get_size()
        pixbuf = gtk.gdk.pixbuf_new_from_file('pymaxe.png')
        obj.window.draw_pixbuf(obj.style.bg_gc[gtk.STATE_NORMAL], pixbuf, 0, 0, size[0] - 100, 17)

    def showDebug(self, obj, event=None):
        ErrorManager.show()

    def notifyOpened(self):
        if osystem == 'WIN':
            self.notificator = os.environ.get('TMP') + '\\' + '.pymaxe'
        else:
            self.notificator = '/tmp/' + '.pymaxe'
        open(self.notificator, 'w')

    def _error(self, tip, msg, tb):
        self.gui.get_object('statusImage').set_from_file('error.png')
        self.gui.get_object('statusLabel').set_text('Error...')
        self.gui.get_object('image1').set_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU)
        return False

    def quit(self, obj, event=None):
        self.stopSong(None)
        for x in self.downloaders:
            self.downloaders[x].cancel()
        if os.path.exists(self.notificator):
            os.remove(self.notificator)
        gtk.main_quit()
        os._exit(0)

if __name__ == "__main__":
    if '--debug' in sys.argv:
        Main()
    else:
        try:
            Main()
        except:
            ErrorManager.exception()

import sys, os, gtk, gobject, tools


class settingsManager:
    def __init__(self, roxe, pymaxe, configure):
        self.roxe = roxe
        self.pymaxe = pymaxe
        self.config = configure
        self.gui = gtk.Builder()
        self.gui.add_from_file('settings.glade')
        self.gui.connect_signals({
            "hideSettings": self.hideSettings,
            "togglePlugin": self.togglePlugin,
            "showHidePreview": self.showHidePreview,
            "showThreadsOptions": self.showThreadsOptions})
        tools.label_set_autowrap(self.gui.get_object('label1'))

    def displayWindow(self, show=True):
        self.gui.get_object('checkbutton1').set_active(self.config.getSetting('General', 'download_covers', True))
        self.gui.get_object('checkbutton7').set_active(self.config.getSetting('General', 'download_lyrics', True))
        self.gui.get_object('checkbutton2').set_active(self.config.getSetting('General', 'autoupdate', True))
        self.gui.get_object('checkbutton3').set_active(self.config.getSetting('General', 'opendownloaded', False))
        self.gui.get_object('checkbutton4').set_active(self.config.getSetting('General', 'downloadhd', True))
        self.gui.get_object('checkbutton6').set_active(self.config.getSetting('General', 'threadeddownload', True))
        self.gui.get_object('checkbutton8').set_active(self.config.getSetting('General', 'showsuggestions', True))
        self.gui.get_object('filechooserbutton1').set_filename(self.config.getSetting('General', 'download_into_default', self.config.guessDownloadFolder()))
        if os.environ.get("APPDATA"):
            self.gui.get_object('filechooserbutton2').set_filename(self.config.getSetting('General', 'pymaxe_plugins_folder', 'C:\\'))
        else:
            self.gui.get_object('filechooserbutton2').set_filename(self.config.getSetting('General', 'pymaxe_plugins_folder', '/'))
        mp3open = tools.getOpenWith('.mp3')[0]
        mp4open = tools.getOpenWith('.mp4')[0]
        if self.config.getSetting('General', 'audio_player', mp3open):
            mp3open = self.config.getSetting('General', 'audio_player', mp3open)
        if self.config.getSetting('General', 'video_player', mp4open):
            mp4open = self.config.getSetting('General', 'video_player', mp4open)

        if os.environ.get("APPDATA"):
            if mp3open:
                self.gui.get_object('filechooserbutton3').set_filename(mp3open)
            if mp4open:
                self.gui.get_object('filechooserbutton4').set_filename(mp4open)
        else:
            if mp3open:
                if not '/usr/bin' in mp3open and not sys.platform == 'darwin':
                    mp3open = '/usr/bin/' + mp3open
                self.gui.get_object('filechooserbutton3').set_filename(mp3open)
            if mp4open:
                if not '/usr/bin' in mp4open and not sys.platform == 'darwin':
                    mp4open = '/usr/bin/' + mp4open
                self.gui.get_object('filechooserbutton4').set_filename(mp4open)
        self.gui.get_object('checkbutton5').set_active(self.config.getSetting('General', 'preview_video', True))
        self.gui.get_object('spinbutton1').set_value(int(float(self.config.getSetting('General', 'downloadthreads', 5))))
        plugins = self.pymaxe.plugins
        blacklist = self.config.getSetting('General', 'plugins_blacklist', '').split(',')
        if blacklist[0] == '':
            blacklist.pop(0)
        self.blacklist = []
        self.gui.get_object('liststore2').clear()
        for x in plugins:
            if x in blacklist:
                self.gui.get_object('liststore2').append([False, x])
                self.blacklist.append(x)
            else:
                self.gui.get_object('liststore2').append([True, x])
        self.gui.get_object('liststore1').clear()
        backends = ['autodetect', 'vlc', 'gstreamer', 'Windows Media Player']
        for x in backends:
            iter = self.gui.get_object('liststore1').append([x])
            if x == self.config.getSetting('General', 'backend', 'autodetect'):
                self.gui.get_object('combobox1').set_active_iter(iter)
        self.gui.get_object('settings').set_transient_for(self.roxe.gui.get_object('mainw'))
        self.gui.get_object('settings').set_modal(True)
        if show:
            self.gui.get_object('settings').show()
        else:
            self.hideSettings(None)

    def togglePlugin(self, obj, path):
        if path is not None:
            model = self.gui.get_object('liststore2')
            iter = model.get_iter(path)
            model[iter][0] = not model[iter][0]
            if not model[iter][0]:
                self.pymaxe.unloadPlugin(model[iter][1])
                self.blacklist.append(model[iter][1])
            else:
                self.pymaxe.loadPlugin(model[iter][1])
                self.blacklist.pop(self.blacklist.index(model[iter][1]))

    def hideSettings(self, obj, event=None):
        self.config.setSetting('General', 'download_covers', self.gui.get_object('checkbutton1').get_active())
        self.config.setSetting('General', 'download_lyrics', self.gui.get_object('checkbutton7').get_active())
        self.config.setSetting('General', 'autoupdate', self.gui.get_object('checkbutton2').get_active())
        self.config.setSetting('General', 'opendownloaded', self.gui.get_object('checkbutton3').get_active())
        self.config.setSetting('General', 'downloadhd', self.gui.get_object('checkbutton4').get_active())
        self.config.setSetting('General', 'threadeddownload', self.gui.get_object('checkbutton6').get_active())
        self.config.setSetting('General', 'showsuggestions', self.gui.get_object('checkbutton8').get_active())
        self.config.setSetting('General', 'downloadthreads', self.gui.get_object('spinbutton1').get_value())
        self.config.setSetting('General', 'download_into_default', self.gui.get_object('filechooserbutton1').get_filename())
        self.config.setSetting('General', 'pymaxe_plugins_folder', self.gui.get_object('filechooserbutton2').get_filename())
        self.config.setSetting('General', 'audio_player', self.gui.get_object('filechooserbutton3').get_filename())
        self.config.setSetting('General', 'video_player', self.gui.get_object('filechooserbutton4').get_filename())
        self.config.setSetting('General', 'preview_video', self.gui.get_object('checkbutton5').get_active())
        self.config.setSetting('General', 'backend', self.gui.get_object('liststore1')[self.gui.get_object('combobox1').get_active_iter()][0])
        self.config.setSetting('General', 'plugins_blacklist', ','.join(self.blacklist))
        self.config.saveSetting()
        self.gui.get_object('settings').hide()

        return True

    def showHidePreview(self, obj, event=None):
        try:
            sel = self.gui.get_object('liststore1')[self.gui.get_object('combobox1').get_active_iter()][0]
            if sel == 'vlc' or sel == 'mplayer' or sel == 'gstreamer':
                self.gui.get_object('checkbutton5').show()
            else:
                self.gui.get_object('checkbutton5').hide()
        except:
            pass

    def showThreadsOptions(self, obj, event=None):
        hbox = self.gui.get_object('hbox6')
        if obj.get_active():
            hbox.show()
        else:
            hbox.hide()

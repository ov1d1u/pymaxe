#-*- coding: utf-8 -*-
import os, datetime, thread2, gobject
path = os.getcwd()

def getBackend(preset, xid):
    backend = None
    if preset == 'autodetect':
        if not backend:
            try:
                import gst, pygst
                backend = GST(gst, xid)
                return backend
            except:
                pass
        if not backend:
            try:
                import vlc
                os.chdir(path)
                backend = VLCPlayer(vlc, xid)
                return backend
            except:
                pass
        if not backend:
            try:
                from win32com.client import Dispatch
                backend = WMPlayer(Dispatch, xid)
                return backend
            except:
                pass
    else:
        if preset == 'vlc':
            try:
                import vlc
                os.chdir(path)
                backend = VLCPlayer(vlc, xid)
                return backend
            except Exception, e:
                print e
        elif preset == 'gstreamer':
            try:
                import gst, pygst
                backend = GST(gst, xid)
                return backend
            except Exception, e:
                print e
        elif preset == 'Windows Media Player':
            try:
                from win32com.client import Dispatch
                backend = WMPlayer(Dispatch, xid)
                return backend
            except:
                pass
        else:
            return None

class WMPlayer:
    def __init__(self, Dispatch, xid):
        print 'using WMPlayer'
        self.mp = Dispatch("WMPlayer.OCX")
        self.playing = False

    def load(self, url):
        tune = self.mp.newMedia(url)
        self.mp.currentPlaylist.appendItem(tune)

    def play(self):
        self.mp.controls.play()
        self.playing = True

    def pause(self):
        self.mp.controls.pause()
        self.playing = False

    def unload(self):
        self.mp.currentPlaylist.clear()
        self.mp.controls.stop()

    def volume(self, value):
        self.mp.settings.volume = int(value)

    def seek(self, pos):
        self.mp.controls.currentPosition = pos

    def isPlaying(self):
        return self.playing

    def getPos(self):
        import time
        try:
            dur_int = self.mp.currentMedia.duration
            cur_int = self.mp.controls.currentPosition
            if dur_int == 0:
                dur_int = -1
            pos = float(cur_int) / float(dur_int) * 100
            cur = time.strftime('%M:%S', time.gmtime(cur_int))
            tot = time.strftime('%M:%S', time.gmtime(dur_int))
            return [pos, cur, tot]
        except Exception, e:
            return [0, '00:00', '00:00']

class GST:
    def __init__(self, gst, xid):
        self.gst = gst
        self.xid = xid
        self.mp = gst.element_factory_make("playbin2", "player")
        volume = gst.element_factory_make("volume", "volume")
        self.mp.add(volume)
        if not xid:
            fakesink = gst.element_factory_make("testsink", "fakesink")
            fakesink.set_property('async', False)
            self.mp.set_property("video-sink", fakesink)
        else:
            xvimagesink = gst.element_factory_make("xvimagesink", "xvimagesink")
            xvimagesink.set_xwindow_id(xid)
            xvimagesink.set_property('force-aspect-ratio', True)
            self.mp.set_property("video-sink", xvimagesink)

        self.playing = False

    def load(self, url):
        self.mp.set_property("uri", url)

    def play(self):
        xvimagesink = self.gst.element_factory_make("xvimagesink", "xvimagesink")
        xvimagesink.set_xwindow_id(self.xid)
        xvimagesink.set_property('force-aspect-ratio', True)
        self.mp.set_property("video-sink", xvimagesink)
        self.mp.set_state(self.gst.STATE_PLAYING)
        self.playing = True

    def pause(self):
        self.mp.set_state(self.gst.STATE_PAUSED)
        self.playing = False

    def unload(self):
        self.mp.set_state(self.gst.STATE_NULL)
        self.playing = False

    def volume(self, value):
        volume = value / 100
        self.mp.set_property("volume", volume)

    def seek(self, pos):
        time_format = self.gst.Format(self.gst.FORMAT_TIME)
        self.mp.seek_simple(time_format, self.gst.SEEK_FLAG_FLUSH, pos)

    def isPlaying(self):
        return self.playing

    def getPos(self):
        try:
            time_format = self.gst.Format(self.gst.FORMAT_TIME)
            dur_int = self.mp.query_duration(time_format, None)[0]
            cur_int = self.mp.query_position(time_format, None)[0]
            if dur_int == 0:
                dur_int = -1
            pos = float(cur_int) / float(dur_int) * float(100)
            cur = self.convert_ns(cur_int)
            tot = self.convert_ns(dur_int)
            return [pos, cur, tot]
        except:
            return [0, '00:00', '00:00']

    def getPos_precise(self):
        try:
            time_format = self.gst.Format(self.gst.FORMAT_TIME)
            cur_int = self.mp.query_position(time_format, None)[0]
            cur = str(datetime.timedelta(seconds=float(cur_int) / float(1000000000)))
            return cur
        except:
            return '0:00:00.00'

    def convert_ns(self, time_int):
        time_int = time_int / 1000000000
        time_str = ""
        if time_int >= 3600:
            _hours = time_int / 3600
            time_int = time_int - (_hours * 3600)
            time_str = str(_hours) + ":"
        if time_int >= 600:
            _mins = time_int / 60
            time_int = time_int - (_mins * 60)
            time_str = time_str + str(_mins) + ":"
        elif time_int >= 60:
            _mins = time_int / 60
            time_int = time_int - (_mins * 60)
            time_str = time_str + "0" + str(_mins) + ":"
        else:
            time_str = time_str + "00:"
        if time_int > 9:
            time_str = time_str + str(time_int)
        else:
            time_str = time_str + "0" + str(time_int)

        return time_str

class VLCPlayer:
    def __init__(self, vlc, xid):
        if xid:
            Instance = vlc.Instance()
        else:
            Instance = vlc.Instance(['--vout', 'dummy'])
        self.mp = vlc.MediaPlayer(Instance)
        if os.environ.get("APPDATA"):
            self.mp.set_hwnd(xid)
        else:
            self.mp.set_xwindow(xid)
        self.playing = False
        os.chdir(path)

    def load(self, url):
        self.mp.set_mrl(url)

    def play(self):
        self.mp.play()
        self.playing = True

    def pause(self):
        self.mp.pause()
        self.playing = False

    def unload(self):
        self.mp.stop()
        self.playing = False

    def volume(self, value):
        self.mp.audio_set_volume(int(value))

    def seek(self, pos):
        goto = int(self.mp.get_length() * float(pos / 100))
        self.mp.set_time(goto)

    def isPlaying(self):
        return self.playing

    def getPos(self):
        try:
            pos = float(self.mp.get_time()) / float(self.mp.get_length()) * 100
        except:
            pos = 0.0
        try:
            cur = str(datetime.timedelta(seconds=self.mp.get_time()/1000))[2:]
        except:
            cur = '00:00'
        try:
            tot = str(datetime.timedelta(seconds=self.mp.get_length()/1000))[2:]
        except:
            tot = '00:00'
        return [pos, cur, tot]

    def getPos_precise(self):
        try:
            cur = str(datetime.timedelta(seconds=float(self.mp.get_time())/float(1000)))
        except:
            cur = '00:00:00'
        return cur

class mediaPlayer:
    def __init__(self, config, setAdjustment, xid):
        if config.getSetting('General', 'preview_video', True):
            xid = xid
        else:
            xid = False
        backend = getBackend(config.getSetting('General', 'backend', 'autodetect'), xid)

        if backend:
            self.backend = backend
            self.available = True
            self.load = backend.load
            self.play = backend.play
            self.pause = backend.pause
            self.unload = backend.unload
            self.volume = backend.volume
            self.seek = backend.seek
            self.isPlaying = backend.isPlaying
            self.isSeeking = False
            self.thread = None
            self.setAdjustment = setAdjustment
            self.getPos_precise = backend.getPos_precise
        else:
            self.available = False

    def updateAdjustment(self, ret):
        if self.thread:
            if self.thread.isAlive():
                try:
                    self.thread.terminate()
                except:
                    pass
        self.thread = thread2.Thread(target=self.getAdjustment, args=(self.setAdjustment, ret))
        self.thread.start()
        if not self.isPlaying():
            return False
        return ret

    def getAdjustment(self, callback, ret):
        pos = self.backend.getPos()
        gobject.idle_add(callback, pos, ret)

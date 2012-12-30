#-*- coding: utf-8 -*-
import urllib, urllib2, gtk, gobject, thread2, re
import coverFinder

class AlbumDownloader:
	def __init__(self, pymaxe, album, albumdata, startDownload):
		self.terminate = False
		self.pymaxe = pymaxe
		self.album = album
		self.data = albumdata
		self.download = startDownload
		self.gui = gtk.Builder()
		self.gui.add_from_file('albumdownload.glade')
		self.gui.connect_signals({
			"hide" : self.hide,
			"toggleCheck" : self.toggleCheck,
			"hideErr" : self.hideErr,
			"startDownload" : self.startDownload,
			"selectFolder" : self.selectFolder
		})
		
	def show(self):
		self.gui.get_object('dwalbum').show()
		self.gui.get_object('label1').set_text('Downloading ' + self.data['artist'] + ' - ' + self.data['name'])
		self.gui.get_object('progressbar1').set_fraction(0)
		self.gui.get_object('hbox5').show()
		self.terminate = False
		self.thread = thread2.Thread(target=self.getTracks, args=(self.data['mbid'], ))
		self.thread.start()
	
	def getTracks(self, albumID):
		tracks = self.album.getAlbumTracks(albumID)
		plugins = self.pymaxe.activePlugins
		results = {}
		t = len(tracks)
		c = 1
		for track in tracks:					# for each track in album we initiate a search
			if self.terminate:
				return
			artist = track[0]
			title = track[1]
			string = artist + ' - ' + title
			results[string] = None
			gobject.idle_add(self.updateProgress, c, t)
			for x in plugins:				# searching with each Pymaxe plugin
				data = self.pymaxe.search(string, x)
				if not data:
					break
				for y in data:				# we are receiving a dict with format {pluginName : [results_list]}
					for z in data[y]:		# we get the results from each plugin
						if self.terminate:
							return
						tracktitle = z[1].lower()
						testartist = artist.lower()
						testtitle = title.lower()
						# some tricks to get better results
						tracktitle = self.tricks(tracktitle)
						testartist = self.tricks(testartist)
						testtitle = self.tricks(testtitle)
						testartist = re.sub(r'\W+', '', testartist)
						testtitle = re.sub(r'\W+', '', testtitle)
						if testartist.lower() in re.sub(r'\W+', '', tracktitle).lower() and testtitle.lower() in re.sub(r'\W+', '', tracktitle).lower():
							trilutemp = None
							if y == 'Trilulilu':
								# Trilulilu SPECIAL FIX
								# we try to avoid Trilulilu, because some media files
								# are no longer available due to a copyright issue with
								# Sony Entertainment(TM)
								trilutemp = z[2]
							else:
								if z[0] == 0x01:
									results[string] = z[2]
							if not results[string]:
								# we didn't find any better option than Trilulilu
								# so we use triluilu, if available
								if trilutemp:
									results[string] = trilutemp
							break
			c = c + 1
			if self.terminate:
				return
			gobject.idle_add(self.updateProgress, c, t)
		if self.terminate:
			return
		gobject.idle_add(self.addTracks, results)
		
	def updateProgress(self, completed, total):
		fr = float(completed) / float(total)
		self.gui.get_object('progressbar1').set_fraction(fr)
		
	def addTracks(self, results):
		liststore = self.gui.get_object('liststore1')
		errstore = self.gui.get_object('liststore2')
		err = False
		for x in results:
			if results[x]:
				liststore.append([True, x, results[x]])
			else:
				err = True
				errstore.append([x])
		if err:
			self.gui.get_object('dialog1').show()
		self.gui.get_object('button2').set_sensitive(True)
		self.gui.get_object('hbox5').hide()
		
	def toggleCheck(self, cell, path):
		model = self.gui.get_object('liststore1')
		if path is not None:
			iter = model.get_iter(path)
			model[iter][0] = not model[iter][0]
			
	def selectFolder(self, obj, event=None):
		chooser = gtk.FileChooserDialog(title='Select folder...',action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
		chooser.set_default_response(gtk.RESPONSE_OK)
		response = chooser.run()
		if response == gtk.RESPONSE_OK:
			saveAs = chooser.get_filename()
			self.gui.get_object('label4').set_text(saveAs)
		chooser.destroy()
			
	def startDownload(self, obj, event=None):
		saveIn = self.gui.get_object('label4').get_text()
		model = self.gui.get_object('liststore1')
		iter = model.get_iter_root()
		if self.gui.get_object('checkbutton1').get_active():
			cover = coverFinder.coverFinder(self.pymaxe, self.saveCover)
			cover.searchCover('', self.data['mbid'])
		while iter:
			if model[iter][0]:
				source = model[iter][2]
				titlu = model[iter][1]
				saveAs = saveIn + '/' + titlu + '.mp3'
				self.download(titlu, source, saveAs)
			iter = model.iter_next(iter)
		self.gui.get_object('dwalbum').hide()
		self.gui.get_object('dwalbum').destroy()
		
	def saveCover(self, cover):
		saveIn = self.gui.get_object('label4').get_text()
		if cover:
			cover.save(saveIn + '/cover.jpg', "JPEG")
			
	def hideErr(self, obj, event=None):
		self.gui.get_object('dialog1').hide()
		return True
		
	def hide(self, obj, event=None):
		try:
			self.thread.terminate()
			self.terminate = True
		except:
			pass
		self.gui.get_object('dwalbum').hide()
		self.gui.get_object('dwalbum').destroy()

	def tricks(self, text):
		text = text.replace('and', '')
		text = text.replace('featuring', '')
		text = re.sub(r'\([^)]*\)', '', text)
		text = re.sub(r'\[[^)]*\]', '', text)
		return text
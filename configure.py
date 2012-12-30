import ConfigParser, os, sys
if '--portable' in sys.argv:
	home = os.getcwd()
	cfgfile = home + '/roxe.ini'
else:
	if os.environ.get("APPDATA"):
		home = os.environ.get("APPDATA")
		if not os.path.exists(home + '/roxe'):
			os.mkdir(home + '/roxe')
		cfgfile = home + '/roxe/roxe.ini'
	else:
		home = os.environ.get("HOME")
		if not os.path.exists(home + '/.roxe'):
			os.mkdir(home + '/.roxe')
		cfgfile = home + '/.roxe/roxe.cfg'

class Config:
	def __init__(self):
		self.config = ConfigParser.ConfigParser()
		self.config.read(cfgfile)
		if not self.config.has_section('General'):
			self.config.add_section('General')
			
	def getSetting(self, section, name, default):
		try:
			self.config.read(cfgfile)
			s = self.config.get(section, name)
			if s == 'True':
				return True
			if s == 'False':
				return False
			if s == 'None':
				return None
			return s
		except:
			return default
			
	def setSetting(self, section, name, value):
		self.config.set(section, name, value)
	
	def saveSetting(self):
		self.config.write(open(cfgfile, 'w'))
		
	def guessDownloadFolder(self):
		if os.environ.get("APPDATA"):
			return os.environ.get("USERPROFILE") + '/Desktop'
		else:
			return os.environ.get("HOME") + '/Desktop'
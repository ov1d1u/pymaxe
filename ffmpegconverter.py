#-*- coding: utf-8 -*-
import os, re, ffmpegexec, subprocess, time, datetime, thread2, datetime

if os.environ.get("APPDATA"):
	ffmpeg = 'ffmpeg.exe'		# We're on a Windows machine
	from win32file import ReadFile, WriteFile
	from win32pipe import PeekNamedPipe
	import msvcrt
else:
	import select, fcntl
	ffmpeg = '/usr/bin/ffmpeg'	# We're on a Unix machine
	
class FFConvert:
	def __init__(self, source, dest, cstring):
		self.cmd = cstring.split()
		self.cmd[self.cmd.index('INPUT')] = source
		self.cmd[self.cmd.index('OUTPUT')] = dest
		self.cmd.insert(0, '-y')
		self.cmd.insert(0, ffmpeg)
		self.source = source
		self.dest = dest
		self.done = False
		self.time_seconds = 0
		self.current = -1
		
	def start(self):
		self.chunk = None
		thread2.Thread(target=self.runffmpeg).start()
		
	def runffmpeg(self):
		if os.environ.get("APPDATA"):
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			self.pipe = ffmpegexec.Popen(self.cmd, stderr=subprocess.PIPE, startupinfo=startupinfo)
		else:
			self.pipe = ffmpegexec.Popen(self.cmd, stderr=subprocess.PIPE)
		secs = None
		
		while True:
			self.chunk = self.pipe.recv_err()
			if self.chunk == '':
				time.sleep(0.002)
				continue
			secs = self.getProgress()
			if secs:
				if secs[0] and secs[1]:
					self.time_seconds = secs[0]
					self.current = secs[1]
					if secs[0] == secs[1]:
						break
				else:
					self.progress = -1
			time.sleep(0.002)
		self.done = True
			
	def getProgress(self, skipthis = 0):
		chunk = self.chunk
		if not chunk:
			return
		if not self.time_seconds:
			if 'Duration:' in chunk:
				line = chunk.split()
				durata = line[line.index('Duration:') + 1][:-4]
				[h, m, s] = durata.split(':')
				self.time_seconds = int(h) * 3600 + int(m)* 60 + int(s)
		
		if self.time_seconds:
			self.current = 0
			if 'time=' in chunk:
				line = chunk.split()
				idx = 0
				for x in line:
					if 'time=' in x:
						idx = line.index(x)
				line = line[idx].split('=')
				if ':' in line[line.index('time') + 1]:
					curr = line[line.index('time') + 1][:-3]
					[h, m, s] = curr.split(':')
				else:
					sec = line[line.index('time') + 1]
					curr = str(datetime.timedelta(seconds=int(float(sec))))
					[h, m, s] = curr.split(':')
				self.current = int(h) * 3600 + int(m)* 60 + int(s)
		return [self.time_seconds, self.current]
		
	def cancel(self):
		if self.pipe.poll() == None:
			self.pipe.kill()
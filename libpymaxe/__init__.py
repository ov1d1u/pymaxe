#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import extras

FILE_TYPE_AUDIO = 0x01
FILE_TYPE_VIDEO = 0x02

DEBUG = 1

class Pymaxe:
	def __init__(self):
		self.version = 0.99
		self.currentPath = os.path.dirname(os.path.realpath(__file__))
		self.pluginDirs = []
		self.setPluginsDir(self.currentPath + '/plugins')
		self.plugins = {}
		self.pluginObj = {}
		self.activePlugins = []	
		self.readPlugins()
		
	def setPluginsDir(self, url):
		self.pluginDirs.append(url)
		sys.path.insert(0, url)
		return True
		
	def readPlugins(self):
		for folder in self.pluginDirs:
			for x in os.listdir(folder):
				if os.path.exists(folder + '/' + x + '/__init__.py'):
					self.plugins[x] = folder + '/' + x
				if os.path.splitext(folder)[1] == '.py':
					self.plugins[x] = folder + '/' + x
	
	def loadPlugin(self, name):
		if name in self.plugins:
			try:
				module = __import__(name)
				self.pluginObj[name] = module.Plugin()
				self.activePlugins.append(name)
				return True
			except:
				if DEBUG:
					extras.output_exc()
				return False
				
	def unloadPlugin(self, name):
		try:
			extras.delete_module(name)
			self.activePlugins.pop(self.activePlugins.index(name))
			return True
		except:
			if DEBUG:
				extras.output_exc()
			return False
			
	def getActivePlugins(self):
		return self.activePlugins
		
	def getPluginInfo(self, name):
		if name in self.activePlugins:
			try:
				pluginName = self.pluginObj[name].pluginName
				pluginVersion = self.pluginObj[name].version
				pluginAuthor = self.pluginObj[name].author
				pluginHomepage = self.pluginObj[name].homepage
				pluginUpdate = self.pluginObj[name].update
				data = {'name' : pluginName,
					'version' : pluginVersion,
					'author' : pluginAuthor,
					'homepage' : pluginHomepage,
					'update' : pluginUpdate}
				return data
			except:
				if DEBUG:
					extras.output_exc()
				return False
		else:
			return False
			
	def search(self, query, plugin=None):
		results = {}
		if not plugin:
			for x in self.activePlugins:
				try:
					results[x] = self.pluginObj[x].search(query)
				except:
					if DEBUG:
						extras.output_exc()
					return None
		else:
			try:
				results[plugin] = self.pluginObj[plugin].search(query)
			except:
				if DEBUG:
					extras.output_exc()
				return None
		return results
		# FORMAT: [TYPE, title, url, time]
		
	def getDetails(self, plugin, url):
		if plugin in self.activePlugins:
			try:
				return self.pluginObj[plugin].fileData(url)
			except:
				if DEBUG:
					extras.output_exc()
				return None
		else:
			return None
			
	def getPluginObj(self, plugin):
		if plugin in self.activePlugins:
			return 're';#self.pluginObj[plugin]
		else:
			return False
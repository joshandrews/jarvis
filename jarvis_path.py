class path:
	def __init__(self, path, handlers=[]):
		self._path = path
		self._handlers = handlers
		
	def addHandler(self, index):
		self._handlers.append(index)
	
	def addHandlers(self, list):
		self._handlers.extend(list)
	
	def checkTriggers(self, list):
		if self._path is not None:
			for voiceElement in list:
				if (voiceElement in self._path[0]):
					self._triggered(list.index(voiceElement), list)
	
	def _triggered(self, element, list):
		for i in range(element, len(list)):
			pathIndex = i-element
			if (pathIndex < len(self._path)):
				if (list[i] in self._path[pathIndex]):
					if (pathIndex in self._handlers):
						print pathIndex
						return(pathIndex)
			
import json


class RelativeJsonFile(object):
	"""
	This class interfaces input and output to json files.
	(Ported from version 4.0.0)
	"""
	def __init__(self, input):
		self.file = input
		with open(f"{input}", encoding="utf-8") as file:
			self.__dict__["_data"] = json.load(file)

	def __getattribute__(self, name):
		_data = object.__getattribute__(self, "_data")
		if name in _data:
			return _data[name]
		return object.__getattribute__(self, name)

	def __enter__(self):
		return self

	def __exit__(self, *args, **kwargs):
		self.flush()

	def flush(self):
		with open(f"{self.file}", "w", encoding="utf-8") as file:
			json.dump(object.__getattribute__(self, "_data"),
					  file, indent=4, ensure_ascii=False)

class Config(RelativeJsonFile):
	"""
	Represents the config file.
	"""
	_data = {}
	def __init__(self):
		self._data = {}
		super().__init__("config.json")

class Messages(RelativeJsonFile):
	"""
	Represents the messages file.
	"""
	_data = {}
	def __init__(self):
		self._data = {}
		super().__init__("messages.json")

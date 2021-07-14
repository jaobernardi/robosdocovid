class Place:
	def __init__(self, name, type, parents, ibge_code, geojson, timestamps, sources, data, alias=[]):
		self.name = name
		self.type = type
		self.parents = parents
		self.ibge_code = ibge_code
		self.geojson = geojson
		self.timestamp = timestamps
		self.sources = sources
		self.data = data
		self.alias = []

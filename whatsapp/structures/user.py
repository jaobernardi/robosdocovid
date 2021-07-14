class User:
	def __init__(self, phone, uuid, places, tags, permissions, roles, new=False):
		self.phone = phone
		self.uuid = uuid
		self.places = places
		self.tags = tags
		self.permissions = permissions
		self.roles = roles
		self.new = new

	@property
	def _store(self):
		store = {}
		store["places"] = self.places
		store["tags"] = self.tags
		store["permissions"] = self.permissions
		store["roles"] = self.roles
		return store

	def flush_info(self):
		import api
		api.update_user(self)

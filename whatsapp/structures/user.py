global temporary_context
temporary_context = {}

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
	def temporary_context(self):
		if self.uuid not in temporary_context:
			temporary_context[self.uuid] = Context()
		return temporary_context[self.uuid]


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

	def has_permission(self, permission):
		possible = list(self.permissions)
		match_tokens = permission.split(".")

		while len(possible) > 0:
			for perm in possible:
				test_tokens = perm.split(".")
				index = 0
				for token in test_tokens:
					if match_tokens[index] == "*":
						return True
					if token == "*":
						return True
					if token != match_tokens[index]:
						possible.remove(perm)
						break
					if index+1 == len(test_tokens) and index+1 == len(match_tokens):
						return True
					if index+1 >= len(match_tokens):
						possible.remove(perm)
						break
					index += 1
		return False

class Context(object):

    def __init__(self):
        x = object.__getattribute__(self, "__dict__")
        x['store'] = {}

    def __setattr__(self, name, value):
        store = object.__getattribute__(self, "store")
        if name not in store:
            store[name] = None
        store[name] = value
        object.__setattr__(self, "store", store)

    def __getattribute__(self, name):
        if name.startswith("_"):
            return object.__getattribute__(self, name)

        store = object.__getattribute__(self, "store")
        if name in store:
            return store[name]
        return None

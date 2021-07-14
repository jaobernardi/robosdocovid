import logging
import requests
from structures import User, Config, Place
import functools

config = Config()

def get_user(phone=None, uuid=None):
	print(phone, uuid)
	if not phone and not uuid:
		raise TypeError("Missing phone or uuid keywords.")

	if phone:
		req = requests.get(f"https://api.robocovid.app/users/phone/{phone}?token={config.api['token']}")
	elif uuid:
		req = requests.get(f"https://api.robocovid.app/users/uuid/{uuid}?token={config.api['token']}")

	if req.status_code == 200:
		data = req.json()
		for query in data['query']:
			return User(**query)
	elif req.status_code == 403:
		logging.critical("Unauthorized query for the API. (probably an invalid token.)")


def create_user(phone, uuid):
	return requests.post(f"https://api.robocovid.app/users/new", json={"phone": phone, "uuid": uuid, "token": config.api['token']})

@functools.cache
def resolve_name(name):
	req = requests.get(f"https://api.robocovid.app/ibge/find?query={name}")
	if req.status_code == 200:
		data = req.json()
		return data['query']
	else:
		logging.critical(f"Failed to query data for {name}")
		return []

def ibge_lookup(code):
	req = requests.get(f"https://api.robocovid.app/ibge/find?code={code}")
	if req.status_code == 200:
		data = req.json()
		return data['query']
	else:
		logging.critical(f"Failed to query data for {code}")
		return []

def get_users():
	req = requests.get(f"https://api.robocovid.app/users/all?token={config.api['token']}")
	if req.status_code == 200:
		data = req.json()
		for query in data['query']:
			yield User(**query)
	elif req.status_code == 403:
		logging.critical("Unauthorized query for the API. (probably an invalid token.)")

def get_place_data(code):
	req = requests.get(f"https://api.robocovid.app/places/query?code={code}")
	if req.status_code == 200:
		data = req.json()
		return Place(**data['query'])
	else:
		logging.critical(f"Failed to query data for {code}")


def update_user(user: User):
	req = requests.post(f"https://api.robocovid.app/users/uuid/{user.uuid}/edit", json={**user._store, "token": config.api['token']})

import json
import unidecode
from difflib import *

ibge_codes = json.load(open("ibge.json"))
ibge_names = {}
for code, info in ibge_codes.items():
	add = ""
	if info['type'] == "city":
		add += "+"+code[:2]
	ibge_names[unidecode.unidecode(info['name']).lower()+add] = int(code)
	if "alias" in info:
		for alias in info['alias']:
			ibge_names[unidecode.unidecode(alias).lower()+add] = int(code)

def parse_ibge(code):
	code = str(code)
	parents  = []
	# If code refers to a city or state
	if len(code) > 0 and code != "0":
		parents.append(ibge_codes["0"])
	if len(code) > 1:
		parents.append(ibge_codes[code[0]])
	# If code refers to a city
	if len(code) > 2:
		parents.append(ibge_codes[code[:2]])

	return ibge_codes[code] | {"parents": parents}

def find_ibge(name):
	# This should be used to find a code that you already know part of it.
	if unidecode.unidecode(name.lower()) in ibge_names:
		return ibge_names[unidecode.unidecode(name.lower())]

def query_name(name):
	# This should be used whenever you aren't sure the place even exists. Also, it deals with incorrect writings.
	output = {}
	for code in ibge_codes:
		data = ibge_codes[code]
		ratio = SequenceMatcher(None, unidecode.unidecode(name.lower()), unidecode.unidecode(data['name'].lower())).ratio()
		if ratio > 0.80:
			output[code] = data|{"match": ratio}
		elif 'alias' in data:
			for alias in data['alias']:
				ratio = SequenceMatcher(None, unidecode.unidecode(name.lower()), unidecode.unidecode(alias.lower())).ratio()
				if ratio > 0.80:
					output[code] = data|{"match": ratio}
					break
	return output

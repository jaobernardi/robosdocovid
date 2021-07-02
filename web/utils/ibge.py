import json
import unidecode

ibge_codes = json.load(open("ibge.json"))
ibge_names = {}
for code, info in ibge_codes.items():
	add = ""
	if info['type'] == "city":
		add += "+"+code[:2]
	ibge_names[unidecode.unidecode(info['name']).lower()+add] = int(code)

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
	if unidecode.unidecode(name.lower()) in ibge_names:
		return ibge_names[unidecode.unidecode(name.lower())]

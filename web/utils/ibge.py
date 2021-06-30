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
	return ibge_codes[str(code)]

def find_ibge(name):
	if unidecode.unidecode(name.lower()) in ibge_names:
		return ibge_names[unidecode.unidecode(name.lower())]

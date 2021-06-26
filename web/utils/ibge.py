import json

ibge_codes = json.load(open("ibge.json"))

def parse_ibge(code):
	return ibge_codes[str(code)]

import json

ibge_codes = json.loads(open("ibge.json"))

def parse_ibge(code):
	return ibge_codes[str(code)]

import requests
from utils import find_ibge
from structures import Database
from datetime import datetime
import json
import urllib.request

def sanitize(string, split, autotype):
	unqouted = [i.removeprefix('"').removesuffix('"') for i in string.split(split)]
	output = []
	for piece in unqouted:
			if piece.isdigit() and autotype:
					output.append(float(piece))
					continue
			output.append(piece)
	return output

def case_type(input):
	if "recuperado" in input.lower():
		return "RECOVERED"
	elif "obito" in input.lower():
		return "DEAD"
	return "ACTIVE"

def case_type_sc(recovered, dead):
	if "sim" in recovered.lower():
		return "RECOVERED"
	elif "sim" in dead.lower():
		return "DEAD"
	return "ACTIVE"

def read_until_line(file_object, split=";", autotype=False):
	while True:
			output = ""
			while (data := file_object.read(1)) != "\n":
				if not data:
					return
				output += data
			if not data:
				return
			yield sanitize(output[:-1], split, autotype)

def RS_Collect():
	output = {}
	req = requests.get("http://ti.saude.rs.gov.br/covid19/download", stream=True)
	reader = req.iter_lines()
	now = datetime.now()
	next(reader)

	# Generate the State place object
	output[43] = {"cases": 0, "deaths": 0, "recovered": 0, "active_cases": 0}
	# read cases in the notification csv
	for case in reader:
		case = sanitize(case.decode('utf-8'), ";", False)
		if len(case) > 1:
			city = find_ibge(case[1]+"+43")
			if not city: print(case[1])
			state = case_type(case[11])

			# create the place if it is not in the output
			if city not in output:
				# Insert place
				output[city] = {"cases": 0, "deaths": 0, "recovered": 0, "active_cases": 0}

			output[city]["cases"] += 1
			output[43]["cases"] += 1
			if state == "DEAD":
				output[city]["deaths"] += 1
				output[43]["deaths"] += 1
			elif state == "RECOVERED":
				output[city]["recovered"] += 1
				output[43]["recovered"] += 1
			else:
				output[city]["active_cases"] += 1
				output[43]["active_cases"] += 1


	data = requests.get("https://secweb.procergs.com.br/isus-covid/api/v1/markers/municipios")
	if data.status_code == 200:
		data = data.json()
		for city in data["markers"]:
			name = find_ibge(city["name"]+"+43")
			if name in output:
				output[name]["beds_uti_adult_general"] = city["beds"]["adults"]["percent"]
				output[name]["beds_uti_adult_sus"] = city["beds"]["adultsSus"]["percent"]
				output[name]["beds_uti_adult_private"] = city["beds"]["adultsPrivado"]["percent"]
				output[name]["beds_covid"] = city["beds"]["others"]["percent"]
				output[name]["respirators"] = city["beds"]["respirators"]["percent"]

	vaccines = requests.get("https://iede.rs.gov.br/server/rest/services/COVID19/perc_doses_aplic_por_disponibilizadas/FeatureServer/0/query?f=json&where=1=1&returnGeometry=false&outFields=*", verify=False)
	if vaccines.status_code == 200:
		for region in vaccines.json()["features"]:
			region = region["attributes"]
			city = region["cod_ibge"]
			if city in output:
				output[city]["vaccinated_percent"] = round((region["doses_aplicadas"]*100)/region["doses_disponibilizadas"],2)
				output[city]["vaccinated_first_percent"] =  round((region["dose_1"]*100)/region["pop_total_1"], 2)
				output[city]["vaccinated_second_percent"] = round((region["dose_2"]*100)/region["pop_total_1"], 2)
				output[city]["vaccinated_remain"] = region["doses_disponibilizadas"]-region["doses_aplicadas"]
				output[city]["vaccinated_health_1st"] = region["vac_prof_saude_d1"]
				output[city]["vaccinated_80_1st"] = region["vac_80mais_d1"]
				output[city]["vaccinated_75_1st"] = region["vac_75_79_d1"]
				output[city]["vaccinated_70_1st"] = region["vac_70_74_d1"]
				output[city]["vaccinated_65_1st"] = region["vac_65_69_d1"]
				output[city]["vaccinated_60_1st"] = region["vac_60_64_d1"]
				output[city]["vaccinated_codeath_1st"] = region["vac_comorb_d1"]
				output[city]["vaccinated_health_2nd"] = region["vac_prof_saude_d2"]
				output[city]["vaccinated_80_2nd"] = region["vac_80mais_d2"]
				output[city]["vaccinated_75_2nd"] = region["vac_75_79_d2"]
				output[city]["vaccinated_70_2nd"] = region["vac_70_74_d2"]
				output[city]["vaccinated_65_2nd"] = region["vac_65_69_d2"]
				output[city]["vaccinated_60_2nd"] = region["vac_60_64_d2"]
				output[city]["vaccinated_codeath_2nd"] = region["vac_comorb_d2"]

	with Database() as db:
		for city in output:
			db.insert_place_data(city, json.dumps(output[city]), 'Secretaria Estadual de Saúde do Rio Grande do Sul.', now)
	return output


def SC_Collect():
	output = {}
	output[42] = {"cases": 0, "deaths": 0, "active_cases": 0, "recovered": 0}
	req = urllib.request.urlretrieve("http://ftp2.ciasc.gov.br/boavista_covid_dados_abertos.csv")
	reader = read_until_line(open(req[0], encoding="utf-8"))
	next(reader)


	for case in reader:
		city = int(case[17])
		state = case_type_sc(case[1], case[11])
		if city.upper() not in output:
			# Insert place
			output[city] = {"cases": 0, "deaths": 0, "recovered": 0, "active_cases": 0}


		output[city]["cases"] += 1
		output[42]["cases"] += 1
		if state == "DEAD":
			output[city]["deaths"] += 1
			output[42]["deaths"] += 1
		elif state == "RECOVERED":
			output[city]["recovered"] += 1
			output[42]["recovered"] += 1
		else:
			output[city]["active_cases"] += 1
			output[42]["active_cases"] += 1
	with Database() as db:
		for city in output:
			db.insert_place_data(city, json.dumps(output[city]), 'Secretaria Estadual de Saúde do Rio Grande do Sul.', now)
	return output

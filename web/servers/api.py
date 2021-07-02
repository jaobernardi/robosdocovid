# Handle requests for the 'API'
import events
from structures import Response, Config, Database
import json
import pyotp
from datetime import datetime
from utils import parse_ibge, generate_string, union_dicts_with_regex

config = Config()
ibge = json.load(open("ibge.json"))


# Listen for http requests
@events.add_handle("http_request")
def api_http(event):
	request = event.request
	# Check the request host
	if "Host" in request.headers and request.headers["Host"] == config.scopes["api"]:
		# Placeholder response
		match event.path:
			case ["places", "query"]:
				if request.method != "POST":
					event.default_headers = event.default_headers | {'Allow': 'POST'}
					output = {"status": 405, "message": "Method Not Allowed", "error": True}

				elif 'Content-Type' in request.headers and request.headers['Content-Type'] == 'application/json':
					try:
						data = json.loads(request.data.decode("utf-8"))
					except:
						output = {"status": 422, "message": "Unprocessable Entity", "error": True}
					else:
						match data:
							case {'code': code, 'timestamp': timestamp}:
								with Database() as db:
									code = int(code)
									ibge_data = parse_ibge(code)
									final_data = []
									match ibge_data:
										case {"type": "country"} | {"type": "region"} | {"type": "state"}:
											query = db.get_place_data(f"{code}%" if code != 0 else "%", datetime.utcfromtimestamp(timestamp) if timestamp else None)
											datas = [json.loads(entry[1]) for entry in query]
											final_data = union_dicts_with_regex(config.fields["summable"]['default'], datas)
										case _:
											query = db.get_place_data(int(code), datetime.utcfromtimestamp(timestamp) if timestamp else None)

									output = {"status": 200,
										"message": "OK",
										"error": False,
										"results": len(query),
										"query": {
											"data": final_data,
											"source": 'Not Implemented',
											"ibge_code": code,
											"timestamp": "Not Implemented",
											"geojson": f"https://servicodados.ibge.gov.br/api/v2/malhas/{code}?formato=application/vnd.geo+json",
											} | ibge_data
										}
							case _:
								output = {"status": 422, "message": "Unprocessable Entity", "error": True}
				else:
					output = {"status": 422, "message": "Unprocessable Entity", "error": True}

			# Insert data into the database
			case ["places", "insert"]:
				if request.method != "POST":
					event.default_headers = event.default_headers | {'Allow': 'POST'}
					output = {"status": 405, "message": "Method Not Allowed", "error": True}

				elif 'Content-Type' in request.headers and request.headers['Content-Type'] == 'application/json':
					try:
						data = json.loads(request.data.decode("utf-8"))
					except:
						output = {"status": 422, "message": "Unprocessable Entity", "error": True}
					else:
						match data:
							case {'code': code, 'data': data, 'source': source, 'token': token, 'timestamp': timestamp}:
								with Database() as db:
									output = {"status": 403, "message": "Unauthorized", "error": True}
									user = db.get_user_by_token(token)
									if user:
										query = db.insert_place_data(int(code), json.dumps(data), source, datetime.utcfromtimestamp(timestamp))
										query_parsed = []

										for entry in query:
											query_parsed.append({
												"data": json.loads(entry[1]),
												"source": entry[2],
												"ibge_code": code,
												"timestamp": entry[3].timestamp(),
												"geojson": f"https://servicodados.ibge.gov.br/api/v2/malhas/{entry[0]}?formato=application/vnd.geo+json"
											} | ibge_data)

										output = {"status": 200, "message": "OK", "error": False, "results": len(query), "query": query_parsed}
							case _:
								output = {"status": 422, "message": "Unprocessable Entity", "error": True}
				else:
					output = {"status": 422, "message": "Unprocessable Entity", "error": True}

			# Edit place data
			case ["places", "edit"]:
				if request.method != "POST":
					event.default_headers = event.default_headers | {'Allow': 'POST'}
					output = {"status": 405, "message": "Method Not Allowed", "error": True}

				elif 'Content-Type' in request.headers and request.headers['Content-Type'] == 'application/json':
					try:
						data = json.loads(request.data.decode("utf-8"))
					except:
						output = {"status": 422, "message": "Unprocessable Entity", "error": True}
					else:
						match data:
							case {'code': code, 'data': data, 'source': source, 'token': token, 'timestamp': timestamp}:
								with Database() as db:
									output = {"status": 403, "message": "Unauthorized", "error": True}
									user = db.get_user_by_token(token)
									if user:
										query = db.edit_place_data(int(code), json.dumps(data), source, datetime.utcfromtimestamp(timestamp))
										query_parsed = []

										for entry in query:
											query_parsed.append({
												"data": json.loads(entry[1]),
												"source": entry[2],
												"ibge_code": code,
												"timestamp": entry[3].timestamp(),
												"geojson": f"https://servicodados.ibge.gov.br/api/v2/malhas/{entry[0]}?formato=application/vnd.geo+json"
											} | ibge_data)

										output = {"status": 200, "message": "OK", "error": False, "results": len(query), "query": query_parsed}
							case _:
								output = {"status": 422, "message": "Unprocessable Entity", "error": True}
				else:
					output = {"status": 422, "message": "Unprocessable Entity", "error": True}

			case ['auth', 'connect']:
				if request.method != "POST":
					event.default_headers = event.default_headers | {'Allow': 'POST'}
					output = {"status": 405, "message": "Method Not Allowed", "error": True}

				elif 'Content-Type' in request.headers and request.headers['Content-Type'] == 'application/json':
					try:
						data = json.loads(request.data.decode("utf-8"))
					except:
						output = {"status": 422, "message": "Unprocessable Entity", "error": True}
					else:
						match data:
							case {'agent': username, 'code': code}:
								with Database() as db:
									query = db.get_user(str(username))
									output = {"status": 403, "message": "Unauthorized", "error": True}
									if query:
										user = query[0]
										two_factor = pyotp.TOTP(user[2])
										if two_factor.verify(str(code)):
											token = generate_string(32)
											db.edit_user_token(user[0], token, datetime.now())
											output = {"status": 200, "message": "OK", "error": False, "token": token}
							case _:
								output = {"status": 422, "message": "Unprocessable Entity", "error": True}
				else:
					output = {"status": 422, "message": "Unprocessable Entity", "error": True}


			case _:
				output = {"status": 404, "message": "Not Found", "error": True}
		jsonfied = json.dumps(output).encode()
		return Response.make(
			output["status"],
			output["message"],
			event.default_headers | {'Content-Type': 'application/json',
			'Content-Length': len(jsonfied)},
			jsonfied
		)

# Handle requests for the 'API'
import events
from structures import Response, Config, Database
import json
import pyotp
from datetime import datetime
from utils import parse_ibge, generate_string, union_dicts_with_regex, query_name

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
			# Query place path
			case ["ibge", "find"]:
				if request.method != "GET":
					event.default_headers = event.default_headers | {'Allow': 'POST'}
					output = {"status": 405, "message": "Method Not Allowed", "error": True}
				match event.request.query_string:
					case {'query': query, **data}:
						query = query_name(query, **data)
						output = {"status": 200, "message": "OK", "error": False, "results": len(query), "query": query}
			case ["places", "query"]:
				# Prevent unwanted http methods
				if request.method != "GET":
					event.default_headers = event.default_headers | {'Allow': 'POST'}
					output = {"status": 405, "message": "Method Not Allowed", "error": True}
				match event.request.query_string:
					case {'code': code}:
						with Database() as db:
							ibge_data = parse_ibge(code)
							code = int(code)

							query = db.get_place_data(f"{code}%" if code != 0 else "%", None)
							datas = []
							sources = []
							timestamps = []
							for entry in query:
								datas.append(json.loads(entry[1]))
								if entry[2] not in sources:
									sources.append(entry[2])
								if entry[3].timestamp() not in timestamps:
									timestamps.append(entry[3].timestamp())
							if ibge_data["type"] != "city":
								if str(code) not in config.fields["summable"]:
									regex = config.fields["summable"]['default']
								else:
									regex = config.fields["summable"][str(code)]
								datas = union_dicts_with_regex(regex, datas)
							else:
								datas = datas[0]

							output = {"status": 200,
								"message": "OK",
								"error": False,
								"results": len(query),
								"query": {
									"data": datas,
									"sources": sources,
									"ibge_code": code,
									"timestamps": timestamps,
									"geojson": f"https://servicodados.ibge.gov.br/api/v2/malhas/{code}?formato=application/vnd.geo+json",
									} | ibge_data
								}
					case _:
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

			case ["users", "all"]:
				if request.method != "GET":
					event.default_headers = event.default_headers | {'Allow': 'POST'}
					output = {"status": 405, "message": "Method Not Allowed", "error": True}

				match event.request.query_string:
					case {'token': token}:
						with Database() as db:
							output = {"status": 403, "message": "Unauthorized", "error": True}
							user = db.get_user_by_token(token)
							if user:
								query = db.get_app_users(uuid=identification)
								query_parsed = []

								for entry in query:
									query_parsed.append({
										"uuid": entry[0],
										"roles": json.loads(entry[1]),
										"permissions": json.loads(entry[2]),
										"tags": json.loads(entry[3]),
										"places": json.loads(entry[4]),
										"phone": entry[5],
									})

								output = {"status": 200, "message": "OK", "error": False, "results": len(query), "query": query_parsed}
					case _:
						output = {"status": 422, "message": "Unprocessable Entity", "error": True}

			case ["users", "new"]:
				print(request.data)
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
							case {'token': token, "phone": phone, "uuid": uuid}:
								with Database() as db:
									output = {"status": 403, "message": "Unauthorized", "error": True}
									user = db.get_user_by_token(token)
									if user:
										db.insert_app_user([], [], [], [], phone, uuid)

										output = {"status": 200, "message": "OK", "error": False}
							case _:
								output = {"status": 422, "message": "Unprocessable Entity", "error": True}
				else:
					output = {"status": 422, "message": "Unprocessable Entity", "error": True}

			case ["users", "uuid" | "phone", identification, "edit"]:
				method = event.path[1]
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
							case {'token': token, **data}:
								with Database() as db:
									output = {"status": 403, "message": "Unauthorized", "error": True}
									user = db.get_user_by_token(token)
									clean_data = {}
									for k, v in data.items():
										clean_data[k] = json.dumps(v)
									if user:
										if method == "uuid":
											db.edit_app_user(uuid=identification, **clean_data)
										elif method == "phone":
											db.edit_app_user(phone=identification, **clean_data)

										output = {"status": 200, "message": "OK", "error": False}
							case _:
								output = {"status": 422, "message": "Unprocessable Entity", "error": True}
				else:
					output = {"status": 422, "message": "Unprocessable Entity", "error": True}


			case ["users", "uuid" | "phone", identification]:
				method = event.path[1]
				if request.method != "GET":
					event.default_headers = event.default_headers | {'Allow': 'POST'}
					output = {"status": 405, "message": "Method Not Allowed", "error": True}

				match event.request.query_string:
					case {'token': token}:
						with Database() as db:
							output = {"status": 403, "message": "Unauthorized", "error": True}
							user = db.get_user_by_token(token)
							if user:
								if method == "uuid":
									query = db.get_app_user(uuid=identification)
								if method == "phone":
									query = db.get_app_user(phone=identification)
								query_parsed = []

								for entry in query:
									query_parsed.append({
										"uuid": entry[0],
										"roles": json.loads(entry[1]),
										"permissions": json.loads(entry[2]),
										"tags": json.loads(entry[3]),
										"places": json.loads(entry[4]),
										"phone": entry[5],
									})

								output = {"status": 200, "message": "OK", "error": False, "results": len(query), "query": query_parsed}
					case _:
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

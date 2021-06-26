# Handle requests for the 'API'
import events
from structures import Response, Config, Database
import json
from utils import parse_ibge

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
									ibge_data = parse_ibge(code)
									# Force the code into a Integer to prevent unwanted queries.
									query = db.get_place_data(int(code), float(timestamp))
									query_parsed = []

									for entry in query:
										query_parsed.append({
											"data": json.loads(entry[1]),
											"source": entry[2],
											"ibge_code": code,
											"timestamp": entry[3].timestamp(),
											"geojson": f"https://servicodados.ibge.gov.br/api/v2/malhas/{query[0]}?formato=application/vnd.geo+json"
										} | ibge_data)

									output = {"status": 200, "message": "OK", "error": False, "results": len(query), "query": query_parsed}
							case _:
								output = {"status": 422, "message": "Unprocessable Entity", "error": True}
				else:
					output = {"status": 422, "message": "Unprocessable Entity", "error": True}

			# Insert data into the database
			case ["places", "insert "]:
					output = {"status": 500, "message": "Not Implemented", "error": True}

			# Edit place data
			case ["places", "edit"]:
					output = {"status": 500, "message": "Not Implemented", "error": True}

			# Query the sources from the database
			case ["places", "sources"]:
					output = {"status": 500, "message": "Not Implemented", "error": True}
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

# Handle requests for the 'API'
import events
from structures import Response, Config, Database
import json

config = Config()

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
						with Database() as db:
							query = db.get_place_data(data['ibge'], data['timestamp'], True)
							query = list(query[0])
							query[-1] = query[-1].timestamp()
							output = {"status": 200, "message": "OK", "error": False, "query": query}
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

# Handle requests for the home page
import events
from structures import Response, Config
import os
import json

config = Config()
mime_types = json.load(open("mime_types.json"))
# Placeholder for the errors
errors = {
	404: b"",
	403: b"",
	500: b"",
	}


@events.add_handle("http_request")
def normal_http(event):
	# Check the request host
	request = event.request
	if "Host" in request.headers and request.headers["Host"] == config.scopes["home"]:
		path = os.path.join("assets/", request.path.removeprefix("/"))

		# Since I really don't wanna handle relative paths, I will just drop.
		if ".." in path:
			return Response.make(
				403,
				'Unauthorized',
				event.default_headers|{
					'Content-Type': 'text/html',
					'Content-Length': len(errors[403])
				},
				errors[403]
			)

		if os.path.exists(path):
			# If there is a path, and it is a file, return the file. Otherwise, if there isn't a file but
			# there is a path, return index.html. If there isn't a path nor a file, return an error.

			if os.path.isfile(path):
				filename = path
			elif os.path.exists(os.path.join(path, 'index.html')):
				filename = os.path.join(path, "index.html")
			else:
				return Response.make(
					404,
					'Not Found',
					event.default_headers|{
						'Content-Type': 'text/html',
						'Content-Length': len(errors[404])
					},
					errors[404]
				)
		else:
			# Path isn't a directory nor a file.
			return Response.make(
				404,
				'Not Found',
				event.default_headers|{
					'Content-Type': 'text/html',
					'Content-Length': len(errors[404])
				},
				errors[404]
			)
		# Read the file, get the MIME type and return everything
		data = open(filename, 'rb').read()
		prefix = os.path.basename(filename).split(".")[-1]
		if prefix in mime_types:
			event.default_headers['Content-Type'] = mime_types[prefix]
		return Response.make(
			200,
			'OK',
			event.default_headers|{
				'Content-Length': len(data),
			},
			data
		)

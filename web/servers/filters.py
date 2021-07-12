import events
from structures import Response, Config
from tasks import thread_function
import time
from urllib.parse import unquote
import socket

config = Config()

# Listen for http requests with a high priority to act as a 'filter'
@events.add_handle("http_request", priority=100)
def analizer_http(event):
	# Analyze the request and add more info to the event object.
	request = event.request
	path = [unquote(i) for i in request.path.split("/")[1:] if i]
	event.add_property(path=path)
	event.add_property(default_headers={"Server": "robosdocovid/1.0", "X-Server": 'robosdocovid/1.0', 'X-Backend': socket.gethostname(), "Access-Control-Allow-Origin": "*"})


# Listen for http requests with the lowest priority, to act as a fallback
@events.add_handle("http_request", priority=-1)
def fallback_http(event):
	# Default fallback handler
	request = event.request
	default_headers = {
		"Server": "robosdocovid/1.0",
		"X-Server": 'robosdocovid/1.0',
		'X-Backend': socket.gethostname(),
		"Access-Control-Allow-Origin": "*"
	}
	return Response.make(
		400,
		'Bad Request',
		default_headers,
		f"400 Bad Request.\nrobosdocovid/1.0\nHeaders: {request.headers}\nQuery string: {request.query_string}\nData: {request.data}".encode()
	)

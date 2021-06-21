# Handle requests for the 'API'
import events
from structures import Response, Config
import json

config = Config()

# Listen for http requests
@events.add_handle("http_request")
def api_http(event):
    request = event.request
    # Check the request host
    if "Host" in request.headers and request.headers["Host"] == config.scopes["api"]:
        # Placeholder response
        output = {"status": 200, "message": "OK", "error": False}
        jsonfied = json.dumps(output).encode()
        return Response.make(
            output["status"],
            output["message"],
            event.default_headers | {'Content-Type': 'application/json',
            'Content-Length': len(jsonfied)},
            jsonfied
        )

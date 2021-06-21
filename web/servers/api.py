import events
from structures import Response, Config
import json

config = Config()

@events.add_handle("http_request")
def api_http(event):
    request = event.request
    default_headers = event.default_headers
    if "Host" in request.headers and request.headers["Host"] == config.scopes["api"]:
        output = {"status": 200, "message": "OK", "error": False}
        jsonfied = json.dumps(output).encode()
        return Response.make(
            output["status"],
            output["message"],
            default_headers | {'Content-Type': 'application/json',
            'Content-Length': len(jsonfied)},
            jsonfied
        )

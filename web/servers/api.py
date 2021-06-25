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
        if event.path[0] == "places":
            # Query data from the database
            if event.path == ["places", "query"]:
                output = {"status": 500, "message": "Not Implemented", "error": True}

            # Insert data into the database
        elif event.path == ["places", "insert"]:
                output = {"status": 500, "message": "Not Implemented", "error": True}

            # Edit place data
        elif event.path == ["places", "edit"]:
                output = {"status": 500, "message": "Not Implemented", "error": True}

            # Query the sources from the database
        elif event.path == ["places", "sources"]:
                output = {"status": 500, "message": "Not Implemented", "error": True}

        jsonfied = json.dumps(output).encode()
        return Response.make(
            output["status"],
            output["message"],
            event.default_headers | {'Content-Type': 'application/json',
            'Content-Length': len(jsonfied)},
            jsonfied
        )

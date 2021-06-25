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
        if path[0] == "place":
            # Query data from the database
            if path == ["place", "query"]:
                output = {"status": 500, "message": "Not Implemented", "error": True}

            # Insert data into the database
            elif path == ["place", "insert"]:
                output = {"status": 500, "message": "Not Implemented", "error": True}

            # Edit place data
            elif path == ["place", "edit"]:
                output = {"status": 500, "message": "Not Implemented", "error": True}

            # Query the sources from the database
            elif path == ["place", "sources"]:
                output = {"status": 500, "message": "Not Implemented", "error": True}

        jsonfied = json.dumps(output).encode()
        return Response.make(
            output["status"],
            output["message"],
            event.default_headers | {'Content-Type': 'application/json',
            'Content-Length': len(jsonfied)},
            jsonfied
        )

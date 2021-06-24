import events
from structures import Response, Config

config = Config()

# Listen for http requests
@events.add_handle("http_request")
def whatsapp_http(event):
    request = event.request
    # Check the request host
    if "Host" in request.headers and request.headers["Host"] == config.scopes["whatsapp"]:
        return Response.make(
            301,
            'Moved Permanently',
            event.default_headers | {'Location': 'https://wa.me/+555499207163'},
            b""
        )

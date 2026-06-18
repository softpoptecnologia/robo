def application(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"PYTHON FUNCIONA - Passenger OK"]

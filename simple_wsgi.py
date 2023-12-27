from urllib.parse import parse_qsl

RESPONSE = b"OK\n"


def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    if environ['REQUEST_METHOD'] == 'POST':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0
        request_body = environ['wsgi.input'].read(request_body_size).decode('utf-8')
        print("(POST) Request body:\n", request_body)
    if environ['REQUEST_METHOD'] == 'GET':
        d = parse_qsl(environ['QUERY_STRING'])
        print("(GET) Parameters: ", *d)
    return [RESPONSE]


application = simple_app
#  gunicorn --bind 127.0.0.1:8081 -w 1 simple_wsgi:application

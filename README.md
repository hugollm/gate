# Gate

Gate is a python library that uses the Web Ser Gateway Interface (WSGI) to handle incoming HTTP requests. It's packed with features to help routing, handling, and extracting information from requests, as well as options to help writing appropriate responses.

[![Build Status](https://travis-ci.org/hugollm/gate.svg?branch=master)](https://travis-ci.org/hugollm/gate)
[![Coverage Status](https://coveralls.io/repos/github/hugollm/gate/badge.svg?branch=tmp)](https://coveralls.io/github/hugollm/gate?branch=tmp)


## Hello World

A simple hello world example with gate looks like:

```python
from gate import App, HtmlEndpoint


class HelloWorld(HtmlEndpoint):

    path = '/'

    def get(self, request, response):
        response.body = '<h1>Hello World</h1>'


app = App()
app.endpoint(HelloWorld)
```

Assuming you save the example in a file called `myapp.py`, running it is as simple as:

    gunicorn myapp:app

You should see the "Hello World" message in your browser on `localhost:8000`.


## App

The `App` object is responsible to hold a list of **endpoints** and providing a WSGI interface so web servers (like gunicorn) can route requests to it. Example:

```python
from gate import App
from . import endpoints


app = App()
app.endoint(endpoints.ListUsers)
app.endoint(endpoints.NewUser)
app.endoint(endpoints.UserDetails)
app.endpoint(endpoints.DeleteUser)
```

The above examples assumes you created an `endpoints.py` file with all those endpoints. To give an example of the routing, the `DeleteUser` endpoint in the example could look like this:

```python
from gate import HtmlEndpoint


class DeleteUser(HtmlEndpoint):

    path = '/users/:id/delete'

    def post(self, request, response):
        id = request.args['id']
        # delete from users where id = :id
```

The app, which is handling incoming requests, only routes to the `DeleteUser` if the request has a path that matches the pattern `/users/:id/delete` and if the HTTP method is `POST`. A single endpoint is allowed to handle more than one method. The allowed methods are:

* GET
* POST
* PUT
* PATCH
* DELETE
* HEAD
* OPTIONS


## Routing

Requests are routed by the `App` object, chosing and adequate endpoint to handle the request. Is the responsibility of the endpoint itself to tell if it can handle the request or not. It does that with the `path` attribute and an `http method`. Example:

```python
from gate import Endpoint


class ListUsers(Endpoint):

    path = '/users'

    def get(self, request, response):
        pass
```

The endpoint above will be able to handle `GET` requests to the `/users` path. If two endpoints are eligible to handle the same request, the app will raise an exception, as this is considered a programming mistake.

The `path` can also contain simple patterns with variables in it. Those variables are stored in the `request.args` attribute. Example:

```python
from gate import HtmlEndpoint


class Hello(HtmlEndpoint):

    path = '/hello/:name'

    def post(self, request, response):
        name = request.args['name']
        response.body = '<h1>Hello {}</h1>'.format(name)
```

If you need something more complex, you can also take it to the next level and define a regex in `path`. Example:

```python
class Static(Endpoint):

    path = r'^/static/(?P<path>.+)$'

    def get(self, request, response):
        path = request.args.get('path')
        if not os.path.isfile('static/' + path):
            raise response.not_found()
        response.file(path)
```

The above example will serve static files in the `static` directory. For regexes to work, you *must* to start `path` with the anchor `^`.


## Endpoints

There's three types of endpoints. A generic `Endpoint` and two subclasses `HtmlEndpoint` and `JsonEndpoint`.

The generic `Endpoint` is agnostic about the type of requests and responses you will be handling. It gives generic `Request` and `Response` objects to the handling method to manipulate. Example:

```python
from gate import Endpoint


class Hello(Endpoint):

    path = '/hello/:name'

    def get(self, request, response):
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.body = '<h1>Hello {}</h1>'.format(request.args['name'])
```

The `HtmlEndpoint` assumes you're dealing with a regular HTML application, accessing links, submitting forms, etc. It will give you `HtmlRequest` and `HtmlResponse` objects, which have special capabilities to parse and render information in these kind of application. Example:

```python
from gate import HtmlEndpoint


class Hello(HtmlEndpoint):

    path = '/hello/:name'

    def get(self, request, response):
        response.render('hello-world.html', {'name': request.args['name']})
```

The `JsonEndpoint` is specialized in JSON APIs, so it gives the handling method a `JsonRequest` and `JsonResponse` that are already prepared to handle JSON information. Example:

```python
from gate import JsonEndpoint


class Hello(JsonEndpoint):

    path = '/hello/:name'

    def get(self, request, response):
        response.json = {'hello': request.args['name']}
```

Endpoints can also define hooks to be executed **before** and **after** a request, as well as when an **exception** is raised. Example:

```python
from gate import JsonEndpoint


class AuthorizedEndpoint(JsonEndpoint):

    def before_request(self, request, response):
        request.session = get_session_from_request(request) # example function
        if not request.session:
            raise response.unauthorized()

    def after_request(self, request, response):
        log_request_and_response(request, response) # example function

    def on_exception(self, request, e):
        send_mail_with_exception(e) # example function
```

If `before_request` raises the response, the intended method from the endpoint (ex: get) never gets executed. The `after_request` method is always executed, even if `before_request` raises the response.

You can use inheritance to benefit from logic written in these hooks, making it easy to write protected endpoints.


## Requests

Request objects holds all the information from the user's requests. In a generic `Request`, the available information is:

```python
request.method # ex: POST
request.url # ex: https://mydomain.com/users/new
request.base_url # ex: https://mydomain.com
request.scheme # ex: https
request.host # ex: mydomain.com
request.path # ex: /users/new
request.query_string # the part after the ? mark. ex: page=1&oder=asc
request.query # parsed dict from the query string. ex: {'page': '1', 'order': 'asc'}
request.headers # headers of the request as a dict, with lowercased keys. ex: {'authorization': 'Bearer a73mad73klajg'}
request.cookies # cookies sent with the request, as a dict. ex: {'session_token': 'a73mad73klajg'}
request.messages # messages "flashed" by the response, that only lasts one request. ex: {'success': 'New user created'}
request.body # ex: b'Hello World'
request.ip # ex: 127.0.0.1
request.referer # ex: https://mydomain.com/users/list
request.user_agent # ex: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36
```

All the properties are lazily accessed, so they are only parsed if you need them.

`HtmlRequest` objects have some extra properties, to deal with HTML applications:

```python
request.form # submitted form data, as a dict. ex: {'email': 'john.doe@gmail.com', 'password': '123456'}
request.files # submitted files, as a dict. ex: {'photo': <UploadedFile>}
```

You can save an uploaded file like this:

```python
photo = request.files['photo']
photo.save('path/to/target.png')
```

`JsonRequest` objects have a `json` property:

```python
request.json # ex: {'hello': 'world'}
```


## Responses

The response object holds the information that will be sent back to the requesting user. In a generic `Response` object, the available information to be set is:

```python
response.headers # a dict of headers
response.body # bytes representing body of the response
```

Here's an example of a response being filled:

```python
response.headers['Content-Type'] = 'application/json; charset=utf-8'
response.body = json.dumps({'hello': 'world'}) # string gets converted to bytes automatically
```

The header `Content-Length` gets automatically filled for you.

`HtmlResponse` objects have a `render` method available, if the `App` has a *Jinja environment* set. Example:

```python
# in the app file
app.set_jinja_env({'packages.users': 'templates'})

# in the endpoint
request.render('hello.html', {'name': 'John'})
```

The above example will render the `hello.html` template, contained within the `templates` directory in the `packages.users` package. The rendered HTML will be filled in the `response.body` and the object will now have a `response.context` dictionary with `{'name': 'John'}`, which is useful for testing.

`JsonResponse` objects have a `json` method available as an easy way to set JSON content in the body. Example:

```python
response.json = {'name': 'John'}
```

The above example will fill `response.body` with the specified value as a JSON string. Note that this will only happen in the `JsonEndpoint` and just before sending the response back. So you won't be able to inspect `response.body` for the json content.

Response objects inherit from `BaseException` so you can `raise` them if you wish to end the request handling prematurely. This is very useful in authentication code, for instance. Example:

```python
session_token = request.cookies.get('session_token')
if not session_exists(session_token): # example function that would verify the validity of the session
    response.status = 401 # Unauthorized
    raise response
```

Or, more easily:

```python
raise response.unauthorized()
```

The above example feature one of the shortcut methods for aborting a response. It merely changes the response status and returns the response, so you can abort the request in one line. The available "abort" methods are:

```python
raise response.redirect(url_or_path)
raise response.not_found()
raise response.bad_request()
raise response.unauthorized()
raise response.forbidden()
```

There's also other methods to help you manipulate the resposne.

For instance, you can set a file to be served with:

```python
response.file('path/to/file.txt')
```

You can set a cookie with:

```python
response.set_cookie('session_id', 'b2kdi2keid8232') # sets a cookie 'session_id' with the value 'b2kdi2keid8232'
```

By default, set cookies are suitable for storing a session id (they have the attributes `HttpOnly` and `SameSite` set). You would only need to set an expiration date and the secure attribute when the request comes from https:

```python
tomorrow = datetime.now() + timedelta(days=1)
secure = request.scheme == 'https'
response.set_cookie('session_id', 'b2kdi2keid8232', expires=tomorrow, secure=secure)
```
Here's an example specifying all the attributes:

```python
tomorrow = datetime.now() + timedelta(days=1)
secure = request.scheme == 'https'
response.set_cookie('session_id', 'b2kdi2keid8232',
    expires=tomorrow,
    domain='mydomain.com',
    path='/dashboard/',
    secure=secure,
    http_only=True,
    same_site=True
)
```

To unset cookies, there's the `unset_cookie` method:

```python
response.unset_cookie('session_id')
```

If you defined the cookie with a `domain` or `path`, you'll need to inform those as well:

```python
response.unset_cookie('session_id', domain='mydomain.com', path='/dashboard/')
```

Using cookies, you can also set ephemeral messages to the next request. This is also known as *flash messages*:

```python
response.set_message('success', 'Profile information updated!')
```

This will be available at `request.messages` dictionary all the cookies will be automatically unset after you access it:

```python
request.messages['success'] # Profile information updated!
```


## Test Client

The `TestClient` exists so you can test your `App` as an user, making requests to it. Here's an example of a test:

```python
from unittest import TestCase
from gate import TestClient
from .myapp import app


class MyAppTestCase(TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_user_list(self):
        response = self.client.get('/users')
        assert response.status == 200
        assert response.json == {'users': ['John']}
```

The available methods in the `client` object are:

```python
client.get
client.post
client.put
client.patch
client.delete
client.head
client.options
```

You can also set query string, form data, json and files to the requests you make. Examples:

```python
client.get('/users', query={'page': 2, 'order': 'asc'})
client.post('/users/new', form={'email': 'john.doe@gmail.com'})
client.post('/users/new', json={'email': 'john.doe@gmail.com'})
client.post('/profile/photo', files={'photo': 'path/to/photo.jpg'})
```

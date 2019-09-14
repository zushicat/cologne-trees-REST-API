### Description
A very simple API using werkzeug and jsrpc
- when running docker container, in Dockerfile
CMD ["poetry", "run", "python", "-m", "api_cradle.api"]:
- starts service in src/api/_main_.py
- src/api/server.py: function "application" waits for jsrpc request
- on request: dispatcher delegates to src/fancy_stuff/_my_application.py
    - passing the attributes from "params" in request
    - a file in /data is read, getting the attribute "name"
    - both values are passed to do_something in _make_fancy_shit
        - returns json
    - returns returned json
- returns API response

No additional fancyness (such as logging, testing & stuff) implemented.

### Prerequisite
- install latest version of docker
- (maybe: docker --> preferences --> allowcate more memory)

### If you are using Visual Studio Code
- (If you are using OSX, install with brew cask install visual-studio-code)
- Useful Extensions: Python, REST Client
- If you want to use REST Client for easy http request (recommended):
    - Create file with extension .http (i.e. test_request.http)
    - Copy request text from below into file
    - "Send Request" will appear in file: click to request (tab with response will open)


### Start Docker Container
- Change into directory "cologne-treemap-api"
- Build and run docker container (with exposed port) named "cologne-treemap-api"
```
$docker build -t cologne-treemap-api .
```
simple run (the first port is the one to http request)
```
docker run -p 8080:80 cologne-treemap-api
```
OR run with restart after every saved code change
```
$docker run --rm -it -p 8080:80 -v $(pwd):/app cologne-treemap-api
```

(If port 8080 is already used by something else, just change the port to i.e. 8081)


### request
2 request methods implemented:

1) mytestrequest
with curl
```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"jsonrpc":"2.0","id":12345,"method":"mytestrequest","params":{}}' \
  http://localhost:8080
```
or with REST Client extension for Visual Studio (see below)
```
POST http://localhost:8080
Content-Type: application/json

{
    "jsonrpc": "2.0",
    "id": 12345,
    "method": "mytestrequest",
    "params": {}
}
```

returns
```
{
  "result": {
    "status": "YAY! API is running."
  },
  "id": 12345,
  "jsonrpc": "2.0"
}
```

2) cradle.fancyrequest
pass parameter "stuff" by http request
with curl
```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"jsonrpc":"2.0","id":12345,"method":"cradle.fancyrequest","params":{"stuff":"Foo Stuff"}}' \
  http://localhost:8080
```
or with REST Client extension for Visual Studio (see below)
```
POST http://localhost:8080
Content-Type: application/json

{
    "jsonrpc": "2.0",
    "id": 12345,
    "method": "cradle.fancyrequest",
    "params": {"stuff": "Foo Stuff"}
}
```

returns
```
{
  "result": {
    "status": "YAY!",
    "name from file": "Fuzzy Bear",
    "name from request": "Foo Stuff",
    "date": "2019-06-05 13:57:46.333072"
  },
  "id": 12345,
  "jsonrpc": "2.0"
}
```
### Description
A simple API to request different accumulations about city trees in Cologne, Germany. 
(Data is taken from the "Baumkataster" csv, published by Stadt Köln)

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


### Request endpoints
Use any http request to localhost with the running docker port (as in example: localhost:8080) and the endpoint you like to request

#### Example
You can request the endpoint 'geo.district_number.numbers' with or without parameters.
If given no parameters, all 9 districts are taken.

with curl
```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"jsonrpc":"2.0","id":12345,"method":"geo.district_number.numbers","params":{}}' \
  http://localhost:8080
```
or with REST Client extension for Visual Studio
```
POST http://localhost:8080
Content-Type: application/json

{
    "jsonrpc": "2.0",
    "id": 12345,
    "method": "geo.district_number.numbers",
    "params": {}
}
```

If you give (comma separated) city districts (1-9, see: https://de.wikipedia.org/wiki/Liste_der_Stadtbezirke_und_Stadtteile_K%C3%B6lns), those will be processed.

with curl
```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"jsonrpc":"2.0","id":12345,"method":"geo.district_number.numbers","params":{"district_numbers":"1,3"}}' \
  http://localhost:8080
```
or with REST Client extension for Visual Studio
```
POST http://localhost:8080
Content-Type: application/json

{
    "jsonrpc": "2.0",
    "id": 12345,
    "method": "geo.district_number.numbers",
    "params": {"district_numbers": "1,3"}
}
```

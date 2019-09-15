### Description
A simple API to request different accumulations about city trees in Cologne, Germany. 

(Underlaying data "trees_cologne_2017.jsonl.tar.gz" is processed from the "Baumkataster" csv file, published by Stadt Köln: https://offenedaten-koeln.de/dataset/baumkataster-koeln)

No additional fancyness (such as logging, testing & stuff) implemented.

### Prerequisite
- install latest version of docker
- (maybe: docker --> preferences --> allowcate more memory)


### Start Docker Container
- Change into directory "cologne-treemap-api"
- Build and run docker container i.e. named "cologne-treemap-api"
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

#### Implemented Endpoints
For now, following endpoints are implemented
- geo.district_number.numbers
- geo.suburb_number.number
- geo.suburb_number.genus.number
- tree.attr.age.overview

(See explanation below)

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


### If you are using Visual Studio Code
- (If you are using OSX, install with brew cask install visual-studio-code)
- Useful Extensions: Python, REST Client
- If you want to use REST Client for easy http request (recommended):
    - Create file with extension .http (i.e. test_request.http)
    - Copy request text from above into file
    - "Send Request" will appear in file: click to request (tab with response will open)



## Endpoints

For district and suburb numbers, see: https://de.wikipedia.org/wiki/Liste_der_Stadtbezirke_und_Stadtteile_K%C3%B6lns

#### geo.district_number.numbers
- "params": {}

Returns number of trees of all 9 districts, their suburbs and (if available) the neighbourhoods of these suburbs
- "params": {"district_numbers": "1,3"}

Returns number of trees of requested districts (here 1 and 3), their suburbs and (if available) the neighbourhoods of these suburbs

#### geo.suburb_number.number
- "params": {"suburb_number": "103"}

Returns number of trees of requested suburb and (if available) the neighbourhoods of this suburb

#### geo.suburb_number.genus.number
- "params": {"suburb_number": "103"}

Returns number of trees and number of (different) genus of requested suburb, as well as each genus with number of trees and german names

#### tree.attr.age.numbers
- "params": {"sort_by": "age"} OR "params": {"sort_by": "number"}

Returns age of trees and according number of planted trees, sorted either by age or by number

#### tree.attr.genus.numbers
- "params": {"sort_by": "genus"} OR "params": {"sort_by": "number"}

Returns genus of trees and according number of planted trees, sorted either by genus or by number
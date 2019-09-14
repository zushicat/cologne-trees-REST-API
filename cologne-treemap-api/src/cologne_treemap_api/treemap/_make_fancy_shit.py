import datetime
from typing import Any, Dict

def do_something(some_string_from_file: str, stuff_from_request: str) -> Dict[str, Any]:
    # do something and return json response
    try:
        response: Dict[str, str] = {
            "status": "YAY!",
            "name from file": some_string_from_file,
            "name from request": stuff_from_request,
            "date": f"{datetime.datetime.now()}"
        }
        return response
    except Exception as e:
        return {"status": f"NOOOO! Something went wrong. {e}"}

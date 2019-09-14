import json
import os
from typing import Any, Dict, List

from ._make_fancy_shit import do_something

DIRNAME = os.environ["DATA_LOCATION"]

def give_result(stuff: str) -> Dict[str, Any]:
    try:
        with open(f"{DIRNAME}/some_data.json") as f:
            data = json.load(f)
        return do_something(data.get("name"), stuff)
    except Exception as e:
        return {"status": f"ERROR! {e}"}

def test_request() -> Dict[str, str]:
    return {"status": "YAY! API is running."}
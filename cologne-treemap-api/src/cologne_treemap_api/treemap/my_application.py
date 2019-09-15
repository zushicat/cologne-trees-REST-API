import json
import os
from typing import Any, Dict, List

from ._make_fancy_shit import do_something
from ._by_geo import get_geo_numbers_per_district_number

DIRNAME = os.environ["DATA_LOCATION"]
TREEDATA = []

def load_tree_data() -> List[Dict[str, Any]]:
    global TREEDATA
    if len(TREEDATA) == 0:
        with open(f"{DIRNAME}/trees_cologne_2017.jsonl") as f:
            lines = f.read().split("\n")
        for line in lines:
            try:
                line = json.loads(line)
                TREEDATA.append(line)
            except Exception as e:
                pass


def geo_numbers_per_district_number(district_numbers: str = None) -> Dict[str, Any]:
    try:
        if len(district_numbers.strip()) == 0:
            district_numbers = None
        return get_geo_numbers_per_district_number(TREEDATA, district_numbers)
    except Exception as e:
        return {"status": f"ERROR! {e}"}


def give_result(stuff: str) -> Dict[str, Any]:
    try:
        with open(f"./data/some_data.json") as f:
            data = json.load(f)
        return do_something(data.get("name"), stuff)
    except Exception as e:
        return {"status": f"ERROR! {e}"}

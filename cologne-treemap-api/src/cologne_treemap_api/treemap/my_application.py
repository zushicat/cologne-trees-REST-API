import json
import os
from typing import Any, Dict, List

from ._by_geo import get_geo_numbers_by_district_number, get_geo_numbers_by_suburb_number, get_geo_genus_numbers_by_suburb_number
from ._by_tree_attr import get_tree_attr_age_overview

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


def geo_numbers_by_district_number(district_numbers: str = None) -> Dict[str, Any]:
    try:
        if district_numbers is not None:
            if len(district_numbers.strip()) == 0:
                district_numbers = None
        return get_geo_numbers_by_district_number(TREEDATA, district_numbers)
    except Exception as e:
        return {"status": f"ERROR! {e}"}

def geo_numbers_by_suburb_number(suburb_number: str = None) -> Dict[str, Any]:
    try:
        return get_geo_numbers_by_suburb_number(TREEDATA, suburb_number)
    except Exception as e:
        return {"status": f"ERROR! {e}"}

def geo_genus_numbers_by_suburb_number(suburb_number: str = None) -> Dict[str, Any]:
    try:
        return get_geo_genus_numbers_by_suburb_number(TREEDATA, suburb_number)
    except Exception as e:
        return {"status": f"ERROR! {e}"}

def tree_attr_age_overview(sort_by: str = None) -> Dict[str, Any]:
    try:
        if sort_by is None:
            sort_by = "age"
        if sort_by not in ["age", "number"]:
            return {"status": f"ERROR! 'sorted' needs to be 'age' or 'number'"}
        return get_tree_attr_age_overview(TREEDATA, sort_by)
    except Exception as e:
        return {"status": f"ERROR! {e}"}
    
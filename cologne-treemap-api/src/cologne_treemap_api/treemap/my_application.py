import json
import os
from typing import Any, Dict, List

from ._by_geo import (
    get_geo_numbers_by_district_number,
    get_geo_numbers_by_suburb_number,
    get_geo_genus_numbers_by_suburb_number,
    get_geo_age_by_suburb_number,
)
from ._by_tree_attr import (
    get_tree_attr_age_numbers, 
    get_tree_attr_genus_numbers, 
    get_tree_attr_name_german_numbers,
)

from ._by_tree_geo import (
    get_tree_geo_name_german_suburb_numbers,
)

DIRNAME = os.environ["DATA_LOCATION"]
TREEDATA = []


def load_tree_data() -> List[Dict[str, Any]]:
    global TREEDATA
    if len(TREEDATA) == 0:
        with open(f"{DIRNAME}/trees_cologne_merged.jsonl") as f:
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


def geo_age_by_suburb_number(
    suburb_number: str = None, sort_by: str = None
) -> Dict[str, Any]:
    try:
        if sort_by is None:
            sort_by = "age"
        if sort_by not in ["age", "number"]:
            return {"status": f"ERROR! 'sort_by' needs to be 'age' or 'number'"}
        return get_geo_age_by_suburb_number(TREEDATA, suburb_number, sort_by)
    except Exception as e:
        return {"status": f"ERROR! {e}"}


def tree_attr_age_numbers(sort_by: str = None) -> Dict[str, Any]:
    try:
        if sort_by is None:
            sort_by = "age"
        if sort_by not in ["age", "number"]:
            return {"status": f"ERROR! 'sort_by' needs to be 'age' or 'number'"}
        return get_tree_attr_age_numbers(TREEDATA, sort_by)
    except Exception as e:
        return {"status": f"ERROR! {e}"}


def tree_attr_genus_numbers(sort_by: str = None) -> Dict[str, Any]:
    try:
        if sort_by is None:
            sort_by = "genus"
        if sort_by not in ["genus", "number"]:
            return {"status": f"ERROR! 'sort_by' needs to be 'genus' or 'number'"}
        return get_tree_attr_genus_numbers(TREEDATA, sort_by)
    except Exception as e:
        return {"status": f"ERROR! {e}"}

def tree_attr_name_german_numbers(sort_by: str = None) -> Dict[str, Any]:
    try:
        if sort_by is None:
            sort_by = "genus"
        if sort_by not in ["name", "number"]:
            return {"status": f"ERROR! 'sort_by' needs to be 'name' or 'number'"}
        return get_tree_attr_name_german_numbers(TREEDATA, sort_by)
    except Exception as e:
        return {"status": f"ERROR! {e}"}

def tree_geo_name_german_suburb_numbers(
    name: str = None
) -> Dict[str, Any]:
    try:
       return get_tree_geo_name_german_suburb_numbers(TREEDATA, name)
    except Exception as e:
       return {"status": f"ERROR! {e}"}

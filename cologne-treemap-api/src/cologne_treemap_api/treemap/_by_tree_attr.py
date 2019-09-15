import json
import datetime

from typing import Any, Dict, List

def get_tree_attr_age_overview(treemap: List[Dict[str, Any]], sort_by: str) -> Dict[str, Any]:
    current_year = int(datetime.datetime.today().year)
    numbers_by_year = {}
    for tree in treemap:
        year_sprout = int(tree["tree_info"]["year_sprout"])
        age = current_year - year_sprout
        
        if numbers_by_year.get(age) is None:
            numbers_by_year[age] = 0
        numbers_by_year[age] += 1
    
    if sort_by == "age":
        numbers_by_year = {k: numbers_by_year[k] for k in sorted(numbers_by_year)}
    if sort_by == "number":
        numbers_by_year = {k: numbers_by_year[k] for k in sorted(numbers_by_year, key=numbers_by_year.get, reverse=True)}

    return numbers_by_year
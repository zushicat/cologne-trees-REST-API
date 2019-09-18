import json
import datetime

from typing import Any, Dict, List

# ***
# initially load global
SUBURBNUMBERS = {}
with open(f"./data/suburb_number.json") as f:
    SUBURBNUMBERS = json.load(f)


def get_tree_geo_name_german_suburb_numbers(
    treemap: List[Dict[str, Any]], name: str = None
) -> Dict[str, Any]:
    # ***
    # process requested suburb
    numbers_by_name = {"name_german": name, "suburbs": {}}
    for tree in treemap:
        try:
            names_german = tree["tree_info"]["name_german"]
            suburb = tree["geo_info"]["suburb"]
            
            name_found = False
            for name_german in names_german:
                if name_german == name:
                    name_found = True
                    break
            
            if name_found is False:
                continue

            if suburb is None:  # about 80 trees: they do have lat, lng
                continue

            if numbers_by_name["suburbs"].get(suburb) is None:
                numbers_by_name["suburbs"][suburb] = 0
            numbers_by_name["suburbs"][suburb] += 1
        except Exception as e:
            print(e)
            continue
    return numbers_by_name

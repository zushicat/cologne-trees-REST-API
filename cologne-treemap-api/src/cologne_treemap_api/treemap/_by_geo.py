import json

from typing import Any, Dict, List

def get_geo_overall_numbers_per_district(treemap: List[Dict[str, Any]]) -> Dict[str, Any]:
    # print(json.dumps(treemap[0], indent=2, ensure_ascii=False))
    tmp = {}
    for tree in treemap:
        try:
            district = tree["geo_info"]["city_district"]
            
            if district is None:
                # debug
                # print(tree["base_info"]["district_number"], tree["geo_info"]["lat"], tree["geo_info"]["lng"])
                continue
            
            if tmp.get(district) is None:
                tmp[district] = 0
            tmp[district] += 1
        except Exception:
            continue
    return tmp
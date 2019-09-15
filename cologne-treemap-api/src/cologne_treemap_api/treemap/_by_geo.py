import json

from typing import Any, Dict, List

def get_geo_numbers_per_district_number(treemap: List[Dict[str, Any]], district_numbers: str = None) -> Dict[str, Any]:
    # ***
    # check requested district; if None: take all
    requested_districts = []
    if district_numbers is None:
        for i in range(1,10):
            requested_districts.append(str(i))
    else:
        district_numbers = district_numbers.strip()
        # if district_numbers.find(",") == -1 and len(district_numbers) > 1:
        #     return {"status": "ERROR! Insert numbers from 1-9, comma-separated if more than 1 district"}

        requested_districts = [x.strip() for x in district_numbers.split(",") if x.strip().isdigit()]
    
    # ***
    # process trees of requested (or all) districts
    numbers_by_district = {}
    numbers_district_in_district_numbers = {}

    # ***
    # suburbs that belong officially to district number
    with open(f"./data/suburb_number.json") as f:
        suburb_numbers = json.load(f)
    for district_number, suburbs in suburb_numbers.items():
        suburb_numbers[district_number] = suburbs.values()
        suburb_numbers[district_number] = [x.replace("/", " ").replace("-", " ") for x in suburb_numbers[district_number]]

    for tree in treemap:
        try:
            district_number = tree["base_info"]["district_number"]

            if district_number not in requested_districts:
                continue
            
            district = tree["geo_info"]["city_district"]
            suburb = tree["geo_info"]["suburb"]
            neighbourhood = tree["geo_info"]["neighbourhood"]

            if district is None:  # about 80 trees: they do have lat, lng
                # debug
                # print(tree["base_info"]["district_number"], tree["geo_info"]["lat"], tree["geo_info"]["lng"])
                continue

            # ***
            # ignore suburbs that do not belong officially to district
            if suburb.replace("/", " ").replace("-", " ") not in suburb_numbers[district_number]:
                print(suburb)
                continue

            # ***
            # since there are some peripheral districts in district number:
            # collect numbers to filter out max later
            if numbers_district_in_district_numbers.get(district_number) is None:
                numbers_district_in_district_numbers[district_number] = {}
            if numbers_district_in_district_numbers[district_number].get(district) is None:
                numbers_district_in_district_numbers[district_number][district] = 0
            numbers_district_in_district_numbers[district_number][district] += 1

            if numbers_by_district.get(district_number) is None:
                numbers_by_district[district_number] = {
                    "number_of_trees": 0,
                    "districts": {}
                }

            numbers_by_district[district_number]["number_of_trees"] += 1

            if district is not None:
                if numbers_by_district[district_number]["districts"].get(district) is None:
                    numbers_by_district[district_number]["districts"][district] = {
                        "district_name": district,
                        "number_of_trees": 0,
                        "suburbs": {}
                    }

                numbers_by_district[district_number]["districts"][district]["number_of_trees"] += 1

                if suburb is not None:
                    if numbers_by_district[district_number]["districts"][district]["suburbs"].get(suburb) is None:
                        numbers_by_district[district_number]["districts"][district]["suburbs"][suburb] = {
                            "number_of_trees": 0,
                            "neighbourhoods": {}
                        }

                    numbers_by_district[district_number]["districts"][district]["suburbs"][suburb]["number_of_trees"] += 1

                    if neighbourhood is not None:
                        if numbers_by_district[district_number]["districts"][district]["suburbs"][suburb]["neighbourhoods"].get(neighbourhood) is None:
                            numbers_by_district[district_number]["districts"][district]["suburbs"][suburb]["neighbourhoods"][neighbourhood] = {
                                "number_of_trees": 0,
                            }

                        numbers_by_district[district_number]["districts"][district]["suburbs"][suburb]["neighbourhoods"][neighbourhood]["number_of_trees"] += 1
        except Exception as e:
            continue
    
    # ***
    # get the 'real' district of district number, skip the rest
    sorted_district_numbers = list(numbers_district_in_district_numbers.keys())
    sorted_district_numbers.sort()
    tmp = {}
    for district_number in sorted_district_numbers:
        district_vals = numbers_district_in_district_numbers[district_number]
        max_district = max(district_vals, key=district_vals.get)
        tmp[district_number] = numbers_by_district[district_number]["districts"][max_district]
    numbers_by_district = tmp

    return numbers_by_district
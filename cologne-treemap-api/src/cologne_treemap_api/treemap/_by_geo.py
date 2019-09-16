import datetime
import json

from typing import Any, Dict, List

# ***
# initially load global
SUBURBNUMBERS = {}
with open(f"./data/suburb_number.json") as f:
    SUBURBNUMBERS = json.load(f)


def get_geo_numbers_by_district_number(
    treemap: List[Dict[str, Any]], district_numbers: str = None
) -> Dict[str, Any]:
    # ***
    # check requested district; if None: take all
    requested_districts = []
    if district_numbers is None:
        for i in range(1, 10):
            requested_districts.append(str(i))
    else:
        district_numbers = district_numbers.strip()
        if district_numbers.find(",") == -1 and len(district_numbers) > 1:
            return {
                "status": "ERROR! Insert numbers from 1-9, comma-separated if more than 1 district"
            }

        requested_districts = [
            x.strip() for x in district_numbers.split(",") if x.strip().isdigit()
        ]

    # ***
    # process trees of requested (or all) districts
    numbers_by_district = {}
    numbers_district_in_district_numbers = {}

    # ***
    # suburbs that belong officially to district number
    # with open(f"./data/suburb_number.json") as f:
    #     suburb_numbers = json.load(f)
    suburb_numbers = {}
    for district_number, suburbs in SUBURBNUMBERS.items():
        suburb_numbers[district_number] = suburbs.values()
        suburb_numbers[district_number] = [
            x.replace("/", " ").replace("-", " ")
            for x in suburb_numbers[district_number]
        ]

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
            if (
                suburb.replace("/", " ").replace("-", " ")
                not in suburb_numbers[district_number]
            ):
                continue

            # ***
            # since there are some peripheral districts in district number:
            # collect numbers to filter out max later
            if numbers_district_in_district_numbers.get(district_number) is None:
                numbers_district_in_district_numbers[district_number] = {}
            if (
                numbers_district_in_district_numbers[district_number].get(district)
                is None
            ):
                numbers_district_in_district_numbers[district_number][district] = 0
            numbers_district_in_district_numbers[district_number][district] += 1

            if numbers_by_district.get(district_number) is None:
                numbers_by_district[district_number] = {
                    "number_of_trees": 0,
                    "districts": {},
                }

            numbers_by_district[district_number]["number_of_trees"] += 1

            if district is not None:
                if (
                    numbers_by_district[district_number]["districts"].get(district)
                    is None
                ):
                    numbers_by_district[district_number]["districts"][district] = {
                        "district_name": district,
                        "number_of_trees": 0,
                        "suburbs": {},
                    }

                numbers_by_district[district_number]["districts"][district][
                    "number_of_trees"
                ] += 1

                if suburb is not None:
                    if (
                        numbers_by_district[district_number]["districts"][district][
                            "suburbs"
                        ].get(suburb)
                        is None
                    ):
                        numbers_by_district[district_number]["districts"][district][
                            "suburbs"
                        ][suburb] = {"number_of_trees": 0, "neighbourhoods": {}}

                    numbers_by_district[district_number]["districts"][district][
                        "suburbs"
                    ][suburb]["number_of_trees"] += 1

                    if neighbourhood is not None:
                        if (
                            numbers_by_district[district_number]["districts"][district][
                                "suburbs"
                            ][suburb]["neighbourhoods"].get(neighbourhood)
                            is None
                        ):
                            numbers_by_district[district_number]["districts"][district][
                                "suburbs"
                            ][suburb]["neighbourhoods"][neighbourhood] = {
                                "number_of_trees": 0
                            }

                        numbers_by_district[district_number]["districts"][district][
                            "suburbs"
                        ][suburb]["neighbourhoods"][neighbourhood][
                            "number_of_trees"
                        ] += 1
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
        tmp[district_number] = numbers_by_district[district_number]["districts"][
            max_district
        ]
    numbers_by_district = tmp

    return numbers_by_district


def get_geo_numbers_by_suburb_number(
    treemap: List[Dict[str, Any]], suburb_number: str = None
) -> Dict[str, Any]:
    # ***
    # get suburb_numbers
    suburb_numbers = {}
    for district_number, suburb_vals in SUBURBNUMBERS.items():
        for s_number, suburb in suburb_vals.items():
            suburb_numbers[s_number] = suburb

    # ***
    # only valid suburb number
    if suburb_number not in suburb_numbers.keys():
        return {"status": f"ERROR! Suburb number {suburb_number} does not exist"}

    requested_suburb_name = (
        suburb_numbers[suburb_number].replace("/", " ").replace("-", " ")
    )

    # ***
    # process requested suburb
    numbers_by_suburb = {}
    for tree in treemap:
        try:
            district_number = tree["base_info"]["district_number"]

            district = tree["geo_info"]["city_district"]
            suburb = tree["geo_info"]["suburb"]
            neighbourhood = tree["geo_info"]["neighbourhood"]

            if district is None:  # about 80 trees: they do have lat, lng
                continue

            # ***
            # ignore suburbs that do not belong officially to district
            if suburb.replace("/", " ").replace("-", " ") != requested_suburb_name:
                continue

            if numbers_by_suburb.get(suburb_number) is None:
                numbers_by_suburb[suburb_number] = {
                    "suburb_name": suburb,
                    "number_of_trees": 0,
                    "neighbourhoods": {},
                }

            numbers_by_suburb[suburb_number]["number_of_trees"] += 1

            if neighbourhood is not None:
                if (
                    numbers_by_suburb[suburb_number]["neighbourhoods"].get(
                        neighbourhood
                    )
                    is None
                ):
                    numbers_by_suburb[suburb_number]["neighbourhoods"][
                        neighbourhood
                    ] = {"number_of_trees": 0}

                numbers_by_suburb[suburb_number]["neighbourhoods"][neighbourhood][
                    "number_of_trees"
                ] += 1

        except Exception as e:
            continue

    return numbers_by_suburb


def get_geo_genus_numbers_by_suburb_number(
    treemap: List[Dict[str, Any]], suburb_number: str = None
) -> Dict[str, Any]:
    # ***
    # get suburb_numbers
    suburb_numbers = {}
    for district_number, suburb_vals in SUBURBNUMBERS.items():
        for s_number, suburb in suburb_vals.items():
            suburb_numbers[s_number] = suburb

    # ***
    # only valid suburb number
    if suburb_number not in suburb_numbers.keys():
        return {"status": f"ERROR! Suburb number {suburb_number} does not exist"}

    requested_suburb_name = (
        suburb_numbers[suburb_number].replace("/", " ").replace("-", " ")
    )

    # ***
    # process requested suburb
    numbers_by_suburb = {}
    for tree in treemap:
        try:
            district_number = tree["base_info"]["district_number"]

            district = tree["geo_info"]["city_district"]
            suburb = tree["geo_info"]["suburb"]
            neighbourhood = tree["geo_info"]["neighbourhood"]

            genus = tree["tree_info"]["genus"]
            if genus in ["", "unbekannt"]:
                genus = "unknown"
            name_german = tree["tree_info"]["name_german"]

            if district is None:  # about 80 trees: they do have lat, lng
                continue

            # ***
            # ignore suburbs that do not belong officially to district
            if suburb.replace("/", " ").replace("-", " ") != requested_suburb_name:
                continue

            if numbers_by_suburb.get(suburb_number) is None:
                numbers_by_suburb[suburb_number] = {
                    "suburb_name": suburb,
                    "number_of_trees": 0,
                    "number_of_genus": 0,
                    "genus": {},
                }

            numbers_by_suburb[suburb_number]["number_of_trees"] += 1

            if genus is not None:
                if numbers_by_suburb[suburb_number]["genus"].get(genus) is None:
                    numbers_by_suburb[suburb_number]["genus"][genus] = {
                        "number_of_trees": 0,
                        "german_names": [],
                    }

                numbers_by_suburb[suburb_number]["genus"][genus]["number_of_trees"] += 1
                if name_german is not None:
                    for n in name_german:
                        if len(n) == 0:
                            continue
                        if (
                            n
                            not in numbers_by_suburb[suburb_number]["genus"][genus][
                                "german_names"
                            ]
                        ):
                            numbers_by_suburb[suburb_number]["genus"][genus][
                                "german_names"
                            ].append(n)

        except Exception as e:
            continue

    numbers_by_suburb[suburb_number]["number_of_genus"] = len(
        numbers_by_suburb[suburb_number]["genus"].keys()
    )

    return numbers_by_suburb


def get_geo_age_by_suburb_number(
    treemap: List[Dict[str, Any]], suburb_number: str, sort_by: str
) -> Dict[str, Any]:
    current_year = int(datetime.datetime.today().year)
    # ***
    # get suburb_numbers
    suburb_numbers = {}
    for district_number, suburb_vals in SUBURBNUMBERS.items():
        for s_number, suburb in suburb_vals.items():
            suburb_numbers[s_number] = suburb

    # ***
    # only valid suburb number
    if suburb_number not in suburb_numbers.keys():
        return {"status": f"ERROR! Suburb number {suburb_number} does not exist"}

    requested_suburb_name = (
        suburb_numbers[suburb_number].replace("/", " ").replace("-", " ")
    )

    # ***
    # process requested suburb
    numbers_by_suburb = {}
    for tree in treemap:
        try:
            district_number = tree["base_info"]["district_number"]

            district = tree["geo_info"]["city_district"]
            suburb = tree["geo_info"]["suburb"]
            neighbourhood = tree["geo_info"]["neighbourhood"]

            genus = tree["tree_info"]["genus"]
            if genus in ["", "unbekannt"]:
                genus = "unknown"
            name_german = tree["tree_info"]["name_german"]

            year_sprout = tree["tree_info"]["year_sprout"]
            age = current_year - year_sprout

            if district is None:  # about 80 trees: they do have lat, lng
                continue

            # ***
            # ignore suburbs that do not belong officially to district
            if suburb.replace("/", " ").replace("-", " ") != requested_suburb_name:
                continue

            if numbers_by_suburb.get(suburb_number) is None:
                numbers_by_suburb[suburb_number] = {"suburb_name": suburb, "age": {}}

            if numbers_by_suburb[suburb_number]["age"].get(age) is None:
                numbers_by_suburb[suburb_number]["age"][age] = 0

            numbers_by_suburb[suburb_number]["age"][age] += 1

        except Exception as e:
            continue

    for suburb_number, suburb_vals in numbers_by_suburb.items():
        if sort_by == "age":
            numbers_by_suburb[suburb_number]["age"] = {
                k: numbers_by_suburb[suburb_number]["age"][k]
                for k in sorted(numbers_by_suburb[suburb_number]["age"])
            }
        if sort_by == "number":
            numbers_by_suburb[suburb_number]["age"] = {
                k: numbers_by_suburb[suburb_number]["age"][k]
                for k in sorted(
                    numbers_by_suburb[suburb_number]["age"],
                    key=numbers_by_suburb[suburb_number]["age"].get,
                    reverse=True,
                )
            }

    return numbers_by_suburb

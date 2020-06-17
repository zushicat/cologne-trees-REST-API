'''
After creating base data set trees_cologne_2017.jsonl:
Try to find duplicates by lat/lng data
    - try to minimize complexity by first sorting into district/suburb buckets
    - save neighbouring trees in list with id pais and distance in meter
----
Incoming lines:
{
  "tree_id": "e2281aa9-5bcd-474d-96eb-f64144c596f0",
  "base_info_completeness": 1,
  "tree_taxonomy_completeness": 0.75,
  "tree_info_completeness": 1,
  "base_info": {
    "maintenance_object": 1009,
    "object_type": "street/court (plaza)",
    "district_number": 1,
    "district_name": "Innenstadt",
    "tree_nr": "MG58"
  },
  "geo_info": {
    "lat": 50.91734830820297,
    "lng": 6.964993084894649,
    "neighbourhood": null,
    "suburb": "Neustadt/Süd",
    "city_district": "Innenstadt"
  },
  "tree_taxonomy": {
    "genus": "Robinia",
    "species": "pseudoacacia",
    "type": null,
    "name_german": [
      "Scheinakazie"
    ]
  },
  "tree_info": {
    "height": 9,
    "treetop_radius": 4,
    "bole_radius": 15,
    "year_sprout": 2007,
    "age_in_2017": 10,
    "age_in_2020": 13,
    "age_group_2020": 1
  }
}{
  "tree_id": "e2281aa9-5bcd-474d-96eb-f64144c596f0",
  "base_info_completeness": 1,
  "tree_taxonomy_completeness": 0.75,
  "tree_info_completeness": 1,
  "base_info": {
    "maintenance_object": 1009,
    "object_type": "street/court (plaza)",
    "district_number": 1,
    "district_name": "Innenstadt",
    "tree_nr": "MG58"
  },
  "geo_info": {
    "lat": 50.91734830820297,
    "lng": 6.964993084894649,
    "neighbourhood": null,
    "suburb": "Neustadt/Süd",
    "city_district": "Innenstadt"
  },
  "tree_taxonomy": {
    "genus": "Robinia",
    "species": "pseudoacacia",
    "type": null,
    "name_german": [
      "Scheinakazie"
    ]
  },
  "tree_info": {
    "height": 9,
    "treetop_radius": 4,
    "bole_radius": 15,
    "year_sprout": 2007,
    "age_in_2017": 10,
    "age_in_2020": 13,
    "age_group_2020": 1
  }
}
'''
import json
from math import radians, cos, sin, asin, sqrt
from typing import Any, Dict, List


def _haversine(lon1, lat1, lon2, lat2):
    """
    https://stackoverflow.com/a/4913653
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    distance_in_km = c * r
    distance_in_m = round(((c * r)*1000), 2)
    return distance_in_m


def calculate_distance(suburb_trees):
    close_pairs = []
    for i, tree_1 in enumerate(suburb_trees):
        #print(i)
        for j, tree_2 in enumerate(suburb_trees):
            if j <= i:
                continue

            distance = _haversine(tree_1["lng"], tree_1["lat"], tree_2["lng"], tree_2["lat"])

            if distance < 3:
                #print(f'   {j} - {distance}')
                close_pairs.append([tree_1["id"], tree_2["id"], distance])
        #print()
    return close_pairs


if __name__ == "__main__":
    with open("raw_trees_cologne_2017.jsonl") as f:
        in_lines = f.read().split("\n")

    trees_by_district_suburb: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    trees_short_list = []

    for i, in_line in enumerate(in_lines):
        print(i)
        try:
            line = json.loads(in_line)
        except:
            continue

        district: str = line["geo_info"]["city_district"]
        suburb: str = line["geo_info"]["suburb"]

        tree_id: str = line["tree_id"]
        lat: float = round(line["geo_info"]["lat"], 5)  # 11m precision
        lng: float = round(line["geo_info"]["lng"], 5)  # 11m precision

        if trees_by_district_suburb.get(district) is None:
            trees_by_district_suburb[district] = {}
        if trees_by_district_suburb[district].get(suburb) is None:
            trees_by_district_suburb[district][suburb] = []
        trees_by_district_suburb[district][suburb].append({
            "id": tree_id,
            "lat": lat,
            "lng": lng
        })

    # print(json.dumps(trees_by_district_suburb, indent=2))

    close_pairs = []
    for district, suburbs in trees_by_district_suburb.items():
        print(f"---- {district} ----")
        for suburb, trees in suburbs.items():
            close_pairs_in_suburb = calculate_distance(trees)
            close_pairs += close_pairs_in_suburb
            print(f"   {suburb} {len(trees)} {len(close_pairs_in_suburb)}")
    
    #print(close_pairs)
    print(len(close_pairs))
    with open("close_tree_pairs_distance.jsonl", "w") as f:
        for line in close_pairs:
            f.write(f"{json.dumps(line, ensure_ascii=False)}\n")
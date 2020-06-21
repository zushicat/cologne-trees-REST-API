import csv
import datetime
import uuid
import json

import utm  

# ***
# https://github.com/Turbo87/utm
# utm usage:
# lat, lng = utm.to_latlon(359814, 5645658, 32, 'U')
# print(lat, lng)


with open("20200610_Baumbestand_Koeln.csv") as f:
    reader = csv.DictReader(f, delimiter=",")
    rows = list(reader)

with open("lat_lng_districts.json") as f:
    lat_lng_districts = json.load(f)

with open("cologne_districts_by_id.json") as f:
    cologne_districts_by_id = json.load(f)

with open("object_types.json") as f:
    object_types = json.load(f)

with open("cologne_districts_by_id.json") as f:
    district_id_name = json.load(f)


# ***
# re-arrange
district_name_id = {v: k for k, v in district_id_name.items()}


count_no_age = 0
count_err = 0
count = 0
i = 0
lines = []
for row in rows:
    print(i)
    i += 1
    try:
        x = int(row["x_koordina"])
        y = int(row["y_koordina"])

        # ***
        # ignore if geo data is not valid / missing
        lat, lng = (None, None)
        try:
            lat, lng = utm.to_latlon(x, y, 32, 'U')
        except Exception as e:
            # print(f"lat lng ERR ----> {e}")
            continue
        if lat is None or lng is None:
            continue

        height = None
        treetop_radius = None
        bole_radius = None
        try:
            if int(row["H_HE"]) > 0:
                height = int(row["H_HE"])
        except:
            pass
        try:
            if int(row["KRONE"]) > 0:
                treetop_radius = int(row["KRONE"])
        except:
            pass
        try:
            if int(row["STAMMBIS"]) > 0:
                bole_radius = int(row["STAMMBIS"])
        except:
            pass

        object_type = None
        try:
            object_type = object_types["en"].get(row["objekttyp"])
            if object_type in ["NN", "Unbekannt", "unknown", "?"]:
                object_type = None
        except:
            pass
        
        year_planting = None
        
        neighbourhood = None
        suburb = None
        city_district = None

        try:
            if int(row["PFLANZJAH"]) > 0:
                year_planting = int(row["PFLANZJAH"])
        except:
            pass

        if year_planting is None:
            count_no_age += 1

        try:
            lat_lng = f'{"{0:.3f}".format(lat)}_{"{0:.3f}".format(lng)}'
            if lat_lng_districts.get(lat_lng) is not None:
                neighbourhood = lat_lng_districts[lat_lng]["neighbourhood"]
                suburb = lat_lng_districts[lat_lng]["suburb"]
                city_district = lat_lng_districts[lat_lng]["city_district"]
        except:
            pass

        district_number = None
        district_name = None

        # ***
        # Substitute missing district in data
        # ! check StandortNr
        if district_name_id.get(city_district) is not None:
            district_number = district_name_id[city_district]
            district_name = city_district


        taxo_genus = row["Gattung"] if len(row["Gattung"]) > 0 and row["Gattung"] not in ["unbekannt", "?"] else None
        taxo_species = row["Art"] if len(row["Art"]) > 0 and row["Art"] not in ["unbekannt", "?"] else None
        taxo_type = row["Sorte"] if len(row["Sorte"]) > 0 and row["Sorte"] not in ["unbekannt", "?"] else None
        taxo_name_german = [x.strip() for x in row["DeutscherN"].split(",")] if len(row["DeutscherN"]) > 0 and row["DeutscherN"] not in ["unbekannt", "?"] else None

        tree_id = str(uuid.uuid4()) 
        
        
        tmp = {
            "tree_id": tree_id,
            "dataset_completeness": 0.0,
            "base_info_completeness": 0.0,
            "tree_taxonomy_completeness": 0.0,
            "tree_measures_completeness": 0.0,
            "tree_age_completeness": 0.0,
            "base_info":
            {
                "object_type": object_type,
                "district_number": district_number,
                "district_name": district_name,
                "tree_nr": row["baumnr"] if len(row["baumnr"]) > 0 else None,
            },
            "geo_info":
            {
                "utm_x": x,
                "utm_y": y,
                "lat": lat,
                "lng": lng,
                "neighbourhood": neighbourhood,
                "suburb": suburb,
                "city_district": city_district,
            },
            "tree_taxonomy":
            {
                "genus": taxo_genus,
                "species": taxo_species,
                "type": taxo_type,
                "name_german": taxo_name_german,
            },
            "tree_measures":
            {
                "height": height,
                "treetop_radius": treetop_radius,
                "bole_radius": bole_radius
            },
            "tree_age":
            {
                "year_planting": year_planting
                # "year_sprout": year_sprout,
                # "age_in_2017": age_in_2017,
                # "age_in_2020": age_in_2020,
                # "age_group_2020": age_group,
            }
        }

        # ********
        # % completeness in "base_info", tree_taxonomy and "tree_info"
        # and overall completeness in "dataset_completeness"
        tmp_completeness_collected = 0.0
        tmp_completeness_attr = ["base_info", "tree_taxonomy", "tree_measures", "tree_age"]
        for k in tmp_completeness_attr:
            collected_types_perc = round(len([type(x).__name__ for x in tmp[k].values() if type(x).__name__ != "NoneType"]) / len(tmp[k].values()), 2)  # i.e. ["NoneType", "str", "int", "str"]
            tmp[f"{k}_completeness"] = collected_types_perc
            tmp_completeness_collected += collected_types_perc

        try:
            tmp_completeness_collected = round(tmp_completeness_collected / len(tmp_completeness_attr), 2)
        except:
            pass
        tmp["dataset_completeness"] = tmp_completeness_collected

        lines.append(tmp)

        count += 1
    except Exception as e:
       count_err += 1
    

print(f"count_err {count_err}")
print(f"count_no_age: {count_no_age}")
print(f"count: {count}")

with open("raw_trees_cologne_2020.jsonl", "w") as f:
    for line in lines:
        f.write(f"{json.dumps(line, ensure_ascii=False)}\n")
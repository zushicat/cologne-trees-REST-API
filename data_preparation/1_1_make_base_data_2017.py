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


with open("Bestand_Einzelbaeume_Koeln_0.csv") as f:
    reader = csv.DictReader(f, delimiter=";")
    rows = list(reader)

with open("lat_lng_districts.json") as f:
    lat_lng_districts = json.load(f)

with open("cologne_districts_by_id.json") as f:
    cologne_districts_by_id = json.load(f)

with open("object_types.json") as f:
    object_types = json.load(f)


# ***
# re-arrange
district_name_id = {v: k for k, v in cologne_districts_by_id.items()}


count_err = 0
i = 0
lines = []
for row in rows:
    print(i)
    i += 1
    try:
        x = int(row["X_Koordina"])
        y = int(row["Y_Koordina"])

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
            if int(row["HöHE"]) > 0:
                height = int(row["HöHE"])
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
            object_type = object_types["en"].get(row["Objekttyp"])
            if object_type in ["NN", "Unbekannt", "unknown"]:
                object_type = None
        except:
            pass
        
        age_in_2017 = None
        age_in_2020 = None
        year_sprout = None
        age_group = None

        neighbourhood = None
        suburb = None
        city_district = None

        try:
            if int(row["AlterSchätzung"]) > 0:
                age_in_2017 = int(row["AlterSchätzung"])
                year_sprout = 2017 - age_in_2017
        except:
            pass

        try:
            age_in_2020 = 2020 - year_sprout
            for j, group in enumerate([(1,18), (18,26), (26,41), (41,1000)]):
                lower_boundary = group[0]
                upper_boundary = group[1]
                if age_in_2020 >= lower_boundary and age_in_2020 < upper_boundary:
                    age_group = j
                    break
        except:
            pass
        
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

        try:
            district_number = int(row["Bezirk"]) if int(row["Bezirk"]) != 0 else None
            district_name = cologne_districts_by_id[str(district_number)]
        except:
            pass

        # ***
        # Substitute missing district in data
        if district_number is None:
            if district_name_id.get(city_district) is not None:
                district_number = district_name_id[city_district]
                district_name = city_district

        taxo_genus = row["Gattung"] if len(row["Gattung"]) > 0 and row["Gattung"] != "unbekannt" else None
        taxo_species = row["Art"] if len(row["Art"]) > 0 and row["Art"] != "unbekannt" else None
        taxo_type = row["Sorte"] if len(row["Sorte"]) > 0 and row["Sorte"] != "unbekannt" else None
        taxo_name_german = [x.strip() for x in row["DeutscherN"].split(",")] if len(row["DeutscherN"]) > 0 and row["DeutscherN"] != "unbekannt" else None

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
                "maintenance_object": int(row["PFLEGEOBJE"]) if int(row["PFLEGEOBJE"]) != 0 else None,
                "object_type": object_type,
                "district_number": district_number,
                "district_name": district_name,
                "tree_nr": row["Baum-Nr."] if len(row["Baum-Nr."]) > 0 else None,
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
                "bole_radius": bole_radius,
            },
            "tree_age":
            {
                "year_sprout": year_sprout,
                "age_in_2017": age_in_2017,
                "age_in_2020": age_in_2020,
                "age_group_2020": age_group,
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
    except Exception as e:
        count_err += 1
    

print(f"count_err {count_err}")
print(f"num lines {len(lines)}")

with open("raw_trees_cologne_2017.jsonl", "w") as f:
    for line in lines:
        f.write(f"{json.dumps(line, ensure_ascii=False)}\n")
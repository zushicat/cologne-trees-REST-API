import csv
import datetime
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

today = datetime.datetime.now()

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
            print(f"lat lng ERR ----> {e}")
            continue
        if lat is None or lng is None:
            continue

        height = None
        treetop_radius = None
        bole_radius = None
        try:
            height = int(row["HöHE"])
        except:
            pass
        try:
            treetop_radius = int(row["KRONE"])
        except:
            pass
        try:
            bole_radius = int(row["STAMMBIS"])
        except:
            pass
        
        age_in_2017 = None
        year_sprout = None

        neighbourhood = None
        suburb = None
        city_district = None

        try:
            age_in_2017 = int(row["AlterSchätzung"])
            year_sprout = 2017 - age_in_2017
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

        tmp = {
            "tree_id": f'{row["PFLEGEOBJE"]}_{row["Objekttyp"]}_{row["Bezirk"]}_{row["Baum-Nr."]}',
            "base_info":
            {
                "maintenance_object": row["PFLEGEOBJE"],
                "object_type": row["Objekttyp"],
                "district_number": row["Bezirk"],
                "tree_nr": row["Baum-Nr."],
            },
            "geo_info":
            {
                "lat": lat,
                "lng": lng,
                "geo_x": x,
                "geo_y": y,
                "neighbourhood": neighbourhood,
                "suburb": suburb,
                "city_district": city_district,
            },
            "tree_info":
            {
                "genus": row["Gattung"],
                "species": row["Art"],
                "type": row["Sorte"],
                "name_german": [x.strip() for x in row["DeutscherN"].split(",")],
                "height": height,
                "treetop_radius": treetop_radius,
                "bole_radius": bole_radius,
                "year_sprout": year_sprout,
                "age_in_2017": age_in_2017,
            }
        }

        lines.append(tmp)
    except Exception as e:
        count_err += 1


print(f"count_err {count_err}")
print(f"num lines {len(lines)}")
with open("trees_cologne_2017.jsonl", "w") as f:
    for line in lines:
        f.write(f"{json.dumps(line, ensure_ascii=False)}\n")
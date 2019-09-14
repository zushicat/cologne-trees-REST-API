# cologne-treemap: Data preparation

- Use latitude, longitude geo data
- Skip trees without valid geo data
- Add "neighbourhood", "suburb" and "city_district"

Use:
- Bestand_Einzelbaeume_Koeln_0.csv ("Baumkataster" published by Stadt Köln, link see bottom of page)
- lat_lng_districts.json

Saved in: 
- trees_cologne_2017.jsonl (json line file with 116276 lines == trees) 

Generates one object per tree
```
{
    "tree_id": concat <STR> of columns row["PFLEGEOBJE"]_row["Objekttyp"]_row["Bezirk"]_row["Baum-Nr."]}"
    "base_info":
    {
        "maintenance_object": from column "PFLEGEOBJE"
        "object_type": from column "Objekttyp"
        "district_number": from column "Bezirk" (ref. numbers 1-9: https://de.wikipedia.org/wiki/Liste_der_Stadtbezirke_und_Stadtteile_K%C3%B6lns)
        "tree_nr": from column "Baum-Nr."
    },
    "geo_info":
    {
        "lat": lat from "X_Koordina"
        "lng": lng from "Y_Koordina"
        "geo_x": "X_Koordina"
        "geo_y": "Y_Koordina"
        "neighbourhood": neighbourhood,
        "suburb": suburb,
        "city_district": city_district,
    },
    "tree_info":
    {
        "genus": from column "Gattung"
        "species": from column "Art"
        "type": from column "Sorte"
        "name_german": from column "DeutscherN"
        "height": from column "HöHE"
        "treetop_radius": from column "KRONE"
        "bole_radius": from column "STAMMBIS"
        "year_sprout": when the tree came into existence (based on "AlterSchätzung")
        "age_in_2017": from column "AlterSchätzung"
    }
}
```

Based on the csv dataset "Baumkataster", published by Stadt Köln (latest version of 2017-04-19):
https://offenedaten-koeln.de/dataset/baumkataster-koeln


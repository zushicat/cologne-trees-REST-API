# cologne-treemap: Data preparation

- Use latitude, longitude geo data
- Skip trees without valid geo data
- Add "neighbourhood", "suburb" and "city_district"

Use:
- Bestand_Einzelbaeume_Koeln_0.csv ("Baumkataster" published by Stadt Köln, link see bottom of page)
- lat_lng_districts.json

Saved in: 
- trees_cologne_2017.jsonl (json line file with 115836 lines == trees) 

Default value if no data for attribute available: **null**

Generates one object per tree
```
{
  "tree_id": generated uuid id,
  "base_info_completeness": number of non-None "base_info" values,
  "tree_info_completeness": number of non-None "tree_info" values,
  "tree_taxonomy_completeness": number of non-None "tree_taxonomy" values,
  "base_info": {
    "maintenance_object": from column "PFLEGEOBJE"
        "object_type": from column "Objekttyp"
        "district_number": from column "Bezirk" (ref. numbers 1-9: https://de.wikipedia.org/wiki/Liste_der_Stadtbezirke_und_Stadtteile_K%C3%B6lns)
        "tree_nr": from column "Baum-Nr."
  },
  "geo_info": {
    "lat": lat from "X_Koordina"
    "lng": lng from "Y_Koordina"
    "neighbourhood": matched neighbourhood from geo data
    "suburb": matched suburb from geo data
    "city_district": matched city_district from geo data
  },
  "tree_taxonomy": {
    "genus": from column "Gattung"
    "species": from column "Art"
    "type": from column "Sorte"
    "name_german": from column "DeutscherN" (array, splitted by ",)
  },
  "tree_info": {
    "height": from column "HöHE"
    "treetop_radius": from column "KRONE"
    "bole_radius": from column "STAMMBIS"
    "year_sprout": when the tree came into existence (based on "AlterSchätzung")
    "age_in_2017": from column "AlterSchätzung"
    "age_in_2020": calculated from from column "AlterSchätzung"
    "age_group_2020": calculated from from column "AlterSchätzung"
  }
}
```

## Example
```
{
  "tree_id": "98280430-558b-4c74-bd2e-dabab15fc60c",
  "base_info_completeness": 5,
  "tree_taxonomy_completeness": 3,
  "tree_info_completeness": 7,
  "base_info": {
    "maintenance_object": 900,
    "object_type": "street/court (plaza)",
    "district_number": 9,
    "district_name": "Mülheim",
    "tree_nr": "21U"
  },
  "geo_info": {
    "lat": 50.95045949638997,
    "lng": 7.00963487885997,
    "neighbourhood": null,
    "suburb": "Buchforst",
    "city_district": "Mülheim"
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
    "treetop_radius": 5,
    "bole_radius": 20,
    "year_sprout": 2007,
    "age_in_2017": 10,
    "age_in_2020": 13,
    "age_group_2020": 1
  }
}
```

Based on the csv dataset "Baumkataster", published by Stadt Köln (latest version of 2017-04-19):
https://offenedaten-koeln.de/dataset/baumkataster-koeln


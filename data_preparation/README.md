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
  "dataset_completeness": overall completeness (derived from the other completeness values),
  "base_info_completeness": number of non-None "base_info" values (in %),
  "tree_info_completeness": number of non-None "tree_info" values (in %),
  "tree_taxonomy_completeness": number of non-None "tree_taxonomy" values (in %),
  "base_info": {
      "maintenance_object": from column "PFLEGEOBJE"
      "object_type": from column "Objekttyp"
      "district_number": from column "Bezirk" (ref. numbers 1-9: https://de.wikipedia.org/wiki/Liste_der_Stadtbezirke_und_Stadtteile_K%C3%B6lns)
      "tree_nr": from column "Baum-Nr."
  },
  "geo_info": {
      "lat": lat from column "X_Koordina"
      "lng": lng from column "Y_Koordina"
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
  "tree_id": "fa229709-c5fc-4807-b974-3cc478ee98e4",
  "dataset_completeness": 0.92,
  "base_info_completeness": 1,
  "tree_taxonomy_completeness": 0.75,
  "tree_info_completeness": 1,
  "base_info": {
    "maintenance_object": 1472,
    "object_type": "street/court (plaza)",
    "district_number": 1,
    "district_name": "Innenstadt",
    "tree_nr": "MU2"
  },
  "geo_info": {
    "lat": 50.91850507655438,
    "lng": 6.9606741725917605,
    "neighbourhood": null,
    "suburb": "Neustadt/Süd",
    "city_district": "Innenstadt"
  },
  "tree_taxonomy": {
    "genus": "Tilia",
    "species": "cordata",
    "type": null,
    "name_german": [
      "Winterlinde"
    ]
  },
  "tree_info": {
    "height": 10,
    "treetop_radius": 7,
    "bole_radius": 25,
    "year_sprout": 1982,
    "age_in_2017": 35,
    "age_in_2020": 38,
    "age_group_2020": 2
  }
}
```

Based on the csv dataset "Baumkataster", published by Stadt Köln (latest version of 2017-04-19):
https://offenedaten-koeln.de/dataset/baumkataster-koeln


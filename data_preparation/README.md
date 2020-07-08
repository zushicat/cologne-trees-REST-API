# cologne-treemap: Data preparation

Based on the csv dataset "Baumkataster", published by Stadt Köln (both version as of 2017 and 2020):
https://offenedaten-koeln.de/dataset/baumkataster-koeln


Creates an enriched dataset trees in Cologne, Germany and generates one object per tree.    
The default value is **null** if no data for an attribute is available.


## Example without predictions
```
{
  "tree_id": "3103908d-197c-4c6c-bfae-d844085e93cd",
  "dataset_completeness": 0.94,
  "base_info_completeness": 1,
  "tree_taxonomy_completeness": 0.75,
  "tree_measures_completeness": 1,
  "tree_age_completeness": 1,
  "base_info": {
    "maintenance_object": 1637,
    "object_type": "street/court (plaza)",
    "district_number": 8,
    "district_name": "Kalk",
    "tree_nr": "26P"
  },
  "geo_info": {
    "utm_x": 359797,
    "utm_y": 5645630,
    "lat": 50.94522243410281,
    "lng": 7.004206827902432,
    "neighbourhood": null,
    "suburb": "Kalk",
    "city_district": "Kalk"
  },
  "tree_taxonomy": {
    "genus": "Robinia",
    "species": "pseudoacacia",
    "type": null,
    "name_german": [
      "Scheinakazie"
    ]
  },
  "tree_measures": {
    "height": 10,
    "treetop_radius": 10,
    "bole_radius": 45
  },
  "tree_age": {
    "year_sprout": 1992,
    "age_in_2017": 25,
    "age_in_2020": 28,
    "age_group_2020": 1,
    "year_planting": 2002
  },
  "found_in_dataset": {
    "2017": true,
    "2020": true
  },
  "num_neighbours_radius_50": 23,
  "predictions": null
}
```

### Predictions
If age group (and/or genus) is not available, the 1 of 2 methods is used to try to predict these missing values:
- 1) if bole radius and genus are available: by age group classifier from these features
- 2) if not: assumption by clustered trees (with similar features) within a 50m radius around the current tree

The probability is saved, so it's up to you to decide which threshold for consideration should be applied.

#### Example for 1)
```
{
  "tree_id": "951e8825-8d8c-4919-a4c2-c4453270e6a5",
  "dataset_completeness": 0.62,
  "base_info_completeness": 1,
  "tree_taxonomy_completeness": 0.5,
  "tree_measures_completeness": 1,
  "tree_age_completeness": 0,
  "base_info": {
    "object_type": "building/school/dormitory (home) building",
    "district_number": "9",
    "district_name": "Mülheim",
    "tree_nr": "6G"
  },
  "geo_info": {
    "utm_x": 358240,
    "utm_y": 5652009,
    "lat": 51.002169444266436,
    "lng": 6.979570594535556,
    "neighbourhood": null,
    "suburb": "Flittard",
    "city_district": "Mülheim"
  },
  "tree_taxonomy": {
    "genus": "Sorbus",
    "species": null,
    "type": null,
    "name_german": [
      "Eberesche",
      "Mehlbeere",
      "Vogelbeerbaum"
    ]
  },
  "tree_measures": {
    "height": 6,
    "treetop_radius": 1,
    "bole_radius": 5
  },
  "tree_age": {
    "year_planting": null,
    "age_in_2017": null,
    "age_in_2020": null,
    "age_group_2020": null,
    "year_sprout": null
  },
  "found_in_dataset": {
    "2017": true,
    "2020": true
  },
  "num_neighbours_radius_50": 0,
  "predictions": {
    "age_prediction": {
      "age_group_2020": 0,
      "probabiliy": 0.66
    },
    "by_radius_prediction": null
  }
}
```

#### Example for 2)
```
{
  "tree_id": "c910be76-8e0f-4963-8f2c-782fb91138ff",
  "dataset_completeness": 0.25,
  "base_info_completeness": 1,
  "tree_taxonomy_completeness": 0,
  "tree_measures_completeness": 0,
  "tree_age_completeness": 0,
  "base_info": {
    "object_type": "building/school/dormitory (home) building",
    "district_number": "5",
    "district_name": "Nippes",
    "tree_nr": "P5"
  },
  "geo_info": {
    "utm_x": 354805,
    "utm_y": 5647947,
    "lat": 50.96480903330279,
    "lng": 6.932269973457881,
    "neighbourhood": null,
    "suburb": "Bilderstöckchen",
    "city_district": "Nippes"
  },
  "tree_taxonomy": {
    "genus": null,
    "species": null,
    "type": null,
    "name_german": null
  },
  "tree_measures": {
    "height": null,
    "treetop_radius": null,
    "bole_radius": null
  },
  "tree_age": {
    "year_planting": null,
    "age_in_2017": null,
    "age_in_2020": null,
    "age_group_2020": null,
    "year_sprout": null
  },
  "found_in_dataset": {
    "2017": false,
    "2020": true
  },
  "num_neighbours_radius_50": 23,
  "predictions": {
    "age_prediction": null,
    "by_radius_prediction": {
      "age_group_2020": 2,
      "genus": "Acer",
      "probabiliy": 0.03
    }
  }
}
```
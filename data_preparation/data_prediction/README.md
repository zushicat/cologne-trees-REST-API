## data prediction
There is a significant number of trees (with geo data) without any or some information about either of the following features:
- measures (height, bole_radius, treetop_radius)
- age (age_in_2017 and derived year_sprout, age_in_2020)
- taxonomy (genus, type, name_german)    

Hence this attempt to fill in the gaps if possible.    

Things to find out:
- measure
    - age, taxonomy
- age
    - measure, taxonomy
- taxonomy
    - measure, age
    - check neighbour trees in radius


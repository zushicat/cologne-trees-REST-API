import json
import tarfile
from typing import Any, Dict, List

with open("close_tree_pairs_distance.jsonl") as f:
    close_neighbour_pair_list: List[str] = f.read().split("\n")

with open("data_prediction/data/all_tree_pairs_distance.jsonl") as f:
    all_neighbour_pair_list: List[str] = f.read().split("\n")

with open("raw_trees_cologne_merged.jsonl") as f:
    tree_list: List[str] = f.read().split("\n")

# with open("cologne_districts_by_id.json") as f:
#     district_id_name: Dict[str, str] = json.load(f)



# # ***
# # re-arrange
# district_name_id = {v: k for k, v in district_id_name.items()}

# ***
# 
trees_by_id: Dict[str, Any] = {}
for line in tree_list:
    try:
        tree_data: Dict[str, Any] = json.loads(line)
    except:
        continue
    # # ***
    # # check for base_info.district_number, base_info.district_name
    # # if None: substitute by derived id and value from geo_info.city_district
    # if tree_data["base_info"]["district_number"] is None:
    #     pred_district_name = tree_data["geo_info"]["city_district"]
    #     if district_name_id.get(pred_district_name) is not None:
    #         tree_data["base_info"]["district_number"] = district_name_id[pred_district_name]
    #         tree_data["base_info"]["district_name"] = pred_district_name

    # ***
    # add new object for number of neighbours
    # neighbours list {<id>: {<id>:<distance>}} saved in separate file
    tree_data["num_neighbours_radius_50"]: int = 0

    trees_by_id[tree_data["tree_id"]] = tree_data

# **********************************
# delete trees which are TOO CLOSE
# **********************************
delete_ids = []

for line in close_neighbour_pair_list:
    try:
        pair: List[Any] = json.loads(line)
    except:
        continue
    id_1: str = pair[0]
    id_2: str = pair[1]
    distance: float = pair[2]

    tree_data_1 = trees_by_id[id_1]
    tree_data_2 = trees_by_id[id_2]

    # ***
    # TODO: merge information .found_in_dataset
    if tree_data_1["base_info_completeness"] > tree_data_2["base_info_completeness"]:
        if tree_data_2["tree_measures_completeness"] == 0 and tree_data_2["tree_age_completeness"] == 0:
            delete_ids.append(id_2)
    else:
        if tree_data_1["base_info_completeness"] < tree_data_2["base_info_completeness"]:
            if tree_data_1["tree_measures_completeness"] == 0 and tree_data_1["tree_age_completeness"] == 0:
                delete_ids.append(id_1)

# remove identified ids
for del_id in set(delete_ids):
    del trees_by_id[del_id]


# **********************************
# process neighbour trees and save in separate file by id
# **********************************
neighbours_by_id: Dict[str, Dict[str, float]] = {}
for line in all_neighbour_pair_list:
    try:
        pair: List[Any] = json.loads(line)
    except:
        continue
    current_tree_id: str = pair[0]
    current_neighbour_tree_id: str = pair[1]
    distance: float = pair[2]

    # skip if one of both is not existing anymore
    if trees_by_id.get(current_tree_id) is None:
        continue
    if trees_by_id.get(current_neighbour_tree_id) is None:
        continue

    if neighbours_by_id.get(current_tree_id) is None:
        neighbours_by_id[current_tree_id]: Dict[str, float] = {}
    neighbours_by_id[current_tree_id][current_neighbour_tree_id] = distance
    

for idx, vals in neighbours_by_id.items():
    trees_by_id[idx]["num_neighbours_radius_50"] = len(vals.keys())


# write cleaned file
with open("trees_cologne_merged.jsonl", "w") as f:  # overwrite old data
    for line in trees_by_id.values():
        f.write(f"{json.dumps(line, ensure_ascii=False)}\n")

# write compressed tar.gz file in docker data directory
tar = tarfile.open("../cologne-treemap-api/data/trees_cologne_merged.jsonl.tar.gz","w:gz")
tar.add("trees_cologne_merged.jsonl")

# write radius neighbour file
with open("neighbours_by_id.json", "w") as f:
    f.write(json.dumps(neighbours_by_id, indent=2))
    
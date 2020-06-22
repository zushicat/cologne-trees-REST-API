import json
import tarfile
from typing import Any, Dict, List

with open("close_tree_pairs_distance.jsonl") as f:
    close_neighbour_pair_list: List[str] = f.read().split("\n")

with open("data_prediction/data/all_tree_pairs_distance.jsonl") as f:
    all_neighbour_pair_list: List[str] = f.read().split("\n")

with open("raw_trees_cologne_merged.jsonl") as f:
    tree_list: List[str] = f.read().split("\n")


# ***
# 
trees_by_id: Dict[str, Any] = {}
for line in tree_list:
    try:
        tree_data: Dict[str, Any] = json.loads(line)
    except:
        continue
    
    # ***
    # add new object for number of neighbours
    # neighbours list {<id>: {<id>:<distance>}} saved in separate file
    tree_data["num_neighbours_radius_50"]: int = 0

    trees_by_id[tree_data["tree_id"]] = tree_data

# **********************************
# delete trees which are TOO CLOSE <= 2m
# **********************************
delete_ids: List[str] = []
replace_trees_by_id: Dict[str, Any] = {}

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
    # merge
    keep_tree = None
    skip_tree = None
    if tree_data_1["dataset_completeness"] >= tree_data_2["dataset_completeness"]:
        keep_tree = tree_data_1
        skip_tree = tree_data_2
    else:
        keep_tree = tree_data_2
        skip_tree = tree_data_1
    
    # use obj. with higher completeness
    for attr_key in ["base_info", "tree_taxonomy", "tree_measures", "tree_age"]:
        if keep_tree[f"{attr_key}_completeness"] < skip_tree[f"{attr_key}_completeness"]:
            keep_tree[attr_key] = skip_tree[attr_key]
    
    # keep dataset occurance information; use simple bool operation
    for dataset in ["2017", "2020"]:
        keep_tree["found_in_dataset"][dataset] = keep_tree["found_in_dataset"][dataset] and skip_tree["found_in_dataset"][dataset]

    # done: add to delete list and add to replacement list
    delete_ids.append(skip_tree["tree_id"])
    replace_trees_by_id[keep_tree["tree_id"]] = keep_tree



# now 5839 / previously 1268

# remove identified ids
for del_id in set(delete_ids):
    del trees_by_id[del_id]


# **********************************
# neighbors per tree
# get / count neighbour trees per id and save in separate file by id
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
    

for idx, vals in neighbours_by_id.items():  # corresponding to trees_by_id
    if replace_trees_by_id.get(idx) is not None:  # new info from merge (see: above)
        trees_by_id[idx] = replace_trees_by_id[idx]
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
    
'''
Create reduced dataset i.e. for web-applications (where data first is being downloaded by client)
'''
import json
import tarfile
from typing import Any, Dict, List, Optional


DATADIR = "../cologne-treemap-api/data"


def _get_compressed_tree_data() -> List[str]:
    '''
    Load compressed file.
    '''
    tar = tarfile.open(f"{DATADIR}/trees_cologne_merged.jsonl.tar.gz")
    f = tar.extractfile("trees_cologne_merged.jsonl")
    lines = f.read().decode().split("\n")
    
    return lines


def _get_reduced_tree_data(tree_data: Dict[str, Any]) -> Dict[str, Any]: # <-- check typing for .geojson datapoint return value
    new_tree_data: Dict[str, Optional[str, int, float]] = {
        "tree_id": tree_data["tree_id"],
        "district_number": tree_data["base_info"]["district_number"],
        "lat": tree_data["geo_info"]["lat"],
        "lng": tree_data["geo_info"]["lng"],
        "genus": None,
        "in_dataset_2020": tree_data["found_in_dataset"]["2020"],
        "age_group": tree_data["tree_age"]["age_group_2020"]  # check if none -> from prediction
    }

    if new_tree_data["age_group"] is None:
        if tree_data["predictions"] is not None:
            if tree_data["predictions"].get("age_prediction") is not None:
                new_tree_data["age_group"] = tree_data["predictions"]["age_prediction"]["age_group_2020"]
            else:
                if tree_data["predictions"].get("by_radius_prediction") is not None:
                    new_tree_data["age_group"] = tree_data["predictions"]["by_radius_prediction"]["age_group_2020"]

    
    if tree_data["tree_taxonomy"]["genus"] is not None:
        new_tree_data["genus"] = tree_data["tree_taxonomy"]["genus"]
    else:
        try: 
            new_tree_data["genus"] = tree_data["predictions"]["by_radius_prediction"]["genus"]
        except:
            pass


    return new_tree_data


if __name__ == "__main__":
    tree_data_str = _get_compressed_tree_data()
    
    new_tree_data_list: List[Dict[str, Any]] = []
    collected_age_groups = {}
    for line in tree_data_str:
        try:
            tree_data = json.loads(line)
        except:
            continue
    
        # ***
        # 
        new_tree_data = _get_reduced_tree_data(tree_data)

        # if new_tree_data["age_group"] is None:
        #     print("xxxx", new_tree_data["tree_id"])
            #break
        
        if collected_age_groups.get(new_tree_data["age_group"]) is None:
            collected_age_groups[new_tree_data["age_group"]] = 0
        collected_age_groups[new_tree_data["age_group"]] += 1
        
        new_tree_data_list.append(new_tree_data)

    print(collected_age_groups)
    
    # ***
    # create reduced file
    with open("trees_cologne_merged_reduced.jsonl", "w") as f:  # overwrite old data
        for line in new_tree_data_list:
            f.write(f"{json.dumps(line, ensure_ascii=False)}\n")

    # ***
    # write compressed tar.gz file
    tar = tarfile.open(f"{DATADIR}/trees_cologne_merged_reduced.jsonl.tar.gz", "w:gz")
    tar.add("trees_cologne_merged_reduced.jsonl")
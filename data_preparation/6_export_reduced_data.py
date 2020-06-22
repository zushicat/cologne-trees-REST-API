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
        "genus": tree_data["tree_taxonomy"]["genus"],
        "in_dataset_2020": tree_data["found_in_dataset"]["2020"],
        "age_group": None  # from data or prediction
    }

    if tree_data["tree_age"]["age_group_2020"] is not None:
        new_tree_data["age_group"] = tree_data["tree_age"]["age_group_2020"]
    else:
        try: 
            new_tree_data["age_group"] = tree_data["predictions"]["age_prediction"]["age_group_2020"]
        except:
            pass

    return new_tree_data


if __name__ == "__main__":
    tree_data_str = _get_compressed_tree_data()
    
    new_tree_data_list: List[Dict[str, Any]] = []
    for line in tree_data_str:
        try:
            tree_data = json.loads(line)
        except:
            continue
    
        # ***
        # 
        new_tree_data = _get_reduced_tree_data(tree_data)
        new_tree_data_list.append(new_tree_data)

    # ***
    # create reduced file
    with open("trees_cologne_merged_reduced.jsonl", "w") as f:  # overwrite old data
        for line in new_tree_data_list:
            f.write(f"{json.dumps(line, ensure_ascii=False)}\n")

    # ***
    # write compressed tar.gz file
    tar = tarfile.open(f"{DATADIR}/trees_cologne_merged_reduced.jsonl.tar.gz", "w:gz")
    tar.add("trees_cologne_merged_reduced.jsonl")
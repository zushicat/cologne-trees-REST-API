'''
Create csv file from tree data .tar.gz file with necessary features
'''
import json
import tarfile
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


def _get_compressed_data() -> List[str]:
    '''
    Load compressed file.
    '''
    tar = tarfile.open("../../cologne-treemap-api/data/trees_cologne_merged.jsonl.tar.gz") #, mode='rb:gz')
    f = tar.extractfile("trees_cologne_merged.jsonl")
    lines = f.read().decode().split("\n")
    
    return lines


def _get_age_group_incl_age_prediction(tree_data: Dict[str, Any]) -> Optional[int]:
    age_group = tree["tree_age"]["age_group_2020"]
    if age_group is None:
        try:
            age_group = tree_data["predictions"]["age_prediction"]["age_group_2020"]
        except:
            pass
    return age_group


if __name__ == "__main__":
    tree_data_str = _get_compressed_data()

    lines: List[Dict[str, Any]] = []
    for line in tree_data_str:
        try:
            tree = json.loads(line)
        except:
            continue
    
        # if tree["base_info"]["district_number"] != 1:  # DEBUG
        #     continue

        try:
            tmp = {
                "id": tree["tree_id"],
                "height": tree["tree_measures"]["height"],
                "treetop_radius": tree["tree_measures"]["treetop_radius"],
                "bole_radius": tree["tree_measures"]["bole_radius"],
                "age": tree["tree_age"]["year_sprout"],
                "age_group_2020": _get_age_group_incl_age_prediction(tree),
                "genus": tree["tree_taxonomy"]["genus"],
                "type": tree["tree_taxonomy"]["type"],
                "name_german": "|".join(tree["tree_taxonomy"]["name_german"]) if tree["tree_taxonomy"]["name_german"] is not None else None,
            }
        except:
            print(tree["tree_id"])
        lines.append(tmp)
    

df = pd.DataFrame(lines)
df.to_csv("data/measures_age_taxonomy.csv", index=False)  

'''
Create csv file from tree data .tar.gz file with necessary features
'''
import json
import tarfile
from typing import Any, Dict, List, Tuple

import pandas as pd


def _get_compressed_data() -> List[str]:
    '''
    Load compressed file.
    '''
    tar = tarfile.open("../../cologne-treemap-api/data/trees_cologne_2017.jsonl.tar.gz") #, mode='rb:gz')
    f = tar.extractfile("trees_cologne_2017.jsonl")
    lines = f.read().decode().split("\n")
    
    return lines


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

        tmp = {
            "id": tree["tree_id"],
            "height": tree["tree_info"]["height"],
            "treetop_radius": tree["tree_info"]["treetop_radius"],
            "bole_radius": tree["tree_info"]["bole_radius"],
            "age": tree["tree_info"]["year_sprout"],
            "age_group_2020": tree["tree_info"]["age_group_2020"],
            "genus": tree["tree_taxonomy"]["genus"],
            "type": tree["tree_taxonomy"]["type"],
            "name_german": "|".join(tree["tree_taxonomy"]["name_german"]) if tree["tree_taxonomy"]["name_german"] is not None else None,
        }
        lines.append(tmp)
    

df = pd.DataFrame(lines)
df.to_csv("data/measures_age_taxonomy.csv", index=False)  

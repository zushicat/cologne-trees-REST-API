import json
import tarfile
from typing import Any, Dict, List

import pandas as pd


def _get_compressed_tree_data() -> List[str]:
    '''
    Load compressed file.
    '''
    tar = tarfile.open("../cologne-treemap-api/data/trees_cologne_merged.jsonl.tar.gz") #, mode='rb:gz')
    f = tar.extractfile("trees_cologne_merged.jsonl")
    lines = f.read().decode().split("\n")
    
    return lines



if __name__ == "__main__":
    tree_data_str = _get_compressed_tree_data()
    df_predictions_age = pd.read_csv("data_prediction/data/predictions_age_group.csv")
    
    lines: List[Dict[str, Any]] = []
    for line in tree_data_str:
        try:
            tree_data = json.loads(line)
        except:
            continue

        if tree_data.get("predictions") is None:
            tree_data["predictions"]: Dict[str, Any] = {}

        tree_id = tree_data["tree_id"]
        tree_prediction_list = df_predictions_age.loc[df_predictions_age['tree_id'] == tree_id]
        
        if len(tree_prediction_list) == 0:
            lines.append(tree_data)
            continue

        current_prediction = tree_prediction_list.iloc[0]
        
        # print(current_prediction["age_group_2020"], current_prediction["probabiliy"])
        tree_data["predictions"]["age_prediction"] = {
            "age_group_2020": int(current_prediction["age_group_2020"]),
            "probabiliy_age_group_2020": float(current_prediction["probabiliy"])
        }

        lines.append(tree_data)

    # write cleaned file
    with open("trees_cologne_merged.jsonl", "w") as f:  # overwrite old data
        for line in lines:
            f.write(f"{json.dumps(line, ensure_ascii=False)}\n")

    # write compressed tar.gz file in docker data directory
    tar = tarfile.open("../cologne-treemap-api/data/trees_cologne_merged.jsonl.tar.gz","w:gz")
    tar.add("trees_cologne_merged.jsonl")
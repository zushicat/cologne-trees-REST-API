import json
import tarfile
from typing import Any, Dict, List

import pandas as pd


def _get_compressed_tree_data() -> List[str]:
    '''
    Load compressed file.
    '''
    tar = tarfile.open("../cologne-treemap-api/data/trees_cologne_2017.jsonl.tar.gz") #, mode='rb:gz')
    f = tar.extractfile("trees_cologne_2017.jsonl")
    lines = f.read().decode().split("\n")
    
    return lines



if __name__ == "__main__":
    tree_data_str = _get_compressed_tree_data()
    df_predictions_age = pd.read_csv("data_prediction/data/predictions_age_group.csv")
    
    lines: List[Dict[str, Any]] = []
    for line in tree_data_str:
        try:
            tree = json.loads(line)
        except:
            continue

        tree_id = tree["tree_id"]
        tree_prediction_list = df_predictions_age.loc[df_predictions_age['tree_id'] == tree_id]
        
        if len(tree_prediction_list) == 0:
            continue

        current_prediction = tree_prediction_list.iloc[0]
        
        print(current_prediction["age_group_2020"], current_prediction["probabiliy"])

        break

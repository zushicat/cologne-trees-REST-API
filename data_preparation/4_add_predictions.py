import json
import tarfile
from typing import Any, Dict, List, Optional

import pandas as pd


def _get_compressed_tree_data() -> List[str]:
    '''
    Load compressed file.
    '''
    tar = tarfile.open("../cologne-treemap-api/data/trees_cologne_merged.jsonl.tar.gz")
    f = tar.extractfile("trees_cologne_merged.jsonl")
    lines = f.read().decode().split("\n")
    
    return lines


def _get_predictions_age() -> Dict[str, Dict[str, Any]]:
    '''
    columns: tree_id, age_group_2020, probability
    '''
    df_predictions_age = pd.read_csv("data_prediction/data/predictions_age_group.csv")

    predictions_age: Dict[str, Dict[str, Any]] = {}
    for index, row in df_predictions_age.iterrows():
        predictions_age[row["tree_id"]] = {
            "age_group": row["age_group_2020"],
            "probability": row["probability"]
        }
    
    return predictions_age


def _get_predictions_by_radius() -> Dict[str, Dict[str, Any]]:
    '''
    columns: tree_id, genus, age_group, probability
    '''
    df_predictions_age = pd.read_csv("data_prediction/data/predictions_by_radius.csv")

    predictions_by_radius: Dict[str, Dict[str, Any]] = {}
    for index, row in df_predictions_age.iterrows():
        predictions_by_radius[row["tree_id"]] = {
            "age_group": row["age_group"],
            "genus": row["genus"],
            "probability": row["probability"]
        }
    
    return predictions_by_radius



if __name__ == "__main__":
    tree_data_str = _get_compressed_tree_data()
    
    predictions_age = _get_predictions_age()
    predictions_by_radius = _get_predictions_by_radius()
    
    lines: List[Dict[str, Any]] = []

    for i, line in enumerate(tree_data_str):
        try:
            tree_data = json.loads(line)
        except:
            continue

        if tree_data.get("predictions") is None:
            tree_data["predictions"]: Optional[Dict[str, Any]] = None

        tree_id = tree_data["tree_id"]
        
        if predictions_age.get(tree_id) is not None or predictions_by_radius.get(tree_id) is not None:
            if tree_data.get("predictions") is None:
                tree_data["predictions"] = {
                    "age_prediction": None,
                    "by_radius_prediction": None
                }

        # ***
        # age_group only prediction
        if predictions_age.get(tree_id) is not None:
            tree_data["predictions"]["age_prediction"] = {
                "age_group_2020": int(predictions_age[tree_id]["age_group"]),
                "probabiliy": float(predictions_age[tree_id]["probability"])
            }
        
        # ***
        # prediction by radius
        if predictions_by_radius.get(tree_id) is not None:
            tree_data["predictions"]["by_radius_prediction"] = {
                "age_group_2020": int(predictions_by_radius[tree_id]["age_group"]),
                "genus": predictions_by_radius[tree_id]["genus"],
                "probabiliy": float(predictions_by_radius[tree_id]["probability"])
            }
        
        lines.append(tree_data)

    # write cleaned file
    with open("trees_cologne_merged.jsonl", "w") as f:  # overwrite old data
        for line in lines:
            f.write(f"{json.dumps(line, ensure_ascii=False)}\n")

    # write compressed tar.gz file in docker data directory
    tar = tarfile.open("../cologne-treemap-api/data/trees_cologne_merged.jsonl.tar.gz","w:gz")
    tar.add("trees_cologne_merged.jsonl")
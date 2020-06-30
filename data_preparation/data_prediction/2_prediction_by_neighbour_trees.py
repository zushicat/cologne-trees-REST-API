'''
This is in fact a classifier problem (rather than a regression problem) which is obvious when predicting age_groups
Make model for age prediction
X: from genus and bole radius
y: age or/age group
'''
# from collections import Counter, defaultdict
import json
from typing import Any, Dict, List, Tuple

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn import metrics
from sklearn.cluster import DBSCAN


# *******************************************************
#
# *******************************************************
def _load_data() -> pd.DataFrame:
    columns = ["id", "age_group_2020", "genus"]
    df = pd.read_csv("data/measures_age_taxonomy.csv", usecols=columns)
    
    return df
    

def _load_neighbour_pairs() -> Dict[str, Dict[str, float]]:
    with open("data/all_tree_pairs_distance.jsonl") as f:
        pairs = f.read().split("\n")
    tree_pairs_by_id: Dict[str, Dict[str, float]] = {}
    for pair_str in pairs:
        try:
            pair = json.loads(pair_str)
        except:
            continue
        id_1 = pair[0]
        id_2 = pair[1]
        distance = pair[2]
        
        # ***
        # bi-directionaly
        if tree_pairs_by_id.get(id_1) is None:
            tree_pairs_by_id[id_1] = {}
        tree_pairs_by_id[id_1][id_2] = distance

        if tree_pairs_by_id.get(id_2) is None:
            tree_pairs_by_id[id_2] = {}
        tree_pairs_by_id[id_2][id_1] = distance

    return tree_pairs_by_id


def _split_data_train_pred(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df["has_all"] = False
    df["missing_all"] = False
    df["missing_age_only"] = False
    
    # df = df[df[cols].notnull().all(axis=1)]
    df["has_all"] = pd.notna(df[["age_group_2020", "genus"]]).all(axis=1)
    df["missing_all"] = pd.isna(df[["age_group_2020", "genus"]]).all(axis=1)
    df["missing_age_only"] = df.apply(lambda x: True if (pd.notna(x.genus) and pd.isnull(x.age_group_2020)) else False, axis=1)
    
    drop_cols = ["has_all", "missing_all", "missing_age_only"]

    df_has_all = df[df["has_all"] == True].drop(drop_cols, axis=1)
    df_has_no_age = df[(df["missing_all"]==False) & (df["missing_age_only"]==True)].drop(drop_cols, axis=1)
    df_has_none = df[df["missing_all"] == True].drop(drop_cols, axis=1)

    df_has_all = df_has_all.dropna()

    return df_has_all, df_has_no_age, df_has_none


def _get_tree_features(df: pd.DataFrame) -> Dict[str, Any]:
    tree_features_by_id: Dict[str, Any] = {}
    for index, row in df.iterrows():
        tree_features_by_id[row["id"]] = {
            "age_group": int(row["age_group_2020"]),
            "encoded_genus": row["encoded_genus"]
        }
    
    return tree_features_by_id


# *******************************************************
#
# *******************************************************
def _evaluate(df_has_all: pd.DataFrame, tree_features_by_id: Dict[str, Any], tree_pairs_by_id: Dict[str, Any], max_distance: int) -> None:
    predictions: Dict[str, Any] = {}
    count_correct_genus = 0
    count_correct_age_group = 0
    count_predicted = 0
    with_neighbours = 0
    all_trees = 0
    for row_index, row in df_has_all.iterrows():
        # if row_index == 2:
        #     break

        all_trees += 1
        current_tree_id = row["id"]

        if tree_pairs_by_id.get(current_tree_id) is None:
            continue
        
        with_neighbours += 1

        # # print(f"--------- {i} --------")
        # # print(current_tree_id)
        # # print(tree_features_by_id[current_tree_id]["age_group"], label_encoder.inverse_transform([tree_features_by_id[current_tree_id]["encoded_genus"]])[0])
        # # print()

        
        gt_genus: str = label_encoder.inverse_transform([tree_features_by_id[current_tree_id]["encoded_genus"]])[0]
        gt_age_group: int = tree_features_by_id[current_tree_id]["age_group"]

        predictions[current_tree_id] = {
            "genus": {
                "gt": gt_genus,
                "prediction": None,
            },
            "age_group": {
                "gt": gt_age_group,
                "prediction": None,
            },
            "num_all_valid_neighbours": 0,
            "num_clusters": 0
        }
    
        try:
            # ***
            # build cluster
            cluster_data = np.empty((0, 2))
            
            for idx, distance in tree_pairs_by_id[current_tree_id].items():
                if tree_features_by_id.get(idx) is None:  # trees without features are not in dict
                    continue
                
                distance = int(round(distance))
                genus = tree_features_by_id[idx]["encoded_genus"]
                age_group = tree_features_by_id[idx]["age_group"]

                if distance > max_distance:
                    continue

                predictions[current_tree_id]["num_all_valid_neighbours"] += 1

                cluster_data = np.append(cluster_data, np.array([[age_group, genus]]), axis=0)
                # cluster_data = np.append(cluster_data, np.array([[genus]]), axis=0)
                # cluster_data = np.append(cluster_data, np.array([[genus, distance]]), axis=0)
                
            #print(json.dumps(bla, indent=2))
            # print(row_index)
            # print(cluster_data)

            X = StandardScaler().fit_transform(cluster_data)
            clusters = DBSCAN(eps=0.5, min_samples=1).fit(X)

            core_samples_mask = np.zeros_like(clusters.labels_, dtype=bool)
            core_samples_mask[clusters.core_sample_indices_] = True

            clusters_labels = clusters.labels_

            predictions[current_tree_id]["num_clusters"] = len(list(set(clusters_labels)))
            predictions[current_tree_id]["counts_cluster"] = []

            clusters_data = {}
            for index, label in enumerate(clusters_labels):
                label = int(label)
                if clusters_data.get(label) is None:
                    age_group = int(cluster_data[index, 0])
                    genus = int(cluster_data[index, 1])
                    clusters_data[label] = {
                        "count": 0, 
                        "age_group": age_group, 
                        "genus": label_encoder.inverse_transform([genus])[0]
                    }
                clusters_data[label]["count"] += 1
                
            # print(json.dumps(clusters_data, indent=2))
            # print()

            # ***
            # get max cluster
            max_key = None
            max_count = 0
            for cluster_label, cluster_vals in clusters_data.items():
                if cluster_vals["count"] >= max_count:
                    max_count = cluster_vals["count"]
                    max_key = cluster_label
                
                predictions[current_tree_id]["counts_cluster"].append(cluster_vals["count"])
            

            predictions[current_tree_id]["max_count_cluster"] = max_count
            
            # print(clusters_data[max_key]["age_group"], clusters_data[max_key]["genus"])
            predictions[current_tree_id]["genus"]["prediction"] = clusters_data[max_key]["genus"]
            predictions[current_tree_id]["age_group"]["prediction"] = clusters_data[max_key]["age_group"]
            
            if predictions[current_tree_id]["genus"]["prediction"] == gt_genus:
                count_correct_genus += 1
            if predictions[current_tree_id]["age_group"]["prediction"] == gt_age_group:
                count_correct_age_group += 1

            # print(predictions[current_tree_id])
            # print("---")
            
            count_predicted += 1
        except:
           continue

    print(all_trees, with_neighbours, round(with_neighbours/all_trees, 2), count_predicted, round(count_predicted/all_trees, 2))
    print(count_predicted, count_correct_genus, round(count_correct_genus/count_predicted, 2), count_correct_age_group, round(count_correct_age_group/count_predicted, 2))


def _predict(df_has_none: pd.DataFrame, tree_features_by_id: Dict[str, Any], tree_pairs_by_id: Dict[str, Any], max_distance: int) -> Dict[str, Any]:
    predictions: Dict[str, Any] = {}
    count_predicted = 0
    for row_index, row in df_has_none.iterrows():
        # if row_index == 2:
        #     break

        current_tree_id = row["id"]

        if tree_pairs_by_id.get(current_tree_id) is None:
            continue
        
        try:
            # ***
            # build cluster
            cluster_data = np.empty((0, 2))
            
            for idx, distance in tree_pairs_by_id[current_tree_id].items():
                if tree_features_by_id.get(idx) is None:  # trees without features are not in dict
                    continue
                
                # distance = int(round(distance))
                genus = tree_features_by_id[idx]["encoded_genus"]
                age_group = tree_features_by_id[idx]["age_group"]

                # cluster_data = np.append(cluster_data, np.array([[distance, age_group, genus]]), axis=0)
                cluster_data = np.append(cluster_data, np.array([[age_group, genus]]), axis=0)
                
            #print(json.dumps(bla, indent=2))
            #print(cluster_data)

            X = StandardScaler().fit_transform(cluster_data)
            clusters = DBSCAN(eps=0.3, min_samples=1).fit(X)

            core_samples_mask = np.zeros_like(clusters.labels_, dtype=bool)
            core_samples_mask[clusters.core_sample_indices_] = True

            clusters_labels = clusters.labels_

            clusters_data = {}
            for index, label in enumerate(clusters_labels):
                label = int(label)
                if clusters_data.get(label) is None:
                    age_group = int(cluster_data[index, 0])
                    genus = int(cluster_data[index, 1])
                    clusters_data[label] = {
                        "count": 0, 
                        "age_group": age_group, 
                        "genus": label_encoder.inverse_transform([genus])[0]
                    }
                clusters_data[label]["count"] += 1
            
            #print(json.dumps(clusters_data, indent=2))
            #print()

            # ***
            # get max cluster
            max_key = None
            max_count = 0
            for cluster_label, cluster_vals in clusters_data.items():
                if cluster_vals["count"] >= max_count:
                    max_count = cluster_vals["count"]
                    max_key = cluster_label
            
            # ***
            #
            predictions[current_tree_id] = {
                "tree_id": current_tree_id,
                "genus": clusters_data[max_key]["genus"],
                "age_group": clusters_data[max_key]["age_group"],
                # "num_cluster": len(clusters_data.keys()),
                # "num_all_neighbours": len(tree_pairs_by_id[current_tree_id].keys()),
                # "max_count": max_count,
                "probability": round(max_count/len(tree_pairs_by_id[current_tree_id].keys()), 2)
            }
            
            count_predicted += 1
        except:
            continue

    # print(count_predicted, len(df_has_none), round(count_predicted/len(df_has_none), 2))
    # print(json.dumps(predictions, indent=2))
    return predictions  # <id>: { ... }


# *******************************************************
#
# *******************************************************
if __name__ == "__main__":
    df = _load_data()
    tree_pairs_by_id = _load_neighbour_pairs()

    print(f"-- data loaded --")
    
    label_encoder = LabelEncoder()
    
    df["encoded_genus"] = label_encoder.fit_transform(df["genus"].astype(str))
    
    df_has_all, df_has_no_age, df_has_none = _split_data_train_pred(df)
    # print(len(df_has_all), len(df_has_no_age), len(df_has_none))
    print(f"-- data split --")
    
    tree_features_by_id = _get_tree_features(df_has_all)
    print(f"-- features loaded --")

    # _evaluate(df_has_all, tree_features_by_id, tree_pairs_by_id, 20)
    prediction_results = _predict(df_has_none, tree_features_by_id, tree_pairs_by_id, 50)

    # ***
    #
    df = pd.DataFrame(prediction_results.values())
    df.to_csv("data/predictions_by_radius.csv", index=False)
    
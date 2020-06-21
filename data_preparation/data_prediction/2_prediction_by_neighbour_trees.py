'''
This is in fact a classifier problem (rather than a regression problem) which is obvious when predicting age_groups
Make model for age prediction
X: from genus and bole radius
y: age or/age group
'''
import json
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from sklearn.preprocessing import LabelEncoder, Normalizer, MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error

from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, VotingClassifier
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

# *******************************************************
#
# *******************************************************
def _load_data() -> Tuple[pd.DataFrame, Dict[str, Dict[str, float]]]:
    columns = ["id", "bole_radius", "age", "age_group_2020", "genus"]
    df = pd.read_csv("data/measures_age_taxonomy.csv", usecols=columns)
    
    # get neighbour pairs
    with open("data/all_tree_pairs_distance.jsonl") as f:
        pairs = f.read().split("\n")
    tree_pairs_by_id: Dict[str, Dict[str, float]] = {}
    for pair_str in pairs[:1000]:
        try:
            pair = json.loads(pair_str)
        except:
            continue
        id_1 = pair[0]
        id_2 = pair[1]
        distance = pair[2]
        if tree_pairs_by_id.get(id_1) is None:
            tree_pairs_by_id[id_1] = {}
        tree_pairs_by_id[id_1] = {id_2: distance}

    return df, tree_pairs_by_id


def _split_data_train_pred(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df["has_all"] = False
    df["missing_all"] = False
    df["missing_age_only"] = False
    
    # df = df[df[cols].notnull().all(axis=1)]
    df["has_all"] = pd.notna(df[["bole_radius", "age_group_2020", "genus"]]).all(axis=1)
    df["missing_all"] = pd.isna(df[["bole_radius", "age_group_2020", "genus"]]).all(axis=1)
    df["missing_age_only"] = df.apply(lambda x: True if ((pd.notna(x.bole_radius) and pd.notna(x.genus)) and pd.isnull(x.age_group_2020)) else False, axis=1)
    
    drop_cols = ["has_all", "missing_all", "missing_age_only", "genus"]

    df_has_all = df[df["has_all"] == True].drop(drop_cols, axis=1)
    df_has_no_age = df[(df["missing_all"]==False) & (df["missing_age_only"]==True)].drop(drop_cols, axis=1)
    df_has_none = df[df["missing_all"] == True].drop(drop_cols, axis=1)

    df_has_all = df_has_all.dropna()

    return df_has_all, df_has_no_age, df_has_none



# *******************************************************
#
# *******************************************************
if __name__ == "__main__":
    df, tree_pairs_by_id = _load_data()
    
    label_encoder = LabelEncoder()
    df["encoded_genus"] = label_encoder.fit_transform(df["genus"].astype(str))
    
    df_has_all, df_has_no_age, df_has_none = _split_data_train_pred(df)
    print(len(df_has_all), len(df_has_no_age), len(df_has_none))

    



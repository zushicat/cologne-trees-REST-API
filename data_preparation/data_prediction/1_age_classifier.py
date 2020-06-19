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
def _load_data() -> pd.DataFrame:
    columns = ["id", "bole_radius", "age", "age_group_2020", "genus"]  # , "type"]
    df = pd.read_csv("data/measures_age_taxonomy.csv", usecols=columns)
    
    # seemingly no significant difference between genus only or genus + type
    # to be further investigated
    # df["genus"] = df.apply(lambda x: None if pd.isnull(x.genus) and pd.isnull(x.type) else f"{x.genus}_{x.type}", axis=1)
    # df.drop(["type"], axis=1, inplace=True)

    return df


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
def _evaluate_train_test(df: pd.DataFrame, num_classes: int, y_col_name: str) -> None:
    X = df[["bole_radius_scaled", "encoded_genus"]].to_numpy()
    y = df[[y_col_name]].to_numpy().ravel()
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.9,test_size=0.1, random_state=0)

    classifiers = [
        ("KNeighbors", KNeighborsClassifier(num_classes)),
        #("SVC_1", SVC(kernel="linear", C=0.025)),
        #("SVC_2", SVC(gamma=2, C=1)),
        #("GaussianProcess", GaussianProcessClassifier(1.0 * RBF(1.0))),
        ("DecisionTree", DecisionTreeClassifier(max_depth=5)),
        ("RandomForest", RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1)),
        #("MLP", MLPClassifier()),
        #("AdaBoost", AdaBoostClassifier()),
        ("NaiveBayes_Gaussian", GaussianNB()),
        #("QuadraticDiscriminantAnalysis", QuadraticDiscriminantAnalysis())
    ]

    classifier = VotingClassifier(estimators=classifiers, voting='soft')
    classifier.fit(X_train, y_train)
    
    score = classifier.score(X_test, y_test)
    print(f"score: {score}")

    mse = mean_squared_error(y_test, classifier.predict(X_test))
    print("The mean squared error (MSE) on test set: {:.4f}".format(mse))

    #print(classifier.classes_)
    #predictions = classifier.predict_proba(X_test)

    # for i, p in enumerate(predictions):
    #     max_prob_index = np.argmax(p)
    #     print(int(classifier.classes_[max_prob_index]), round(p[max_prob_index], 2))
    #     break
    
    predictions = classifier.predict(X_test)
    correct_count = 0
    incorrect_count = 0
    delta_diff = {"1": 0, "2": 0, "3": 0}
    for i, p in enumerate(predictions):
        predicted_age = int(round(p))
        gt_age = int(y_test[i])
        if predicted_age != gt_age:
            incorrect_count += 1
            delta = abs(predicted_age - gt_age)
            if delta == 1:
                delta_diff["1"] += 1
            if delta == 2:
                delta_diff["2"] += 1
            if delta >= 3:
                delta_diff["3"] += 1
        else:
            correct_count += 1
            
    print(delta_diff)
    print(incorrect_count)
    print(correct_count)


# *******************************************************
#
# *******************************************************
if __name__ == "__main__":
    df = _load_data()
    
    label_encoder = LabelEncoder()
    df["encoded_genus"] = label_encoder.fit_transform(df["genus"].astype(str))
    
    df_has_all, df_has_no_age, df_has_none = _split_data_train_pred(df)
    print(len(df_has_all), len(df_has_no_age), len(df_has_none))

    # ***
    # scale values of bole_radius
    scaler = StandardScaler()
    df_has_all["bole_radius_scaled"] = scaler.fit_transform(df_has_all[["bole_radius"]])
    df_has_no_age["bole_radius_scaled"] = scaler.fit_transform(df_has_no_age[["bole_radius"]])

    # ***
    #
    num_classes = len(df_has_all["age_group_2020"].unique())
    # num_classes = len(df_has_all["age"].unique())

    #_evaluate_train_test(df_has_all, num_classes, "age_group_2020")

    X_train = df_has_all[["bole_radius_scaled", "encoded_genus"]].to_numpy()
    y_train = df_has_all[["age_group_2020"]].to_numpy().ravel()

    X_pred = df_has_no_age[["bole_radius_scaled", "encoded_genus"]].to_numpy()
 
    classifiers = [
        ("KNeighbors", KNeighborsClassifier(num_classes)),
        #("SVC_1", SVC(kernel="linear", C=0.025)),
        #("SVC_2", SVC(gamma=2, C=1)),
        #("GaussianProcess", GaussianProcessClassifier(1.0 * RBF(1.0))),
        ("DecisionTree", DecisionTreeClassifier(max_depth=5)),
        ("RandomForest", RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1)),
        #("MLP", MLPClassifier()),
        #("AdaBoost", AdaBoostClassifier()),
        ("NaiveBayes_Gaussian", GaussianNB()),
        #("QuadraticDiscriminantAnalysis", QuadraticDiscriminantAnalysis())
    ]

    classifier = VotingClassifier(estimators=classifiers, voting='soft')
    classifier.fit(X_train, y_train)

    predictions = classifier.predict_proba(X_pred)

    collected_predictions: List[Dict[str, Any]] = []
    for i, p in enumerate(predictions):
        max_prob_index = np.argmax(p)

        tmp = {
            "tree_id": df_has_no_age.iloc[i]["id"],
            "age_group_2020": int(classifier.classes_[max_prob_index]),
            "probabiliy": round(p[max_prob_index], 2)
        }
        collected_predictions.append(tmp)

    # ***
    #
    df = pd.DataFrame(collected_predictions)
    df.to_csv("data/predictions_age_group.csv", index=False)  

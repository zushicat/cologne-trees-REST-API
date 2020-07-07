'''
Merge data 2017 and 2020
'''
import json
from typing import Any, Dict, List, Optional


# Debatable: Assume a certain default age when planting
# According to Stadt Düsseldorf, a young tree spends it's first 8 - 12 years in tree nursery:
# https://www.duesseldorf.de/stadtgruen/baeume-in-der-stadt/baum-doku.html
PLANTING_AGE = 10


def _add_to_list(tree_list: List[str], year: str, trees_by_utm: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    for line in tree_list:
        try:
            tree_data = json.loads(line)
        except:
            continue

        utm_values = f'{tree_data["geo_info"]["utm_x"]}_{tree_data["geo_info"]["utm_y"]}'
        if trees_by_utm.get(utm_values) is None:
            trees_by_utm[utm_values] = {"2017": [], "2020": []}
        trees_by_utm[utm_values][year].append(tree_data)

    return trees_by_utm


def _recalc_age_values(tree_age_data: Dict[str, Any]) -> Dict[str, Any]:
    '''
    Gets the "tree_age" object part.
    '''
    tree_age_data["year_sprout"] = tree_age_data["year_planting"] - PLANTING_AGE
    tree_age_data["age_in_2017"] = 2017 - tree_age_data["year_sprout"]
    tree_age_data["age_in_2020"] = 2020 - tree_age_data["year_sprout"]

    for j, group in enumerate([(1,26), (26,41), (41,1000)]):
        lower_boundary = group[0]
        upper_boundary = group[1]
        if tree_age_data["age_in_2020"] >= lower_boundary and tree_age_data["age_in_2020"] < upper_boundary:
            tree_age_data["age_group_2020"] = j
            break

    return tree_age_data


def _recalc_completeness(tree_data: Dict[str, Any]) -> Dict[str, Any]:
    # ********
    # % completeness in "base_info", tree_taxonomy and "tree_info"
    # and overall completeness in "dataset_completeness"
    tmp_completeness_collected = 0.0
    tmp_completeness_attr = ["base_info", "tree_taxonomy", "tree_measures", "tree_age"]
    for k in tmp_completeness_attr:
        collected_types_perc = round(len([type(x).__name__ for x in tree_data[k].values() if type(x).__name__ != "NoneType"]) / len(tree_data[k].values()), 2)  # i.e. ["NoneType", "str", "int", "str"]
        tree_data[f"{k}_completeness"] = collected_types_perc
        tmp_completeness_collected += collected_types_perc

    try:
        tmp_completeness_collected = round(tmp_completeness_collected / len(tmp_completeness_attr), 2)
    except:
        pass
    tree_data["dataset_completeness"] = tmp_completeness_collected

    return tree_data
    

def _get_best_tree_from_treelist(tree_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    dataset_completeness_list = [x["dataset_completeness"] for x in tree_list]
    best_completeness_index = dataset_completeness_list.index(max(dataset_completeness_list))

    return tree_list[best_completeness_index]


with open("raw_trees_cologne_2017.jsonl") as f:
    trees_2017_list = f.read().split("\n")

with open("raw_trees_cologne_2020.jsonl") as f:
    trees_2020_list = f.read().split("\n")


trees_by_utm: Dict[str, List[Dict[str, Any]]] = _add_to_list(trees_2017_list, "2017", {})
trees_by_utm: Dict[str, List[Dict[str, Any]]] = _add_to_list(trees_2020_list, "2020", trees_by_utm)

merged_data: List[Dict[str, Any]] = []

for utm_key, utm_vals in trees_by_utm.items():
    current_tree_2017: Optional[Dict[str, Any]] = None
    current_tree_2020: Optional[Dict[str, Any]] = None
    
    try:
        current_tree_2017 = _get_best_tree_from_treelist(utm_vals["2017"])
        # ***
        # fill missing age data -> 2017
        current_tree_2017["tree_age"]["year_planting"] = None
        if current_tree_2017["tree_age"]["year_sprout"] is not None:
            current_tree_2017["tree_age"]["year_planting"] = current_tree_2017["tree_age"]["year_sprout"] + PLANTING_AGE
        current_tree_2017 = _recalc_completeness(current_tree_2017)
    except:
        pass

    try:
        current_tree_2020 = _get_best_tree_from_treelist(utm_vals["2020"])
        # ***
        # fill missing age data -> 2020
        for age_key in ["age_in_2017", "age_in_2020", "age_group_2020", "year_sprout"]:
            current_tree_2020["tree_age"][age_key] = None
        if current_tree_2020["tree_age"]["year_planting"] is not None:
            current_tree_2020["tree_age"] = _recalc_age_values(current_tree_2020["tree_age"])
        current_tree_2020 = _recalc_completeness(current_tree_2020)
    except:
        pass
    
    tmp_merged: Dict[str, Any] = {}

    available_in_dataset = {
        "2017": False if current_tree_2017 is None else True,
        "2020": False if current_tree_2020 is None else True
    }

    if available_in_dataset["2017"] != available_in_dataset["2020"]:  # xor
        # ***
        # tree only in one of both sets
        if available_in_dataset["2017"] is True:
            tmp_merged = current_tree_2017
        else:
            tmp_merged = current_tree_2020
    else:
        # ***
        # tree in both sets: prefer 2020 if equal complete, otherwise take best
        if current_tree_2017["dataset_completeness"] == current_tree_2020["dataset_completeness"]:
            tmp_merged = current_tree_2020
        else:
            tmp_merged = _get_best_tree_from_treelist([current_tree_2017, current_tree_2020])

    # ***
    #
    try:
        tmp_merged["found_in_dataset"]: Dict[str, bool] = available_in_dataset
        merged_data.append(tmp_merged)
    except:
        continue


with open("raw_trees_cologne_merged.jsonl", "w") as f:
    for line in merged_data:
        f.write(f"{json.dumps(line, ensure_ascii=False)}\n")

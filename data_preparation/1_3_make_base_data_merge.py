'''
Merge data 2017 and 2020
'''
import json
from typing import Any, Dict, List


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


def _recalc_age_values(tree_age_data: Dict[str, Any], planting_age: int) -> Dict[str, Any]:
    '''
    Gets the "tree_age" object part.
    '''
    tree_age_data["year_sprout"] = tree_age_data["year_planting"] - planting_age
    tree_age_data["age_in_2017"] = 2017 - tree_age_data["year_sprout"]
    tree_age_data["age_in_2020"] = 2020 - tree_age_data["year_sprout"]

    for j, group in enumerate([(1,6), (6,16), (16,40), (40,1000)]):
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
    

with open("raw_trees_cologne_2017.jsonl") as f:
    trees_2017_list = f.read().split("\n")

with open("raw_trees_cologne_2020.jsonl") as f:
    trees_2020_list = f.read().split("\n")


trees_by_utm: Dict[str, List[Dict[str, Any]]] = _add_to_list(trees_2017_list, "2017", {})
trees_by_utm: Dict[str, List[Dict[str, Any]]] = _add_to_list(trees_2020_list, "2020", trees_by_utm)

# Debatable: Assume a certain default age when planting
# According to Stadt Düsseldorf, a young tree spends it's first 8 - 12 years in tree nursery:
# https://www.duesseldorf.de/stadtgruen/baeume-in-der-stadt/baum-doku.html
planting_age = 10

merged_data: List[Dict[str, Any]] = []
for utm_key in list(trees_by_utm.keys()):
    len_2017 = len(trees_by_utm[utm_key]["2017"])
    len_2020 = len(trees_by_utm[utm_key]["2020"])

    tmp_merged: Dict[str, Any] = {}

    available_in_dataset = {
        "2017": False,
        "2020": False
    }

    # ***
    # 2020 only
    if len_2017 == 0 and len_2020 == 1:
        tmp_merged = trees_by_utm[utm_key]["2020"][0]
        for age_key in ["age_in_2017", "age_in_2020", "age_group_2020", "year_sprout"]:
            tmp_merged["tree_age"][age_key] = None
        if tmp_merged["tree_age"]["year_planting"] is not None:
            tmp_merged["tree_age"] = _recalc_age_values(tmp_merged["tree_age"], planting_age)
        available_in_dataset["2020"] = True
    
    # ***
    # 2017 only
    if len_2017 == 1 and len_2020 == 0:
        tmp_merged = trees_by_utm[utm_key]["2017"][0]
        tmp_merged["tree_age"]["year_planting"] = None
        if tmp_merged["tree_age"]["year_sprout"] is not None:
            tmp_merged["tree_age"]["year_planting"] = tmp_merged["tree_age"]["year_sprout"] + planting_age
        available_in_dataset["2017"] = True
    
    # ***
    # 2017 and 2020
    if len_2017 == 1 and len_2020 == 1:
        available_in_dataset["2017"] = True
        available_in_dataset["2020"] = True

        # ***
        # 
        if trees_by_utm[utm_key]["2017"][0]["dataset_completeness"] >= trees_by_utm[utm_key]["2020"][0]["dataset_completeness"]:
            tmp_merged = trees_by_utm[utm_key]["2017"][0]
            tmp_merged["tree_age"]["year_planting"] = trees_by_utm[utm_key]["2020"][0]["tree_age"]["year_planting"]
        else:
            tmp_merged = trees_by_utm[utm_key]["2020"][0]
            tmp_merged["tree_age"]["age_in_2017"] = trees_by_utm[utm_key]["2017"][0]["tree_age"]["age_in_2017"]
            tmp_merged["tree_age"]["age_in_2020"] = trees_by_utm[utm_key]["2017"][0]["tree_age"]["age_in_2020"]
            tmp_merged["tree_age"]["age_group_2020"] = trees_by_utm[utm_key]["2017"][0]["tree_age"]["age_group_2020"]
            tmp_merged["tree_age"]["year_sprout"] = trees_by_utm[utm_key]["2017"][0]["tree_age"]["year_sprout"]

        # ***
        # debatable: trust the "year_planting" value in 2020 set more than the age estimation in 2017 set
        if tmp_merged["tree_age"]["year_planting"] is not None:
            tmp_merged["tree_age"] = _recalc_age_values(tmp_merged["tree_age"], planting_age)
        else:
            if tmp_merged["tree_age"]["year_sprout"] is not None:
                tmp_merged["tree_age"]["year_planting"] = tmp_merged["tree_age"]["year_sprout"] + planting_age

    # ***
    # ignore for the moment
    # TODO: create filter for most relevant in each list, then merge
    if len_2017 > len_2020  and len_2017 > 1:  # both_uneven_2017_bigger num: 170
        continue
    if len_2020 > len_2017  and len_2020 > 1:  # both_uneven_2020_bigger num: 112
        continue
    
    # ***
    #
    try:
        tmp_merged = _recalc_completeness(tmp_merged)
        tmp_merged["found_in_dataset"]: Dict[str, bool] = available_in_dataset
        merged_data.append(tmp_merged)
    except:
        continue


with open("raw_trees_cologne_merged.jsonl", "w") as f:
    for line in merged_data:
        f.write(f"{json.dumps(line, ensure_ascii=False)}\n")

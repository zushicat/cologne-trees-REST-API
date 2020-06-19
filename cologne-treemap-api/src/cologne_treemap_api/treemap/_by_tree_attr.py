import json
import datetime

from typing import Any, Dict, List


def get_tree_attr_age_numbers(
    treemap: List[Dict[str, Any]], sort_by: str
) -> Dict[str, Any]:
    current_year = int(datetime.datetime.today().year)
    numbers_by_year = {}
    for tree in treemap:
        year_sprout = tree["tree_age"]["year_sprout"]
        if year_sprout is not None:
            age = current_year - year_sprout
        else:
            age = -1

        if numbers_by_year.get(age) is None:
            numbers_by_year[age] = 0
        numbers_by_year[age] += 1

    if sort_by == "age":
        numbers_by_year = {k: numbers_by_year[k] for k in sorted(numbers_by_year)}
    if sort_by == "number":
        numbers_by_year = {
            k: numbers_by_year[k]
            for k in sorted(numbers_by_year, key=numbers_by_year.get, reverse=True)
        }

    return numbers_by_year


def get_tree_attr_genus_numbers(
    treemap: List[Dict[str, Any]], sort_by: str
) -> Dict[str, Any]:
    numbers_by_genus = {}
    for tree in treemap:
        genus = tree["tree_taxonomy"]["genus"]
        if genus in ["", "unbekannt", None]:
            genus = "unknown"

        if numbers_by_genus.get(genus) is None:
            numbers_by_genus[genus] = 0
        numbers_by_genus[genus] += 1

    if sort_by == "genus":
        numbers_by_genus = {k: numbers_by_genus[k] for k in sorted(numbers_by_genus)}
    if sort_by == "number":
        numbers_by_genus = {
            k: numbers_by_genus[k]
            for k in sorted(numbers_by_genus, key=numbers_by_genus.get, reverse=True)
        }

    return numbers_by_genus

def get_tree_attr_name_german_numbers(
    treemap: List[Dict[str, Any]], sort_by: str
) -> Dict[str, Any]:
    numbers_by_name_german = {}
    for tree in treemap:
        names_german = tree["tree_taxonomy"]["name_german"]

        if names_german is None:
            names_german = [None]
        
        for name_german in names_german:
            if name_german in ["", "unbekannt", None]:
                name_german = "unknown"

            if numbers_by_name_german.get(name_german) is None:
                numbers_by_name_german[name_german] = 0
            numbers_by_name_german[name_german] += 1

    if sort_by == "name":
        numbers_by_name_german = {k: numbers_by_name_german[k] for k in sorted(numbers_by_name_german)}
    if sort_by == "number":
        numbers_by_name_german = {
            k: numbers_by_name_german[k]
            for k in sorted(numbers_by_name_german, key=numbers_by_name_german.get, reverse=True)
        }

    return numbers_by_name_german

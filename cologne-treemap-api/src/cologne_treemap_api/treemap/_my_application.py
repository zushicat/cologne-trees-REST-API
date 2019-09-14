import json
import os
from typing import Any, Dict, List

from ._make_fancy_shit import do_something

DIRNAME = os.environ["DATA_LOCATION"]
TREEDATA = []

def load_tree_data() -> List[Dict[str, Any]]:
    global TREEDATA
    if len(TREEDATA) == 0:
        with open(f"{DIRNAME}/trees_cologne_2017.jsonl") as f:
            lines = f.read().split("\n")
        for line in lines:
            try:
                line = json.loads(line)
                TREEDATA.append(line)
            except Exception as e:
                # print(f"TREEDATA load line ERR ---> {e}")
                pass

def _print_first_tree() -> None:
    print(json.dumps(TREEDATA[0], indent=2, ensure_ascii=False))


def give_result(stuff: str) -> Dict[str, Any]:
    _print_first_tree()
    try:
        with open(f"./data/some_data.json") as f:
            data = json.load(f)
        return do_something(data.get("name"), stuff)
    except Exception as e:
        return {"status": f"ERROR! {e}"}

def test_request() -> Dict[str, str]:
    return {"status": "YAY! API is running."}
import json
import tarfile
from typing import Any, Dict, List, Optional


DATADIR = "../cologne-treemap-api/data"


def _get_compressed_tree_data() -> List[str]:
    '''
    Load compressed file.
    '''
    tar = tarfile.open(f"{DATADIR}/trees_cologne_merged.jsonl.tar.gz")
    f = tar.extractfile("trees_cologne_merged.jsonl")
    lines = f.read().decode().split("\n")
    
    return lines


def _do_something(tree_data: Dict[str, Any]) -> Dict[str, Any]: # <-- check typing for .geojson datapoint return value
    '''
    TODO: create geojson for single tree data
    '''
    pass


if __name__ == "__main__":
    tree_data_str = _get_compressed_tree_data()
    
    geojson_lines: List[Dict[str, Any]] = []  # <-- this is just an assumption: check how single date is saved in .geojson
    # Please check at this point: is there any structure (i.e. Dict) where single tree data (i.e. within List) is embedded
    # If so: create Dict and use this ccontainer (instead of above default geojson_lines) 

    for line in tree_data_str:
        try:
            tree_data = json.loads(line)
        except:
            continue
    
    # ***
    # this is just an assumption: check how single date is saved in .geojson
    tree_data_geojson = _do_something(tree_data)
    geojson_lines.append(tree_data_geojson)


    # ***
    # create .geojson file
    with open("trees_cologne_merged.geojson", "w") as f:  # overwrite old data
        for line in lines:
            f.write(f"{json.dumps(geojson_lines, ensure_ascii=False)}\n")

    # ***
    # write compressed tar.gz file in docker data directory
    tar = tarfile.open("trees_cologne_merged_geojson.jsonl.tar.gz","w:gz")
    tar.add("trees_cologne_merged.geojson")
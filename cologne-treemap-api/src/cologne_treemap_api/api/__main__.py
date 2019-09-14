from werkzeug.serving import run_simple
from .server import application
from cologne_treemap_api.treemap import load_tree_data

print("load treedata...")
load_tree_data()
print("treedata loaded.")

def start():
    run_simple('0.0.0.0', 80, application, use_reloader=True, reloader_type="stat")

start()

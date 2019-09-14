from werkzeug.serving import run_simple
from .server import application

def start():
    run_simple('0.0.0.0', 80, application, use_reloader=True, reloader_type="stat")

start()

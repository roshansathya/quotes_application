from flask import Flask
from briq.database.mongo_setup import global_init
from settings import BASE_DIR, APP_SECRET_KEY

app = Flask(__name__, template_folder=BASE_DIR+"/briq/template")
app.secret_key = APP_SECRET_KEY
global_init()
from .views import core_views
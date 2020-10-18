import  os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = BASE_DIR+"/briq"
APP_SECRET_KEY = 'briqassignment'

DB_NAME = 'briq_db'
DB_ALIAS = 'core'
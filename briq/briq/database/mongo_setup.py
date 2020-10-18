import mongoengine
from settings import DB_ALIAS, DB_NAME

def global_init():
    mongoengine.register_connection(alias=DB_ALIAS, name=DB_NAME)
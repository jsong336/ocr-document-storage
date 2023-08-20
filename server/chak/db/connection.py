from ..settings import settings
from pymongo import MongoClient


client = MongoClient(settings.mongodb_config.connection_uri)
database = client[settings.mongodb_config.database]


class collections(object):
    UserAccount = database["UserAccounts"]
    Documents = database["Documents"]

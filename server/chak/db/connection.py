from ..settings import settings
from pymongo import MongoClient
from pymongo.collection import Collection


client = MongoClient(settings.mongodb_config.connection_uri)
database = client[settings.mongodb_config.database]
collections = {
    "UserAccount": database["UserAccounts"]
}

def get_user_collection() -> Collection:
    return collections["UserAccount"]
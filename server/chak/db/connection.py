from ..settings import settings
from pymongo import MongoClient


client = MongoClient(settings.mongodb_config.connection_uri)
database = client[settings.mongodb_config.database]


class collections(object):
    UserAccount = database["UserAccounts"]
    Documents = database["Documents"]


collections.UserAccount.create_index("email", unique=True)
collections.Documents.create_index(["text_search", "text"])

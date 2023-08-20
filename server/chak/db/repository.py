from .schema import UserAccount
from .connection import get_user_collection
import datetime as dt
from bson.objectid import ObjectId

user_collection = get_user_collection()

def create_user_account(user: UserAccount):
    if user.id is not None:
        raise ValueError("user already has user id")

    user.created_at = dt.datetime.utcnow()
    user.updated_at = dt.datetime.utcnow()


    result = user_collection.insert_one(user.model_dump())
    user.id = str(result.inserted_id)
    return 


def get_user_account(id: str) -> UserAccount:
    results = user_collection.find_one(filter={
        "_id": ObjectId(id)
    })

    results["_id"] = str(results["_id"])

    return UserAccount(**results)
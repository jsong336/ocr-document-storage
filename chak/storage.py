import google.cloud.storage as gcs
import typing as t
from google.cloud.exceptions import Conflict
from .db.schema import  Document


client = gcs.Client()

class buckets:
    Documents = "documents"

try:
    bucket = client.create_bucket(buckets.Documents)
except Conflict:
    bucket = client.get_bucket(buckets.Documents)


def _user_document_blob(document: Document):
    if not document.id:
        raise ValueError("Document must exists before uploading to storage.")
    if not document.owner_id:
        raise ValueError("Document is not owned by a user")
    
    blobpath = f"{buckets.Documents}/{document.owner_id}/{document.id}-{document.file.filename}"
    return bucket.blob(blobpath), f"/{blobpath}"


b: gcs.Blob = next(bucket.list_blobs())
b.download_as_string()



@t.overload
def upload_user_document(document: Document, fs: t.Any) -> str:
    ...

@t.overload
def upload_user_document(document: Document, data:str) -> str:
    ...


def upload_user_document(document: Document, fs: t.Any) -> str:
    blob, link = _user_document_blob(document)
    blob.upload_from_file(fs)
    return link


def upload_user_document(document: Document, data:str) -> str:
    blob, link = _user_document_blob(document)
    blob.upload_from_string(data)
    return link
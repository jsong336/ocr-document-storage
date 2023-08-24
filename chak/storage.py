import google.cloud.storage as gcs
import typing as t
import io
import tempfile as tmp
from google.cloud.exceptions import Conflict
from .db.schema import Document


client = gcs.Client()


class Bucket:
    Documents = "documents"
    Thumbnails = "thumbnails"

    @classmethod
    def valid_bucket(cls, bucket: str) -> bool:
        return bucket in [cls.Documents, cls.Thumbnails]


try:
    bucket = client.create_bucket(Bucket.Documents)
except Conflict:
    bucket = client.get_bucket(Bucket.Documents)


@t.overload
def upload_blob(dest: str, user_id: str, name: str, file: io.IOBase) -> str:
    ...


@t.overload
def upload_blob(
    dest: str, user_id: str, name: str, file: tmp.SpooledTemporaryFile
) -> str:
    ...


@t.overload
def upload_blob(dest: str, user_id: str, name: str, file: str) -> str:
    ...


def upload_blob(
    dest: str,
    user_id: str,
    name: str,
    file: t.Union[io.IOBase, tmp.SpooledTemporaryFile, str],
) -> str:
    blobpath = f"{dest}/{user_id}/{name}"
    blob = bucket.blob(blobpath)
    if isinstance(file, io.IOBase):
        blob.upload_from_file(file, rewind=True)
    elif isinstance(file, tmp.SpooledTemporaryFile):
        blob.upload_from_file(file._file, rewind=True)
    elif isinstance(file, str):
        blob.upload_from_string(file)
    else:
        raise ValueError(f"{type(file)} is not supported type.")

    return f"/{blobpath}"


def download_blob(
    dest: str,
    user_id: str,
    name: str,
    fs: io.IOBase,
) -> None:
    blobpath = f"{dest}/{user_id}/{name}"
    blob = bucket.blob(blobpath)
    blob.download_to_file(fs)
    return


def _validate_document(document: Document):
    if not document.id:
        raise ValueError("Document must exists before uploading to storage.")
    if not document.owner_id:
        raise ValueError("Document is not owned by a user")


def upload_user_document(dest: str, document: Document, *args, **kwargs) -> str:
    _validate_document(document)
    if not Bucket.valid_bucket(dest):
        raise ValueError(f"{dest} is not valid bucket name.")

    filename = f"{document.id}/{document.file.filename}"
    upload_blob(dest, document.owner_id, filename, *args, **kwargs)
    return f"/storage/{dest}/{document.id}"


def download_user_document(
    dest: str, document: Document, fs: io.IOBase, *args, **kwargs
) -> None:
    _validate_document(document)
    if not Bucket.valid_bucket(dest):
        raise ValueError(f"{dest} is not valid bucket name.")

    filename = f"{document.id}/{document.file.filename}"
    download_blob(dest, document.owner_id, filename, fs, *args, **kwargs)

    return

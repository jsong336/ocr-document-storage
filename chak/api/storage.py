from fastapi import APIRouter, Depends, Response
from .documents import get_user_document
from ..db.schema import UserAccount, Document, FileMeta
from ..storage import download_user_document, Bucket
import logging
import io

logging = logging.getLogger(__file__)

router = APIRouter()


@router.get("/{dest}/{document_id}")
def get_blob_from_storage(
    dest: str, user_document: tuple[UserAccount, Document] = Depends(get_user_document)
):
    _, document = user_document

    fs = io.BytesIO()
    download_user_document(dest, document, fs)

    file: FileMeta = None

    match dest:
        case Bucket.Documents:
            file = document.file
        case Bucket.Thumbnails:
            file = document.thumbnail
        case _:
            raise Exception()

    fs.seek(0)
    return Response(fs.read(), media_type=file.content_type)

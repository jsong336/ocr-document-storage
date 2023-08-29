from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
    Depends,
    Request,
)
from fastapi.responses import JSONResponse
from ..db.schema import UserAccount, Document, FileMeta
from ..api.auth import get_user
from ..db.repository import (
    create_document,
    update_document,
    mark_document_delete, 
    DocumentQuery,
    get_document_by_id,
)
from ..image import process_ocr, generate_thumbnail, THUMBNAIL_FORMAT
from ..storage import upload_user_document, Bucket
from PIL import Image
import typing as t
import logging
import uuid

logger = logging.getLogger(__file__)

router = APIRouter()


class DocumentNotFoundException(Exception):
    ...


def get_user_document(
    document_id: str, request: Request
) -> tuple[UserAccount, Document]:
    user_account = get_user(request)
    doc = get_document_by_id(document_id)
    # TODO: check for permission of user_account on document
    if doc.owner_id != user_account.id:
        # document id not owned by user.
        raise DocumentNotFoundException()
    return user_account, doc


@router.get("/")
def search_documents(query: t.Annotated[DocumentQuery, Depends(DocumentQuery)]):
    return {"documents": query(exclude={"text_search"})}


@router.delete("/")
def mark_document_removed(user_document: tuple[UserAccount, Document] = Depends(get_user_document)):
    _, document = user_document
    mark_document_delete(document)
    return JSONResponse({"message": f"marked document {document.id} removed"}, status_code=202)


@router.post("/")
def submit_documents(
    background_tasks: BackgroundTasks,
    title: t.Annotated[str, Form()],
    file: UploadFile = File(...),
    tags: t.Optional[list] = File(default_factory=list),
    user_account: UserAccount = Depends(get_user),
):
    doc = Document(
        owner_id=user_account.id,
        title=title,
        tags=tags,
        file=FileMeta(
            filename=file.filename, file_size=file.size, content_type=file.content_type
        ),
    )
    create_document(doc)

    def process_document(doc: Document, task_id: str, file: UploadFile):
        try:
            if file.content_type == "image/heic":
                heic = Image.open(file.file)
                img = heic.convert("RGB")
            else:
                img = Image.open(file.file)
            
            text = process_ocr(task_id, img)
            thumbnail = generate_thumbnail(task_id, img)
            thumbnail_link = upload_user_document(
                Bucket.Thumbnails, doc, file=thumbnail
            )
            # with open("test.png", "wb") as f:
            #     thumbnail.seek(0)
            #     s = thumbnail.read()
            #     f.write(s)

            link = upload_user_document(Bucket.Documents, doc, file=file.file)
            update_document(
                doc,
                updates={
                    "text_search": text,
                    "file.link": link,
                    "thumbnail": FileMeta(
                        filename=f"{doc.file.filename}.thumbnail",
                        content_type=f"image/{THUMBNAIL_FORMAT}",
                        link=thumbnail_link,
                    ).model_dump(),
                },
            )
        except Exception as e:
            logger.warning(str(e))
            raise
        finally:
            file.file.close()

    task_id = str(uuid.uuid4())
    logger.info(f"queuing task_id: {task_id}")
    background_tasks.add_task(process_document, doc, task_id, file)

    return {"message": "ok", "document_id": doc.id}, 201

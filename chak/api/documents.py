from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, Query
from ..db.schema import UserAccount, Document, FileMeta
from ..api.auth import get_user
from ..db.repository import create_document, update_document, DocumentQuery
from ..image import process_ocr, generate_thumbnail
from ..storage import upload_user_document, upload_user_thumbnail
import typing as t
import logging
import io
import uuid

logger = logging.getLogger(__file__)

router = APIRouter()


@router.get("/")
def search_documents(query: t.Annotated[DocumentQuery, Depends(DocumentQuery)]):
    return {"documents": query(exclude={"text_search"})}


@router.post("/")
def submit_documents(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_account: UserAccount = Depends(get_user),
    title: str = Query(),
    tags: t.Optional[list[str]] = Query(default_factory=list),
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
            text = process_ocr(task_id, file.file)
            thumbnail = generate_thumbnail(task_id, file.file)
            thumbnail_link = upload_user_thumbnail(doc, file=thumbnail)
            # with open("test.png", "wb") as f:
            #     thumbnail.seek(0)
            #     s = thumbnail.read()
            #     f.write(s)

            link = upload_user_document(doc, file=file.file)
            update_document(
                doc,
                updates={
                    "text_search": text,
                    "file.link": link,
                    "file.thumbnail_link": thumbnail_link,
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

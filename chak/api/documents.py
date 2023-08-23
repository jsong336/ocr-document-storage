from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, Query
from ..db.schema import UserAccount, Document, FileMeta
from ..api.auth import get_user
from ..db.repository import create_document, update_document, DocumentQuery
from ..image import process_ocr as _process_ocr
from ..storage import upload_user_document
import typing as t
import logging
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

    def process_ocr(doc: Document, *args, **kw):
        try:
            text = _process_ocr(*args, **kw)
            link = upload_user_document(doc, file.file.read())
            update_document(doc, text_search=text, link=link)
        except Exception as e:
            logger.warning(str(e))
            raise
        finally:
            file.file.close()

    task_id = str(uuid.uuid4())
    logger.info(f"queuing task_id: {task_id}")
    background_tasks.add_task(process_ocr, doc, task_id, file.file)

    return {"message": "ok", "document_id": doc.id}, 201

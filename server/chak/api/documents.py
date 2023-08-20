from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from ..ocr import process_ocr as _process_ocr
import logging
import uuid

logger = logging.getLogger(__file__)

router = APIRouter()


@router.post("/")
def submit_documents(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
):
    for file in files:

        def process_ocr(*args, **kw) -> str:
            try:
                texts = _process_ocr(*args, **kw)

            except Exception:
                logger.warning()
            finally:
                file.file.close()

        task_id = str(uuid.uuid4())
        logger.info(f"queuing task_id: {task_id}")
        background_tasks.add_task(process_ocr, task_id, file.file)

    return {"message": "ok", "task_id": task_id}, 201

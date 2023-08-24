import pytesseract
import io
import logging
from PIL import Image


logger = logging.getLogger(__name__)
pytesseract.pytesseract.tesseract_cmd = "tesseract"
THUMBNAIL_SIZE = (500, 500)
THUMBNAIL_FORMAT = "png"


def process_ocr(task_id: str, data: io.BytesIO) -> str:
    img = Image.open(data)
    results = pytesseract.image_to_string(img)
    logging.info(f"processed ocr - {task_id}")
    return results


def generate_thumbnail(task_id: str, data: io.BytesIO) -> io.BytesIO:
    img = Image.open(data)
    img.thumbnail(THUMBNAIL_SIZE, Image.AFFINE)
    logging.info(f"generating thumbnails - {task_id}")

    file = io.BytesIO()
    img.save(file, format=THUMBNAIL_FORMAT)
    return file

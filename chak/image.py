import pytesseract
import io
import logging
from PIL import Image
from pillow_heif import register_heif_opener

logger = logging.getLogger(__name__)

pytesseract.pytesseract.tesseract_cmd = "tesseract"
register_heif_opener()

THUMBNAIL_SIZE = (500, 500)
THUMBNAIL_FORMAT = "png"


def process_ocr(task_id: str, img: Image) -> str:
    results = pytesseract.image_to_string(img)
    logging.info(f"processed ocr - {task_id}")
    return results


def generate_thumbnail(task_id: str, img: Image) -> io.BytesIO:
    img.thumbnail(THUMBNAIL_SIZE, Image.AFFINE)
    logging.info(f"generating thumbnails - {task_id}")

    file = io.BytesIO()
    img.save(file, format=THUMBNAIL_FORMAT)
    return file

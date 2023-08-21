import pytesseract
import io
import logging
from PIL import Image


logger = logging.getLogger(__name__)
pytesseract.pytesseract.tesseract_cmd = "tesseract"


def process_ocr(task_id: str, data: io.BytesIO) -> str:
    img = Image.open(data)
    results = pytesseract.image_to_string(img)
    logging.info(f"processed ocr - {task_id}")
    return results

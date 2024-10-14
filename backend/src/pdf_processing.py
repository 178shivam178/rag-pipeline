import pytesseract
from pathlib import Path
from pdf2image import convert_from_path
import platform
import logging

class PDFProcessingError(Exception):
    def __init__(self, message: str, details: str = ""):
        super().__init__(message)
        self.details = details

def get_pdf_text(pdf_path: Path) -> list:
    # Set up Tesseract path
    system_name = platform.system()
    if system_name == "Windows":
        pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"
        poppler_path = "dependency/poppler-21.11.0/Library/bin"
    elif system_name == "Linux":
        poppler_path = "/usr/bin"
    elif system_name == "Darwin":
        pytesseract.pytesseract.tesseract_cmd = r"/usr/local/bin/tesseract"
        poppler_path = "/usr/local/bin"
    else:
        raise PDFProcessingError("Unsupported operating system")

    if not pdf_path.suffix.lower() == '.pdf':
        raise PDFProcessingError("The provided file is not a PDF")

    all_text = []
    try:
        pages = convert_from_path(pdf_path, poppler_path=poppler_path)
    except Exception as e:
        logging.error(f"Error converting PDF to images: {str(e)}")
        raise PDFProcessingError('Failed to convert PDF to images', str(e))

    for page_num, img_blob in enumerate(pages, start=1):  # Page numbering starts from 1
        try:
            text = pytesseract.image_to_string(img_blob, lang='eng')
            all_text.append((page_num, text))  # Store tuple of page number and text
        except Exception as e:
            logging.error(f"Error extracting text from page {page_num}: {str(e)}")
            raise PDFProcessingError(f'Failed to extract text from page {page_num}', str(e))

    return all_text  # Return list of (page_num, text) tuples

def PDFProcessing(pdf_filepath: str) -> dict:
    try:
        pdf_path = Path(pdf_filepath)
        raw_text = get_pdf_text(pdf_path)
        return {'pages': raw_text}  # Return a dictionary with pages as key
    except PDFProcessingError as e:
        logging.error(f"PDF Processing Error: {e}")
        return {'error': str(e), 'details': e.details}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return {'error': 'An error occurred', 'details': str(e)}

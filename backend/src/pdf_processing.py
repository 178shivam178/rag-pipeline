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
    # Set up Poppler path for Linux
    if platform.system() == "Linux":
        poppler_path = "/usr/bin"  # Default path for poppler utils on Ubuntu
    else:
        raise PDFProcessingError("Unsupported operating system for this setup")

    if not pdf_path.suffix.lower() == '.pdf':
        raise PDFProcessingError("The provided file is not a PDF")

    all_text = []
    try:
        # Convert PDF pages to images
        pages = convert_from_path(pdf_path, poppler_path=poppler_path)
    except Exception as e:
        logging.error(f"Error converting PDF to images: {str(e)}")
        raise PDFProcessingError('Failed to convert PDF to images', str(e))

    for page_num, img_blob in enumerate(pages, start=1):  # Page numbering starts from 1
        try:
            # Extract text from image using Tesseract
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

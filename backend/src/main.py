# main.py

from pathlib import Path
import os
from pdf_processing import PDFProcessing, PDFProcessingError
from embedding_classification import process_and_store_text, save_data

def process_pdf_and_store_embeddings(pdf_filepath: str):
    try:
        result = PDFProcessing(pdf_filepath)
        
        if 'error' in result:
            print(f"Error processing PDF: {result['error']}, Details: {result['details']}")
            return
        
        pages_text = result.get('pages', [])
        for page_num, text in pages_text:
            print("page no: ",page_num)
            print(f"Processing page {page_num}...")
            process_and_store_text(text, page_number=page_num)
        save_data()

    except PDFProcessingError as e:
        print(f"PDF Processing Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    pdf_filepath = "uploads/IGBC_Green_New_Buildings_Rating_System_(Version_3.0_with_Fifth_Addendum).pdf"  

    if not Path(pdf_filepath).is_file():
        print(f"File not found: {pdf_filepath}")
    else:
        process_pdf_and_store_embeddings(pdf_filepath)

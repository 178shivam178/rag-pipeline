import openai
import faiss
import numpy as np
import pickle
from dotenv import load_dotenv
import os
from typing import List, Dict
from flask import Flask, request, jsonify
from src.pdf_processing import PDFProcessing, PDFProcessingError
from src.embedding_classification import process_and_store_text, save_data

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize FAISS index and document store
embedding_dim = 1536 
index = faiss.read_index("db/faiss_index.bin")

with open("db/document_store.pkl", "rb") as f:
    document_store = pickle.load(f)

app = Flask(__name__)

def get_openai_embedding(text: str) -> List[float]:
    try:
        response = openai.Embedding.create(input=[text], model="text-embedding-ada-002")
        return response['data'][0]['embedding']
    except Exception as e:
        raise Exception(f"Error in getting embedding: {str(e)}")

def query_top_chunk(text: str) -> Dict[str, any]:
    try:
        embedding = get_openai_embedding(text)
        embedding_np = np.array([embedding], dtype='float32')
        distances, indices = index.search(embedding_np, 1)
        
        idx = indices[0][0]
        chunk, metadata = document_store[idx]
        
        top_chunk = {
            "chunk": chunk,
            "credit_type": metadata['credit_type'],
            "distance": float(distances[0][0]),
            "page_number": metadata.get('page_number', 'N/A')  
        }
        
        return top_chunk
    except Exception as e:
        raise Exception(f"Error in querying top chunk: {str(e)}")

def generate_best_answer(user_query: str, top_chunk: Dict[str, any]) -> str:
    try:
        messages = [
            {"role": "system", "content": "You are an expert in green building practices and standards."},
            {"role": "user", "content": f"The user asked: '{user_query}'."},
            {"role": "assistant", "content": f"Relevant Chunk (Credit Type: {top_chunk['credit_type']}, Distance: {top_chunk['distance']}, Page: {top_chunk['page_number']}):\n{top_chunk['chunk']}"}
        ]
        
        messages.append({
            "role": "user", 
            "content": "Now, based on the information above, please provide the best answer."
        })

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        raise Exception(f"Error in generating answer: {str(e)}")

def process_pdf_and_store_embeddings(pdf_filepath: str):
    try:
        result = PDFProcessing(pdf_filepath)
        
        if 'error' in result:
            return {"error": f"Error processing PDF: {result['error']}, Details: {result['details']}"}
        
        pages_text = result.get('pages', [])
        for page_num, text in pages_text:
            print(f"Processing page {page_num}...")
            process_and_store_text(text, page_number=page_num)
        
        save_data()
        
        # Reload updated FAISS index and document store
        global index, document_store
        index = faiss.read_index("db/faiss_index.bin")

        with open("db/document_store.pkl", "rb") as f:
            document_store = pickle.load(f)

        return {"success": True, "message": "PDF processed and embeddings stored successfully."}
        
    except PDFProcessingError as e:
        return {"error": f"PDF Processing Error: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

@app.route("/v1/query", methods=["POST"])
def query():
    """API endpoint to get the top result and best answer."""
    try:
        data = request.json
        user_query = data.get('user_query')

        if not user_query:
            return jsonify({"error": "user_query is required"}), 400

        top_chunk = query_top_chunk(user_query)

        best_answer = generate_best_answer(user_query, top_chunk)
        return jsonify({
            "top_chunk": top_chunk,
            "best_answer": best_answer
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/v1/upload_pdf", methods=["POST"])
def upload_pdf():
    """API endpoint to upload a PDF and process it."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected for uploading"}), 400

        if not file.filename.endswith('.pdf'):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        upload_folder = "uploads/"
        os.makedirs(upload_folder, exist_ok=True)
        pdf_filepath = os.path.join(upload_folder, file.filename)
        file.save(pdf_filepath)

        result = process_pdf_and_store_embeddings(pdf_filepath)

        return jsonify(result), 200 if "success" in result else 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3008)

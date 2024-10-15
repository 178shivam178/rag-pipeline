# embedding_classification.py

import openai
import faiss
import numpy as np
import pickle
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

embedding_dim = 1536 
index = faiss.IndexFlatL2(embedding_dim)  
document_store = []

def clear_existing_store():
    """Reset document_store and FAISS index."""
    global document_store
    document_store = []  
    index.reset()  

clear_existing_store()

def split_text_into_chunks(text: str, chunk_size: int = 300) -> List[str]:
    words = text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def classify_chunk_with_gpt(chunk: str) -> str:
    prompt = f"""
    You are a green building expert. The following text is part of a green building certification document. 
    Classify the text into one of the following categories: 
    1. Energy Efficiency
    2. Water Conservation
    3. Sustainable Materials
    4. Indoor Environmental Quality
    5. General (if it doesn't fit in any of the above)
    
    Here is the text: {chunk}
    
    Respond with only the category name.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  
        messages=[
            {"role": "system", "content": "You are a classification assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    classification = response['choices'][0]['message']['content'].strip()
    valid_categories = ["Energy Efficiency", "Water Conservation", "Sustainable Materials", "Indoor Environmental Quality", "General"]
    
    if classification in valid_categories:
        return classification.lower().replace(" ", "_") 
    else:
        return "general"  

def get_openai_embedding(text: str) -> List[float]:
    response = openai.Embedding.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']

def process_and_store_text(text: str, page_number: int):
    chunks = split_text_into_chunks(text)
    
    for idx, chunk in enumerate(chunks):
        print(f"Processing chunk {idx + 1}/{len(chunks)} from page {page_number}...")
        embedding = get_openai_embedding(chunk) 
        credit_type = classify_chunk_with_gpt(chunk) 
        print(f"Classified as: {credit_type}")

        embedding_np = np.array(embedding, dtype='float32')
        index.add(np.array([embedding_np])) 
        document_store.append((chunk, {"credit_type": credit_type, "page_number": page_number}))

    print("Document embeddings and metadata stored successfully.")

def save_data():
    os.makedirs("db", exist_ok=True)
    faiss.write_index(index, "db/faiss_index.bin")
    print("FAISS index saved to disk.")
    with open("db/document_store.pkl", "wb") as f:
        pickle.dump(document_store, f)
    print("Document store saved to disk.")

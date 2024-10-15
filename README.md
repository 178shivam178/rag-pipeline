# Green Building RAG Application

This project implements a **Retrieval-Augmented Generation (RAG)** system for answering questions based on a dataset of green building PDF documents. It uses **Tesseract OCR** to extract text from PDFs, classifies the text into different categories using **LLM models**, and generates answers to user queries via a **Streamlit UI**.

## Live Project

You can access the live application [here](https://20.39.198.211:8501/)


## Features

- **PDF Text Extraction**:
  - PDFs are processed using **Tesseract OCR** to extract the text from each page.
  - The extracted text is split into 300-character chunks for further processing.

- **Classification**:
  - Each text chunk is classified into one of the following categories using a **prompt-based LLM model**:
    1. Energy Efficiency
    2. Water Conservation
    3. Sustainable Materials
    4. Indoor Environmental Quality
    5. General (for text that doesn't fit any of the above categories)

- **Embeddings & Metadata Storage**:
  - For each text chunk, the following metadata is stored:
    - Classification type
    - Page number
    - Embeddings
  - The embeddings and metadata are stored in a **vector index** for efficient querying.

- **Query API**:
  - A REST API is available for querying the model. It fetches the top relevant text chunks based on the embeddings and classification type, then passes them to the **LLM** to generate answers.

- **Chatbot UI**:
  - A **Streamlit-based chatbot interface** allows users to upload PDFs, ask questions, and get responses based on the document’s content and classification.

- **PDF Replacement**:
  - If a new PDF is uploaded, the system processes the document, generates embeddings, updates the database, and the chatbot will answer questions based on the new content.

## Project Setup

### Prerequisites

- Python 3.10
- Docker (optional, for running via Docker Compose)

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/178shivam178/rag-pipeline.git
    cd rag-pipeline
    ```

2. **Create a virtual environment**:
    ```bash
    python3.10 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies**:

   - Backend dependencies:
     ```bash
     cd backend
     pip install -r requirements.txt
     ```

   - Frontend dependencies:
     ```bash
     cd ../frontend
     pip install -r requirements.txt
     ```

4. **Run the Backend**:
    ```bash
    cd backend
    python api.py
    ```

5. **Run the Frontend (Streamlit UI)**:
    ```bash
    cd ../frontend
    streamlit run UI.py
    ```

### Optional: Run with Docker Compose

If you prefer to use Docker, you can run the application with Docker Compose:

```bash
docker-compose up

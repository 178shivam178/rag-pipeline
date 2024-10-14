import streamlit as st
import requests
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

UPLOAD_PDF_URL = os.getenv('UPLOAD_PDF_URL')
QUERY_URL = os.getenv('QUERY_URL')

st.set_page_config(page_title="Green Building Chatbot", layout="wide")  
st.title("Green Building Chatbot")

with st.container():
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        st.header("Upload PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
        if st.button("Process PDF"):
            if uploaded_file is not None:
                pdf_data = BytesIO(uploaded_file.read())
                files = {'file': (uploaded_file.name, pdf_data, 'application/pdf')}
                
                response = requests.post(UPLOAD_PDF_URL, files=files)
                if response.status_code == 200:
                    st.success("PDF uploaded and processed successfully!")
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error occurred.')}")
            else:
                st.warning("Please upload a PDF file.")

    with col2:
        st.header("Chat with the Bot")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_query = st.text_input("Ask a question about green building:")
        
        if st.button("Send"):
            if user_query:
                response = requests.post(QUERY_URL, json={"user_query": user_query})
                if response.status_code == 200:
                    data = response.json()
                    best_answer = data["best_answer"]
                    relevant_chunk = data.get("top_chunk")  
                    st.session_state.chat_history.append({
                        "user": user_query,
                        "bot": best_answer,
                        "top_chunk": relevant_chunk 
                    })
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error occurred.')}")

        if st.session_state.chat_history:
            for chat in st.session_state.chat_history:
                st.write(f"**User:** {chat['user']}")
                st.write(f"**Bot:** {chat['bot']}")
                st.write("---")

    with col3:
        st.header("Relevant Chunks")
        if st.session_state.chat_history:
            last_chat = st.session_state.chat_history[-1]
            last_chunk = last_chat.get("top_chunk")  

            if last_chunk:  # Check if last_chunk exists
                st.write(f"**Credit Type:** {last_chunk['credit_type']}")
                st.write(f"**Page Number:** {last_chunk['page_number']}")
                st.write(f"**Chunk:** {last_chunk['chunk']}")
            else:
                st.write("No relevant chunks available.")
        else:
            st.write("No relevant chunks to display.")

import streamlit as st
import time
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
import os
import requests
import uuid
from langchain.llms.ollama import Ollama

llm_model = "llama3.2:latest"
chroma_client = chromadb.PersistentClient(path=os.path.join(os.getcwd(), "chroma_db"))
collection = chroma_client.get_or_create_collection(name="docs_collection")


class SentenceTransformerEmbeddingFunction:
    def __init__(self, sentence_model):
        self.sentence_model = sentence_model

    def __call__(self, input):
        if isinstance(input, str):
            input = [input]
        return self.sentence_model.encode(input, convert_to_tensor=True).tolist()

sentence_transformer_model = SentenceTransformer('all-MiniLM-L6-v2')

def query_ollama(prompt):
    llm = Ollama(model=llm_model)
    return llm.invoke(prompt)

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file and clean formatting."""
    pdf_reader = PdfReader(uploaded_file)
    text = []
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text.replace("\n", " "))  
    return " ".join(text)


def upload_document(file,content):
    try:
        embedding = sentence_transformer_model.encode(content).tolist()
        doc_id = str(uuid.uuid4())
        collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[{"file_name": file.name}]
        )

        progress_bar = st.progress(0)
        for perc_completed in range(100):
            time.sleep(0.05)
            progress_bar.progress(perc_completed+1)
        st.success(f"File '{file.name}' successfully added.")
    except Exception as e:
        st.error(f"Error processing the file: {e}")

def display_documents():
    global collection
    docs = collection.get()
    if not docs["documents"]:  
        st.write("No saved documents found.")
        return

    for i, doc in enumerate(docs["documents"]):
        st.write(f"### Document {i + 1}")
        st.write(f"**Metadata:** {docs['metadatas'][i]}")
        st.write(f"**Content Preview:** {doc[:1000]}...") 
    if st.button(f"🗑 Delete all documents"):
        chroma_client.delete_collection(name="docs_collection")
        collection = chroma_client.get_or_create_collection(name="docs_collection")
        st.info("deleted!")

def google_search(query):
    """Perform a Google search using SerpAPI."""
    API_KEY = "437c9e22d88c1a62067b7e41fd39b00cf2c252308db785f284e8407008578079"  
    url = f"https://serpapi.com/search.json?q={query}&api_key={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json().get("organic_results", [])
        if results:
            return "\n".join(item.get("snippet", "No snippet available.") for item in results)
        return "No results found."
    except Exception as e:
        st.error(f"Error searching Google: {e}")
        return ""

def analyze_uploaded_file(content, query_text):
    """Generate an AI response using the uploaded file content as context."""
    augmented_prompt = f"Context: {content}\n\nQuestion: {query_text}\nAnswer:"
    response = query_ollama(augmented_prompt)
    return response

def delete_all_documents():
    all_docs = collection.get(include=['ids'])
    doc_ids = all_docs['ids']
    if doc_ids:
        collection.delete(ids=doc_ids)

def main():
    st.set_page_config(page_title="AI Assistant", layout="wide")
    st.title("AI-Powered Assistant")
    tab1, tab2, tab3 = st.tabs(["📂 Document Analysis", "🌐 Web Search", "🤖Chatbot"])
    
    with tab1:
        st.header("Upload a Document and Ask a Question")
        uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf"])

        if st.button("Add Documents"):
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension == "txt":
                content = uploaded_file.read().decode("utf-8")
            elif file_extension == "pdf":
                content = extract_text_from_pdf(uploaded_file)
            else:
                st.error("Unsupported file type.")
                return
            upload_document(uploaded_file, content)
        

        """Showing documents"""
        with st.expander("📁 Saved Documents"):
            display_documents()
        query_text = st.text_input("Enter your question here...")

        if st.button("Submit Document Query"):
            if collection.count()>0 and query_text:
                with st.spinner("Processing your file..."):
                    try:
                        response = analyze_uploaded_file(collection.get(), query_text)
                        st.markdown("AI Response:")
                        st.info(response)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.error("Please upload a file and enter a question to proceed.")

            
    
    with tab2:
        st.header("Search the Web for Context and Ask a Question")
        user_input = st.text_input("Ask a question for web-based context:")
        
        if st.button("Submit Web Search Query"):
            if user_input:
                with st.spinner("Searching the web..."):
                    context = google_search(user_input)
                    
                    if context:
                        prompt = f"Context:\n{context}\n\nQuestion:\n{user_input}\nAnswer:"
                        try:
                            response = query_ollama(prompt)
                            st.markdown("### 🌍 AI Response from Web Context:")
                            st.info(response)
                        except Exception as e:
                            st.error(f"Error with LLM response: {e}")
            else:
                st.error("Please enter a question to proceed.")
    with tab3:
        st.header("ChatBot")
        prompt = st.chat_input("Ask anything...")
        if "messages" not in st.session_state:
            st.session_state.messages = []
        for message in st.session_state.messages:
            with st.chat_message(message["role"]): 
                st.markdown(message["content"])

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            response = query_ollama(prompt)

            st.session_state.messages.append({"role": "assistant", "content": response})

            with st.chat_message("assistant"):
                st.markdown(response)


if __name__ == "__main__":
    main()

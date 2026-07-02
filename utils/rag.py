import os

from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer

from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from google import genai


# ---------------------------------------
# Load Gemini API Key
# ---------------------------------------

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=API_KEY)

DB_ROOT = "vector_db"

os.makedirs(DB_ROOT, exist_ok=True)


# ---------------------------------------
# Embedding Model
# ---------------------------------------

class LocalEmbeddings(Embeddings):

    def __init__(self):
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def embed_documents(self, texts):
        return self.model.encode(texts).tolist()

    def embed_query(self, text):
        return self.model.encode(text).tolist()


embedding_model = LocalEmbeddings()


# ---------------------------------------
# Create Vector Store
# ---------------------------------------

def create_vector_store(text, document_name):

    db_path = os.path.join(DB_ROOT, document_name)

    # ------------------------------------
    # If database already exists,
    # DO NOT recreate it.
    # ------------------------------------

    if os.path.exists(db_path):

        return db_path

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_text(text)

    Chroma.from_texts(
        texts=chunks,
        embedding=embedding_model,
        persist_directory=db_path
    )

    return db_path


# ---------------------------------------
# Ask Question using RAG
# ---------------------------------------

def ask_rag(question, db_path):

    db = Chroma(
        persist_directory=db_path,
        embedding_function=embedding_model
    )

    docs = db.similarity_search(
        question,
        k=4
    )

    if not docs:

        return "No relevant information found."

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    prompt = f"""
You are a Cybersecurity Compliance Assistant.

Answer ONLY from the provided context.

If the answer is not available, reply:

"The document does not contain this information."

Context:
{context}

Question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
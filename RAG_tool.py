import os
from datetime import datetime
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import tool
from dotenv import load_dotenv
from retrieval import retrieve_answer  
load_dotenv()
# SAFE LOADERS FOR WINDOWS
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)


QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")


# ------------------------------FILE LOADER SELECTION (safe for Windows)------------------------------ 

def load_file(file_path: str):
    ext = file_path.lower()

    if ext.endswith(".pdf"):
        return PyPDFLoader(file_path).load()

    if ext.endswith(".txt"):
        return TextLoader(file_path).load()

    if ext.endswith(".docx"):
        return Docx2txtLoader(file_path).load()

    raise ValueError(f"Unsupported file type: {file_path}")



#------------------------------ INGESTION PIPELINE------------------------------

def ingest_documents(folder_path: str,
                     chunk_size: int = 1000,
                     chunk_overlap: int = 200):
    print(" Starting ingestion pipeline...")

    all_chunks = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if not os.path.isfile(file_path):
            continue

        print(f" Loading: {filename}")

        docs = load_file(file_path)
        print(f" Extracted {len(docs)} raw documents")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = splitter.split_documents(docs)

        print(f" Chunked into {len(chunks)} pieces")

        timestamp = datetime.now().isoformat()
        for c in chunks:
            c.metadata["source"] = filename
            c.metadata["created_at"] = timestamp

        all_chunks.extend(chunks)

    embeddings = OpenAIEmbeddings()

    print(" Saving vectors into Qdrant...")
    Qdrant.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        path="./Data/qdrant_db",
        collection_name="company_docs",
    )

    print("✅ Ingestion Complete!")
    return f"Ingestion complete — {len(all_chunks)} chunks added."


# --------------------------------RAG TOOL – Called by LangChain Agent--------------------------------

@tool
def rag_tool(query: str) -> str:
    """RAG tool: retrieves relevant chunks + summary."""
    print(f"\n🟦 RAG TOOL CALLED → {query}")

    try:
        result = retrieve_answer(query)
        return (
            f"📘 DOCUMENT ANSWER:\n\n{result['summary']}\n\n"
            f"🔹 Total chunks used: {result['total_chunks_found']}\n"
            f"🔹 Embedding dimension: {result['embedding_dimension']}\n"
        )
    except Exception as e:
        return f"❌ RAG ERROR: {e}"



#------------------------------ INGEST TOOL WRAPPER------------------------------

@tool
def ingest_tool(folder_path: str) -> str:
    """Uploads all documents from a folder into Qdrant."""
    return ingest_documents(folder_path)



# from qdrant_client import QdrantClient

# qdrant_client = QdrantClient(
#     url="https://9e721394-6117-418a-9fc2-8880bd99e156.eu-central-1-0.aws.cloud.qdrant.io:6333", 
#     api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.ENeyah4sXizQxeuGLemOoGIbGEHNKClA7puw-A3vhJI",
# )

# print(qdrant_client.get_collections()) 
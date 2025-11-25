import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import Distance, VectorParams
from qdrant_client import QdrantClient
from dotenv import load_dotenv
load_dotenv()


class VectorStoreManager:
    def __init__(self, folder_path="Data/documents_used", collection_name="company_docs", 
                 chunk_size=1000, chunk_overlap=200):
        """Initialize the Vector Store Manager."""
        self.folder_path = folder_path
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.client = None
        self.vector_store = None

    def load_documents(self):
        """Load PDF, TXT, DOCX files."""
        try:
            print("\n Loading documents...\n")

            if not os.path.exists(self.folder_path):
                raise FileNotFoundError(f"Folder not found: {self.folder_path}")

            loaders = []

            for file in os.listdir(self.folder_path):
                full = os.path.join(self.folder_path, file)

                if file.endswith(".pdf"):
                    loaders.append(PyPDFLoader(full))
                elif file.endswith(".txt"):
                    loaders.append(TextLoader(full, encoding="utf-8"))
                elif file.endswith(".docx"):
                    loaders.append(Docx2txtLoader(full))

            if not loaders:
                raise ValueError(f"No supported documents found in {self.folder_path}")

            documents = []
            for loader in loaders:
                try:
                    docs = loader.load()
                    print(f" Loaded: {loader.file_path}")
                    documents.extend(docs)
                except Exception as e:
                    print(f" Error loading {loader}: {e}")

            if not documents:
                raise ValueError("No documents were successfully loaded")

            print(f"\n Loaded {len(documents)} raw documents")
            return documents
        
        except Exception as e:
            print(f" Error in load_documents: {e}")
            raise

    def chunk_documents(self, documents):
        """Split documents into chunks."""
        try:
            if not documents:
                raise ValueError("No documents provided for chunking")
            
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
            chunks = splitter.split_documents(documents)

            if not chunks:
                raise ValueError("Failed to create chunks from documents")

            print(f" Split into {len(chunks)} chunks")
            return chunks
        
        except Exception as e:
            print(f" Error in chunk_documents: {e}")
            raise

    def create_vectorstore(self, chunks):
        """Create Qdrant vector store and add document chunks."""
        try:
            if not chunks:
                raise ValueError("No chunks provided for vector store creation")
            
            if not self.qdrant_url or not self.qdrant_api_key:
                raise ValueError("Qdrant URL and API key must be set in environment variables")
            
            # Connect to Qdrant with URL and API key
            self.client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key
            )

            # Get vector size from embeddings
            vector_size = len(self.embeddings.embed_query("sample text"))

            # Create collection if it doesn't exist
            if not self.client.collection_exists(self.collection_name):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )
                print(f" Created new collection: {self.collection_name}")
            else:
                print(f" Collection {self.collection_name} already exists")

            # Initialize vector store and add documents
            self.vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embedding=self.embeddings,
            )
            
            # Add chunks to vector store
            print(f"\n Adding {len(chunks)} chunks to Qdrant...")
            self.vector_store.add_documents(chunks)
            print(" Successfully stored embeddings in Qdrant!")
            
            return self.vector_store
        
        except Exception as e:
            print(f" Error in create_vectorstore: {e}")
            raise

    def setup(self):
        """Run the complete setup pipeline."""
        try:
            documents = self.load_documents()
            chunks = self.chunk_documents(documents)
            vector_store = self.create_vectorstore(chunks)
            print("\n Vector store setup complete!")
            return vector_store
        
        except Exception as e:
            print(f"\n Setup failed: {e}")
            raise


if __name__ == "__main__":
    try:
        # Initialize and run vector store manager
        manager = VectorStoreManager()
        manager.setup()
    except Exception as e:
        print(f"\n Failed to complete vector store setup: {e}")




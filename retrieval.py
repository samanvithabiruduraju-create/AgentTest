import os
from typing import Optional, List, Dict
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

# Constants from .env
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class VectorRetriever:
    """
    Vector Retriever relevant Tool for fetching similar documents from Qdrant Vector Store.
    """
    def __init__(self, collection_name: str = "company_docs", num_docs: int = 4, similarity: float = 0.6):
        self.collection_name = collection_name
        self.num_docs = num_docs
        self.similarity = similarity

        """Constructor method that runs when you create a new VectorRetriever object."""
        
        # Initialize embeddings and vectorstore
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=OPENAI_API_KEY)
        vectorstore = QdrantVectorStore.from_existing_collection(
            embedding=embeddings,
            collection_name=self.collection_name,
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY
        )

        """vectorstore: A storage system that holds vectors (numerical representations of data) for efficient retrieval."""

        self.retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": self.num_docs, "score_threshold": self.similarity}
        )

        """Converts text into numerical vectors (arrays of numbers) that capture meaning."""

        
    def retrieve(self, query: str) -> List[Dict[str, str]]:
        try:
            # Use LangChain retriever
            results = self.retriever.invoke(query)
            
            if not results:
                print(f"No Context related to you queryyyyy!!!")
                return [{"context": ""}]

            context = []
            for doc in results:
                context.append({"context": doc.page_content})
            
            print(f"Context:\n{context}")
            return context

        except Exception as e:
            print(f"Error during retrieval: {e}")
            return None
        
# if __name__ == "__main__":
#     retriever = VectorRetriever()
    
#     print("Vector Retrieval System Welocmes you Alwaysssss!!")
#     print("Type 'exit' or 'quit' to stop\n")
    
#     while True:
#         query = input("Enter your question: ").strip()
        
#         if query.lower() in ['exit', 'quit', 'q']:
#             print("Goodboiiiiiiiiiii.....!!!!!!!!")
#             break
        
#         if not query:
#             print("You may ask your Queryyy I can Answer.\n")
#             continue
        
#         print(f"\nSearching for: {query}")
#         results = retriever.retrieve(query)
#         print("-" * 80 + "\n")
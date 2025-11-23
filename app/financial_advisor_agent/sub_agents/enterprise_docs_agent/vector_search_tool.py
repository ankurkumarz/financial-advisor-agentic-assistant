import os
import uuid
from typing import Any, Dict, List, Optional
from pypdf import PdfReader
import chromadb
from chromadb.utils import embedding_functions
from ...utils.logger import setup_logger 

logger = setup_logger(__name__)

class VectorSearchTool:
    def __init__(
        self,
        collection_name: str = "financial_documents",
        db_path: str = "./chroma_db",
        top_k: int = 5,
        api_key: Optional[str] = None
    ) -> None:
        self.collection_name = collection_name
        self.top_k = top_k
        
        # 1. Google Native Embedding
        self.embedding_fn = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
            api_key=api_key or os.getenv("GEMINI_API_KEY"),
            model_name="models/text-embedding-004",
            task_type="RETRIEVAL_DOCUMENT"
        )
        
        # 2. Persistent Client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # 3. Collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name, 
            embedding_function=self.embedding_fn
        )

    def is_empty(self) -> bool:
        """Checks if the collection has any documents."""
        return self.collection.count() == 0

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Simple sliding window chunker."""
        if not text: return []
        chunks = []
        start = 0
        while start < len(text):
            chunks.append(text[start : start + chunk_size])
            start += (chunk_size - overlap)
        return chunks

    def load_documents_from_folder(self, folder_path: str) -> int:
        if not os.path.exists(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            return 0
            
        total_chunks = 0
        logger.info(f"📂 scanning folder: {folder_path}")
        
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            full_text = ""
            
            try:
                if filename.lower().endswith(".pdf"):
                    reader = PdfReader(file_path)
                    for page in reader.pages:
                        full_text += page.extract_text() + "\n"
                
                elif filename.lower().endswith(".json"):
                    import json
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Convert JSON to string representation for embedding
                        full_text = json.dumps(data, indent=2)
                else:
                    continue

                text_chunks = self._chunk_text(full_text)
                if not text_chunks: continue

                # Generate IDs and Metadata
                ids = [f"{filename}_{i}_{str(uuid.uuid4())[:8]}" for i in range(len(text_chunks))]
                metadatas = [{"source": filename, "chunk_index": i} for i in range(len(text_chunks))]
                
                self.collection.add(
                    documents=text_chunks,
                    metadatas=metadatas,
                    ids=ids
                )
                total_chunks += len(text_chunks)
                print(f"   ✅ Indexed {filename} ({len(text_chunks)} chunks)")
                
            except Exception as e:
                logger.error(f"Error reading {filename}: {e}")
                    
        return total_chunks

    def search(self, query: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """
        Search for relevant documents using semantic similarity.

        Args:
            query: The search query
            top_k: Number of results to return (defaults to self.top_k)

        Returns:
            Dictionary containing search results with documents, metadata, and distances
        """
        if top_k is None:
            top_k = self.top_k

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )

            # Format results for the agent
            if not results or not results.get('documents') or not results['documents'][0]:
                return {
                    "found": False,
                    "message": "No relevant documents found.",
                    "results": []
                }

            formatted_results = []
            documents = results['documents'][0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]

            for idx, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                formatted_results.append({
                    "rank": idx + 1,
                    "content": doc,
                    "source": metadata.get('source', 'Unknown'),
                    "chunk_index": metadata.get('chunk_index', 0),
                    "relevance_score": 1 - distance  # Convert distance to similarity score
                })

            return {
                "found": True,
                "query": query,
                "total_results": len(formatted_results),
                "results": formatted_results
            }

        except Exception as e:
            logger.error(f"Error during vector search: {e}")
            return {
                "found": False,
                "error": str(e),
                "message": "Error occurred during search.",
                "results": []
            }
        
    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Returns the tool definition in Google ADK format.
        The agent will use this to understand how to call the tool.
        """
        return {
            "name": "search_documents",
            "description": (
                "Search internal financial documents using semantic similarity. "
                "Returns relevant document chunks with source information and relevance scores. "
                "Use this tool to find information about financial products, policies, regulations, and company guidelines."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find relevant documents. Use specific terms and questions."
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of document chunks to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            },
            "handler": self.search
        }
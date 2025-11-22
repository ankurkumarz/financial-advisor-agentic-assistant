"""Knowledge Retriever Agent - Agentic RAG with ChromaDB."""
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from typing import Dict, Any
from financial_advisor_agent.config import settings
from financial_advisor_agent.utils import setup_logger
from google.genai import types
from .prompt import ENTERPRISE_DOCS_AGENT_PROMPT
from .vector_search_tool import VectorSearchTool

logger = setup_logger(__name__)

# --- 1. Initialize the Tool ---
# This connects to the database folder "./chroma_db"
search_tool = VectorSearchTool(
    collection_name=settings.chroma_collection_name,
    db_path=settings.chroma_persist_directory
)

def create_financial_enterprise_docs_agent() -> Agent:
    """Create the Knowledge Retriever Agent using Google ADK."""
    return Agent(
        name="financial_enterprise_docs_agent",
        model=settings.vertex_ai_model,
        instruction=ENTERPRISE_DOCS_AGENT_PROMPT,
        tools=[
            FunctionTool(
                func=search_tool.search
            )
        ],
        output_key="retrieval_result",
        generate_content_config=types.GenerateContentConfig(
          temperature=settings.retriever_temperature
        )
    )

def initialize_knowledge_base():
    """
    Runs at startup. Checks if DB is empty. If so, loads PDFs.
    """
    if search_tool.is_empty():
        logger.info("📉 Database is empty. Starting initial PDF ingestion...")
        
        count = search_tool.load_documents_from_folder(settings.chroma_pdf_folder)
        
        if count > 0:
            logger.info(f"🎉 Success! Loaded {count} text chunks into ChromaDB.")
        else:
            logger.warning("⚠️ No documents found or loaded.")
    else:
        # If documents exist, we skip loading to save time/money
        doc_count = search_tool.collection.count()
        logger.info(f"✅ Database ready. Contains {doc_count} chunks. Skipping ingestion.")


initialize_knowledge_base()
financial_enterprise_docs_agent = create_financial_enterprise_docs_agent()
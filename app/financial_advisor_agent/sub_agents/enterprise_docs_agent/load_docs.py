from ...config import settings
from ...utils import setup_logger
from .vector_search_tool import VectorSearchTool

logger = setup_logger(__name__)


# --- 1. Initialize the Tool ---
search_tool = VectorSearchTool(
    collection_name=settings.chroma_collection_name,
    db_path=settings.chroma_persist_directory
)

def initialize_knowledge_base():
    """
    Runs at startup. Checks if DB is empty. If so, loads Docs.
    """
    if search_tool.is_empty():
        logger.info("📉 Database is empty. Starting initial PDF ingestion...")
        
        # 1. Load local docs
        count = search_tool.load_documents_from_folder(settings.chroma_docs_folder)

        # 2. Load Kaggle Dataset
        # try:
        #     #import kagglehub
        #     #logger.info("⬇️ Downloading Kaggle dataset...")
        #     #path = kagglehub.dataset_download("tuc111/financial-guidance-generator-investment-strategy")
            
        #     kaggle_count = search_tool.load_documents_from_folder(path)
        #     count += kaggle_count
            
        # except Exception as e:
        #     logger.error(f"❌ Failed to load Kaggle dataset: {e}")
        
        if count > 0:
            logger.info(f"🎉 Success! Loaded {count} text chunks into ChromaDB.")
        else:
            logger.warning("⚠️ No documents found or loaded.")
    else:
        # If documents exist, we skip loading to save time/money
        doc_count = search_tool.collection.count()
        logger.info(f"✅ Database ready. Contains {doc_count} chunks. Skipping ingestion.")

"""Knowledge Retriever Agent - Agentic RAG with ChromaDB."""
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool
from typing import Dict, Any
from ...config import settings
from ...utils import setup_logger
from google.genai import types
from .prompt import ENTERPRISE_DOCS_AGENT_PROMPT
from .load_docs import initialize_knowledge_base, search_tool

logger = setup_logger(__name__)

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

def create_financial_enterprise_docs_agent() -> Agent:
    """Create the Knowledge Retriever Agent using Google ADK."""
    return Agent(
        name="financial_enterprise_docs_agent",
        model=Gemini(model=settings.vertex_ai_model, retry_options=retry_config),
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

initialize_knowledge_base()
financial_enterprise_docs_agent = create_financial_enterprise_docs_agent()
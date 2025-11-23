"""Main entry point for the FA³AI multi-agent system."""
import os
import logging
from typing import Optional
from google.adk.cli.fast_api import get_fast_api_app
from fastapi import FastAPI
from app.financial_advisor_agent import root_agent
from app.financial_advisor_agent.config import settings

# Configure logging directly since utils is empty
logging.basicConfig(level=settings.log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Create FastAPI app with cloud tracing for future use
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    trace_to_cloud=False,
)

app.title = "financial-advisor-agentic"
app.description = "API for interacting with the Agent Financial Advisor Agent"

def main():
    """Main entry point for running the FastAPI application."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

# Main execution
if __name__ == "__main__":
    main()
"""Knowledge Orchestrator Agent - Main LLM orchestrator using Google ADK."""
from google.adk.agents import Agent, LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import AgentTool, FunctionTool
from typing import Dict, Any, List, Optional
from google.genai import types
from google.genai import types
import asyncio
from .config import settings
from .utils import setup_logger
from .prompt import FINANCIAL_ADVISOR_PROMPT
from .sub_agents.enterprise_docs_agent import financial_enterprise_docs_agent
from .sub_agents.google_research_agent import google_research_agent
from .sub_agents.crm_leads_insights_agent import crm_leads_insights_agent
from .sub_agents.compliance_checker_agent import compliance_checker_agent

logger = setup_logger(__name__)

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

def create_financial_advisor_agent() -> Agent:
    """
    Create the main Financial Advisor Agent acting as a Knowledge Orchestrator with sub-agents.
    This agent uses sub-agents as tools to help advisors find the right information, assist with their queries, and internal information & research.
    Returns:
        The orchestrator agent with sub-agents wrapped as tools
    """
    return LlmAgent(
        name="financial_advisor_agent",
        model=Gemini(model=settings.vertex_ai_model, retry_options=retry_config),
        description=(
           "guide advisorss through a structured process to their financial queries"
           "by orchestrating a series of expert subagents. help them "
           "analyze their queries, retrieve relevant enterprise information from the knowledge base and CRM system "
           "providing comprehensive, personalized responses."
        ),
        tools=[
            AgentTool(agent=financial_enterprise_docs_agent),
            AgentTool(agent=google_research_agent),
            AgentTool(agent=crm_leads_insights_agent),
            AgentTool(agent=compliance_checker_agent)
        ],
        instruction = FINANCIAL_ADVISOR_PROMPT,
        output_key="financial_advisor_output",
    )


root_agent = create_financial_advisor_agent()
"""Knowledge Orchestrator Agent - Main LLM orchestrator using Google ADK."""
from google.adk.agents import Agent, LlmAgent
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

logger = setup_logger(__name__)

def create_financial_advisor_agent() -> Agent:
    """
    Create the main Financial Advisor Agent acting as a Knowledge Orchestrator with sub-agents.
    This agent coordinates all sub-agents by calling them as tools.
    
    Args:
        planner_agent: The knowledge planner agent
        retriever_agent: The knowledge retriever agent
        reviewer_agent: The content reviewer agent
    
    Returns:
        The orchestrator agent with sub-agents wrapped as tools
    """
    return LlmAgent(
        name="financial_advisor_agent",
        model=settings.vertex_ai_model,
        description=(
           "guide advisorss through a structured process to their financial queries"
           "by orchestrating a series of expert subagents. help them "
           "analyze their queries, retrieve relevant enterprise information from the knowledge base and CRM system "
           "providing comprehensive, personalized responses."
        ),
        tools=[
            AgentTool(agent=financial_enterprise_docs_agent),
            #AgentTool(agent=crm_prospects_insights_agent),
            #AgentTool(agent=compliance_checker_agent)
        ],
        instruction = FINANCIAL_ADVISOR_PROMPT,
        output_key="financial_advisor_output",
    )


root_agent = create_financial_advisor_agent()
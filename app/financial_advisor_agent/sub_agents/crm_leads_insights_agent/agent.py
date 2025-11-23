from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types
from google.adk.tools import FunctionTool
from ...config import settings
from ...utils import setup_logger
from .prompt import CRM_LEADS_INSIGHTS_AGENT_PROMPT
from .tools import crm_dataframe_tool

logger = setup_logger(__name__)

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

logger.info("Creating CRM Leads Insights Agent with model as: {}".format(settings.vertex_ai_model))

crm_leads_insights_agent = LlmAgent(
    name="crm_leads_insights_agent",
    model=Gemini(model=settings.vertex_ai_model, retry_options=retry_config),
    description="Insights agent for CRM Leads and Prospects",
    instruction=CRM_LEADS_INSIGHTS_AGENT_PROMPT,
           tools=[
            FunctionTool(
                func=crm_dataframe_tool.query_dataframe
            )
        ],
)
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types
from ...config import settings
from ...utils import setup_logger
from google.adk.tools.google_search_tool import google_search
from .prompt import GOOGLE_RESEARCH_AGENT_PROMPT

logger = setup_logger(__name__)

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

logger.info("Creating Google Research Agent with model as: {}".format(settings.vertex_ai_research_model))

google_research_agent = LlmAgent(
    name="google_research_agent",
    model=Gemini(model=settings.vertex_ai_research_model, retry_options=retry_config),
    description="Researcher for information using Google search",
    instruction=GOOGLE_RESEARCH_AGENT_PROMPT,
    tools=[google_search]
)
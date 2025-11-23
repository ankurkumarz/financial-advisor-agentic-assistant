from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types
from ...config import settings
from ...utils import setup_logger
from google.adk.tools import FunctionTool
from google.adk.tools.google_search_tool import google_search
from .prompt import COMPLIANCE_CHECKER_AGENT_PROMPT
from .compliance_checklist_tool import compliance_checklist_tool
from .disclaimer_template_tool import disclaimer_template_tool

logger = setup_logger(__name__)

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

logger.info("Creating Compliance Checker Agent with model as: {}".format(settings.vertex_ai_compliance_model))

# Initialize compliance tools
compliance_tools = [
    FunctionTool(
        func=compliance_checklist_tool.validate_compliance,
    ),
    FunctionTool(
        func=disclaimer_template_tool.generate_disclaimers,
    )
]

compliance_checker_agent = LlmAgent(
    name="compliance_checker_agent",
    model=Gemini(model=settings.vertex_ai_compliance_model, retry_options=retry_config),
    description="Compliance Checker for Advisors to ensure responses are complete, accurate, compliant with legal and regulatory standards including AI disclosure requirements",
    instruction=COMPLIANCE_CHECKER_AGENT_PROMPT,
    tools=compliance_tools
)
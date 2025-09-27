"""
Founder Profile Orchestrator Agent - Main Founding Team Verification Agent

This is the root agent that coordinates the multi-agent founder verification system.
It orchestrates query generation, search execution, analysis agents, and report generation.
"""

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import FunctionTool
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools.tool_context import ToolContext


from utils.configs import config
from utils.helper import (
    data_consolidation_after_model_callback,
)
from utils.logging_config import get_logger, log_callback_event

MODEL = config.get_model_for_agent("OLLAMA")

from tools.search_tool import (
    comprehensive_founder_search,
    concise_google_search,
    search_indian_news,
)

from . import prompt

logger = get_logger(__name__)

def after_model_callback_query_generator(callback_context: CallbackContext, llm_response: LlmResponse):
    log_callback_event("ended", "founder-query-generator", "agent")
    data_consolidation_after_model_callback("founder_query_generation", callback_context, llm_response)


def create_query_generator_agent():
    """Create a fresh instance of the query generator agent."""
    return Agent(
        model=MODEL,
        name="query_generator",
        description="Generates targeted search queries for founder claim verification with India-specific focus",
        instruction=prompt.QUERY_GENERATOR_INSTRUCTION,
        tools=[FunctionTool(concise_google_search), FunctionTool(search_indian_news)],
        before_agent_callback=log_callback_event("started", "query-generator", "agent"),
        generate_content_config=types.GenerateContentConfig(
            temperature=config.TEMPERATURE,
        ),
        include_contents="default",
        output_key="search_evidence",  # Store generated queries under this key
        after_model_callback=after_model_callback_query_generator,
    )

def after_model_callback_data_analyst(callback_context: CallbackContext, llm_response: LlmResponse):
    log_callback_event("started", "founder-data-analyst", "agent")
    data_consolidation_after_model_callback("founder_data_analysis", callback_context, llm_response)


def create_data_analyst_agent():
    """Create a fresh instance of the data analyst agent."""
    return Agent(
        model=MODEL,
        name="data_analyst",
        description="Analyzes founder claims against search results and generates verification KPIs with India-specific assessment",
        instruction=prompt.DATA_ANALYST_INSTRUCTION,
        tools=[
            FunctionTool(comprehensive_founder_search),
            FunctionTool(concise_google_search),
            FunctionTool(search_indian_news),
        ],
        before_agent_callback=log_callback_event(
            "started", "founder-data_analyst","agent"
        ),
        generate_content_config=types.GenerateContentConfig(
            temperature=config.TEMPERATURE,
        ),
        include_contents="default",
        output_key="founder_analysis",
        after_model_callback=after_model_callback_data_analyst,
    )

def after_model_callback_fr(callback_context: CallbackContext, llm_response: LlmResponse):
    log_callback_event("started", "founder-report-synthesizer", "agent")
    data_consolidation_after_model_callback("founder_profile_report", callback_context, llm_response)

def create_founder_report_synthesizer():
    """Create a fresh instance of the founder report synthesizer."""
    return Agent(
        model=MODEL,
        name="founder_report_synthesizer",
        description="Synthesizes individual founder verification results into a comprehensive team assessment report",
        instruction=prompt.REPORT_SYNTHESIS_INSTRUCTION,
        before_agent_callback=log_callback_event("started", "founder_report_synthesizer", "agent"),
        after_agent_callback=after_model_callback_fr,
        generate_content_config=types.GenerateContentConfig(
            temperature=config.TEMPERATURE,  # Use configured temperature
        ),
        include_contents="default",
        output_key="founder_profile_report",
    )


# Report synthesis agent
founder_report_synthesizer = create_founder_report_synthesizer()


# Root orchestrator agent
def create_founder_profile_orchestrator():
    """Create a fresh instance of the founder profile orchestrator agent."""
    return SequentialAgent(
        name="founder_evaluation_pipeline",
        description="Sequential execution of founder verification, analysis, and report generation",
        before_agent_callback=log_callback_event("started", "founder_profile_orchestrator", "workflow"),
        sub_agents=[
            create_query_generator_agent(),  # First generate search queries
            create_data_analyst_agent(),  # Then analyze results (will use our search tools internally)
            create_founder_report_synthesizer(),  # Then synthesize team report
        ],
    )


founder_profile_agent = create_founder_profile_orchestrator()
# root_agent = founder_profile_agent

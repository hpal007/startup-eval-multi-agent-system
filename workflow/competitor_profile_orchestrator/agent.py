"""
Competitor Profile Orchestrator Agent - Main Competitive Analysis Agent

This is the root agent that coordinates the multi-agent competitor analysis system.
It orchestrates competitor extraction, market research, intelligence gathering, and report generation.
"""

from google.adk.agents import Agent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse

from agents.competitive_analysis.agent import competitive_analysis_agent
from agents.competitor_extractor.agent import create_competitor_extractor_agent
from agents.competitor_intelligence.agent import create_competitor_intelligence_agent
from agents.market_researcher.agent import create_market_researcher_agent
from agents.report_synthesis.agent import report_synthesis_agent
from utils.configs import config
from utils.helper import data_consolidation_after_model_callback
from utils.logging_config import get_logger, log_callback_event

MODEL = config.get_model_for_agent("abc_agent")

logger = get_logger(__name__)


def synthesis_callback(
    callback_context: CallbackContext, llm_response: LlmResponse | None = None, **kwargs
):
    """Callback to synthesize results from all competitor analyses."""
    log_callback_event("ended", "report_synthesis_pipeline_agent", "agent")
    data_consolidation_after_model_callback("competitor_report_synthesis", callback_context, llm_response)


def create_report_synthesis_pipeline_agent():
    """Create a fresh instance of the report synthesis pipeline agent."""
    return Agent(
        model=MODEL,
        name="report_synthesis_pipeline_agent",
        description="Generates comprehensive competitor profile reports with confidence scores, recommendations, and risk factor identification",
        instruction=report_synthesis_agent.instruction,
        tools=report_synthesis_agent.tools,
        before_agent_callback=log_callback_event("starting", "report_synthesis_pipeline_agent", "agent"),
        after_model_callback=synthesis_callback,
        generate_content_config=report_synthesis_agent.generate_content_config,
        include_contents=report_synthesis_agent.include_contents,
    )

def create_competitive_analysis_pipeline_agent():
    """Create a fresh instance of the competitive analysis pipeline agent."""
    return Agent(
        model=MODEL,
        name="competitive_analysis_pipeline_agent",
        description="Validates competitive advantage claims against market evidence and performs gap analysis to identify missing competitors",
        instruction=competitive_analysis_agent.instruction,
        tools=competitive_analysis_agent.tools,
        before_agent_callback=log_callback_event("starting", "competitive_analysis_pipeline_agent", "agent"),
        after_model_callback=competitive_analysis_agent.after_model_callback,
        generate_content_config=competitive_analysis_agent.generate_content_config,
        include_contents=competitive_analysis_agent.include_contents,
    )


def create_competitor_profile_orchestrator():
    """Create a fresh instance of the competitor profile orchestrator agent."""
    return SequentialAgent(
        name="competitor_evaluation_pipeline",
        description="Complete competitor analysis workflow: discovery → analysis → synthesis",
        before_agent_callback=log_callback_event("starting", "competitor_profile_orchestrator", "workflow"),
        sub_agents=[
            create_competitor_extractor_agent(),  # Stage 1: Extract mentioned competitors
            create_market_researcher_agent(),  # Stage 2: Discover unlisted competitors
            create_competitor_intelligence_agent(),  # Stage 3: Gather detailed intelligence
            create_competitive_analysis_pipeline_agent(),  # Analyze competitive landscape and validate claims
            create_report_synthesis_pipeline_agent(),  # Generate comprehensive competitor profile report
        ],
        after_agent_callback=log_callback_event("completed", "competitor_profile_orchestrator", "workflow"),
    )

# Root orchestrator agent
root_agent = create_competitor_profile_orchestrator()

# Enhanced report synthesis agent with progress tracking
report_synthesis_pipeline_agent = create_report_synthesis_pipeline_agent()
# Enhanced competitive analysis agent with progress tracking
competitive_analysis_pipeline_agent = create_competitive_analysis_pipeline_agent()
"""
Founder Profile Orchestrator Agent - Main Founding Team Verification Agent

This is the root agent that coordinates the multi-agent founder verification system.
It orchestrates query generation, search execution, analysis agents, and report generation.
"""

import logging

from google.adk.agents import Agent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.planners import PlanReActPlanner
from google.adk.tools import FunctionTool
from google.genai import types

from utils.configs import config
from utils.helper import get_session_dir, save_llm_response_to_file, save_state_to_file

MODEL = config.get_model_for_agent("abc_agent")


from tools.search_tool import (
    comprehensive_founder_search,
    concise_google_search,
    search_indian_news,
)

from . import prompt

logger = logging.getLogger(__name__)


def setup_orchestrator_callback(callback_context, **kwargs):
    """Setup callback for the founder profile orchestrator agent."""
    logger.info(
        "\n👑 Founder Profile Orchestrator: 🚀 Starting founding team verification workflow\n"
    )
    # Initialize any global state needed for founder verification


def synthesis_callback(callback_context: CallbackContext, llm_response: LlmResponse | None = None, **kwargs):
    """Callback to synthesize results from all founder analyses."""
    logger.info(
        "\n🤖 founder_report_synthesizer: Synthesizing verification results from all founders\n"
    )
    try:
        if not llm_response:
            logger.warning("⚠️ synthesis_callback called without an LlmResponse; skipping save.")
            return
        if llm_response.content and llm_response.content.parts:
            save_llm_response_to_file(
                filename="founder_verification_llm_response",
                llm_content=llm_response.content,
                session_path=get_session_dir(callback_context),
                file_type="md",
            )
        else:
            logger.warning("⚠️ No content in LlmResponse to save in synthesis_callback.")
    except Exception as e:
        logger.error(f"❌ Error saving LLM response in synthesis_callback: {e}")

    try:
        if callback_context.state:
            save_state_to_file(
                context=callback_context,
                session_path=get_session_dir(callback_context),
                filename="founder_verification_report_state",
                file_type="json",
            )
    except Exception as e:
        logger.error(f"❌ Error saving state in synthesis_callback: {e}")



def verification_pipeline_callback(callback_context, **kwargs):
    """Callback for verification pipeline progress."""
    logger.info(
        "\n🔄 verification_pipeline: Founder verification pipeline initiated - processing all founders\n"
    )


def query_generation_callback(callback_context, **kwargs):
    """Callback for query generation phase."""
    logger.info(
        "\n🔍 query_generator: Generating targeted search queries for founder verification\n"
    )


def data_analysis_callback(callback_context, **kwargs):
    """Callback for data analysis phase."""
    logger.info(
        "\n📊 data_analyst: Analyzing founder claims against search evidence with India-specific patterns\n"
    )


def create_query_generator_agent():
    """Create a fresh instance of the query generator agent."""
    return Agent(
        model=MODEL,
        name="query_generator",
        description="Generates targeted search queries for founder claim verification with India-specific focus",
        instruction=prompt.QUERY_GENERATOR_INSTRUCTION,
        tools=[FunctionTool(concise_google_search), FunctionTool(search_indian_news)],
        before_agent_callback=query_generation_callback,
        generate_content_config=types.GenerateContentConfig(
            temperature=config.TEMPERATURE,
        ),
        include_contents="default",
    )


query_generator_agent = create_query_generator_agent()


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
        before_agent_callback=data_analysis_callback,
        generate_content_config=types.GenerateContentConfig(
            temperature=config.TEMPERATURE,
        ),
        include_contents="default",
    )


data_analyst_agent = create_data_analyst_agent()


def create_verification_pipeline():
    """Create a fresh instance of the verification pipeline."""
    return SequentialAgent(
        name="verification_pipeline",
        description="Sequential execution of query generation and analysis for founder verification",
        sub_agents=[
            create_query_generator_agent(),  # First generate search queries
            create_data_analyst_agent(),  # Then analyze results (will use our search tools internally)
        ],
        before_agent_callback=verification_pipeline_callback,
    )


# Verification pipeline for sequential processing (simplified)
verification_pipeline = create_verification_pipeline()


def create_founder_report_synthesizer():
    """Create a fresh instance of the founder report synthesizer."""
    return Agent(
        model=MODEL,
        name="founder_report_synthesizer",
        description="Synthesizes individual founder verification results into a comprehensive team assessment report",
        instruction=prompt.REPORT_SYNTHESIS_INSTRUCTION,
        after_model_callback=synthesis_callback,
        generate_content_config=types.GenerateContentConfig(
            temperature=config.TEMPERATURE,  # Use configured temperature
        ),
        include_contents="default",
    )


# Report synthesis agent
founder_report_synthesizer = create_founder_report_synthesizer()


def create_founder_evaluation_pipeline():
    """Create a fresh instance of the founder evaluation pipeline."""
    return SequentialAgent(
        name="founder_evaluation_pipeline",
        description="Sequential execution of founder verification, analysis, and report generation",
        sub_agents=[
            create_verification_pipeline(),  # First verify all founders
            create_founder_report_synthesizer(),  # Then synthesize team report
        ],
    )


# Main founder evaluation pipeline
founder_evaluation_pipeline = create_founder_evaluation_pipeline()

# Root orchestrator agent
def create_founder_profile_orchestrator():
    """Create a fresh instance of the founder profile orchestrator agent."""
    return Agent(
        model=MODEL,
        name="founder_profile_orchestrator",
        description=(
            "Main orchestrator for founding team verification and analysis specialized for Indian startups. "
            "Coordinates India-specific query generation, multi-source search execution (Google + News API), "
            "comprehensive claim verification, and team assessment reporting with India-specific KPIs."
        ),
        instruction=prompt.ORCHESTRATOR_INSTRUCTION,
        # planner=PlanReActPlanner(),
        sub_agents=[create_founder_evaluation_pipeline()],
        before_agent_callback=setup_orchestrator_callback,
        after_agent_callback=synthesis_callback,
        # generate_content_config=types.GenerateContentConfig(
        #     temperature=config.TEMPERATURE,
        # ),
        include_contents="default",
        output_key="founder_verification_output",
    )

# Create a default instance for backward compatibility
founder_profile_agent = create_founder_profile_orchestrator()
# root_agent = founder_profile_agent

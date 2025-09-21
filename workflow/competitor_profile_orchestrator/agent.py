"""
Competitor Profile Orchestrator Agent - Main Competitive Analysis Agent

This is the root agent that coordinates the multi-agent competitor analysis system.
It orchestrates competitor extraction, market research, intelligence gathering, and report generation.
"""

import logging

from google.adk.agents import Agent, SequentialAgent
from google.adk.models import LlmResponse
from google.adk.planners import PlanReActPlanner
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from agents.competitive_analysis.agent import competitive_analysis_agent
from agents.competitor_extractor.agent import create_competitor_extractor_agent
from agents.competitor_intelligence.agent import create_competitor_intelligence_agent
from agents.market_researcher.agent import create_market_researcher_agent
from agents.report_synthesis.agent import report_synthesis_agent
from utils.configs import config
from utils.helper import get_session_dir, save_llm_response_to_file

from . import prompt

MODEL = config.get_model_for_agent("abc_agent")

logger = logging.getLogger(__name__)


def setup_orchestrator_callback(callback_context, **kwargs):
    """Setup callback for the competitor profile orchestrator agent."""
    logger.info(
        "\n🏢 Competitor Profile Orchestrator: 🚀 Starting competitive landscape analysis workflow\n"
    )
    # Initialize any global state needed for competitor analysis


def synthesis_callback(callback_context: CallbackContext , llm_response: LlmResponse):
    """Callback to synthesize results from all founder analyses."""
    logger.info(
        "\n🤖 founder_report_synthesizer: Synthesizing verification results from all founders\n"
    )
    try:
        if llm_response.content and llm_response.content.parts:
            save_llm_response_to_file(
                filename="founder_verification_report",
                llm_content=llm_response.content,
                session_path=get_session_dir(callback_context),
                file_type="md",
            )
        else:
            logger.warning("⚠️ No content in LlmResponse to save in synthesis_callback.")
    except Exception as e:
        logger.error(f"❌ Error saving LLM response in synthesis_callback: {e}")


def analysis_pipeline_callback(callback_context: CallbackContext, **kwargs):
    """Callback for competitor analysis pipeline progress."""
    logger.info(
        "\n🔄 competitor_analysis_pipeline: Competitor analysis pipeline initiated - processing competitive landscape\n"
    )
    logger.info("Pipeline stages: Competitive Analysis → Report Synthesis")


def competitive_analysis_progress_callback(callback_context, **kwargs):
    """Progress callback for competitive analysis phase."""
    logger.info(
        "\n🔍 Analysis Stage 1/2: Competitive Analysis - Validating claims and identifying gaps\n"
    )


def report_synthesis_progress_callback(callback_context, **kwargs):
    """Progress callback for report synthesis phase."""
    logger.info(
        "\n📊 Analysis Stage 2/2: Report Synthesis - Generating comprehensive competitor profile report\n"
    )


def competitor_discovery_pipeline_callback(callback_context, **kwargs):
    """Callback for competitor discovery pipeline progress tracking."""
    logger.info(
        "\n🔍 competitor_discovery_pipeline: Starting sequential competitor discovery process\n"
    )
    logger.info(
        "Pipeline stages: Extraction → Market Research → Intelligence Gathering"
    )


def competitor_extraction_progress_callback(callback_context, **kwargs):
    """Progress callback for competitor extraction phase."""
    logger.info(
        "\n📋 Stage 1/3: Competitor Extraction - Parsing mentioned competitors and claims\n"
    )


def market_research_progress_callback(callback_context, **kwargs):
    """Progress callback for market research phase."""
    logger.info(
        "\n🌐 Stage 2/3: Market Research - Discovering unlisted competitors through search\n"
    )


def intelligence_gathering_progress_callback(callback_context, **kwargs):
    """Progress callback for competitor intelligence gathering phase."""
    logger.info(
        "\n🕵️ Stage 3/3: Intelligence Gathering - Building detailed competitor profiles\n"
    )


def create_competitor_discovery_pipeline():
    """Create a fresh instance of the competitor discovery pipeline."""
    return SequentialAgent(
        name="competitor_discovery_pipeline",
        description="Sequential pipeline for comprehensive competitor discovery: extraction → research → intelligence",
        sub_agents=[
            create_competitor_extractor_agent(),  # Stage 1: Extract mentioned competitors
            create_market_researcher_agent(),  # Stage 2: Discover unlisted competitors
            create_competitor_intelligence_agent(),  # Stage 3: Gather detailed intelligence
        ],
        before_agent_callback=competitor_discovery_pipeline_callback,
    )


# Competitor Discovery Pipeline - Sequential execution of discovery agents
competitor_discovery_pipeline = create_competitor_discovery_pipeline()


def create_competitive_analysis_pipeline_agent():
    """Create a fresh instance of the competitive analysis pipeline agent."""
    return Agent(
        model=MODEL,
        name="competitive_analysis_pipeline_agent",
        description="Validates competitive advantage claims against market evidence and performs gap analysis to identify missing competitors",
        instruction=competitive_analysis_agent.instruction,
        tools=competitive_analysis_agent.tools,
        before_agent_callback=competitive_analysis_progress_callback,
        after_model_callback=competitive_analysis_agent.after_model_callback,
        generate_content_config=competitive_analysis_agent.generate_content_config,
        include_contents=competitive_analysis_agent.include_contents,
    )


# Enhanced competitive analysis agent with progress tracking
competitive_analysis_pipeline_agent = create_competitive_analysis_pipeline_agent()


def create_report_synthesis_pipeline_agent():
    """Create a fresh instance of the report synthesis pipeline agent."""
    return Agent(
        model=MODEL,
        name="report_synthesis_pipeline_agent",
        description="Generates comprehensive competitor profile reports with confidence scores, recommendations, and risk factor identification",
        instruction=report_synthesis_agent.instruction,
        tools=report_synthesis_agent.tools,
        before_agent_callback=report_synthesis_progress_callback,
        after_model_callback=report_synthesis_agent.after_model_callback,
        generate_content_config=report_synthesis_agent.generate_content_config,
        include_contents=report_synthesis_agent.include_contents,
    )


# Enhanced report synthesis agent with progress tracking
report_synthesis_pipeline_agent = create_report_synthesis_pipeline_agent()


def create_analysis_synthesis_pipeline():
    """Create a fresh instance of the analysis synthesis pipeline."""
    return SequentialAgent(
        name="analysis_synthesis_pipeline",
        description="Sequential pipeline for competitive analysis and report synthesis",
        sub_agents=[
            create_competitive_analysis_pipeline_agent(),  # Analyze competitive landscape and validate claims
            create_report_synthesis_pipeline_agent(),  # Generate comprehensive competitor profile report
        ],
        before_agent_callback=analysis_pipeline_callback,
    )


# Analysis and Synthesis Pipeline - Sequential execution of analysis and reporting
analysis_synthesis_pipeline = create_analysis_synthesis_pipeline()


def create_competitor_evaluation_pipeline():
    """Create a fresh instance of the competitor evaluation pipeline."""
    return SequentialAgent(
        name="competitor_evaluation_pipeline",
        description="Complete competitor analysis workflow: discovery → analysis → synthesis",
        sub_agents=[
            create_competitor_discovery_pipeline(),  # First discover and profile competitors
            create_analysis_synthesis_pipeline(),  # Then analyze and synthesize results
        ],
    )


# Main competitor evaluation pipeline
competitor_evaluation_pipeline = create_competitor_evaluation_pipeline()


def create_competitor_profile_orchestrator():
    """Create a fresh instance of the competitor profile orchestrator agent."""
    return Agent(
        model=MODEL,
        name="competitor_profile_orchestrator",
        description=(
            "Main orchestrator for competitive landscape analysis and market validation. "
            "Coordinates competitor extraction, market research, intelligence gathering, "
            "competitive analysis, and comprehensive reporting for investment decision-making."
        ),
        instruction=prompt.ORCHESTRATOR_INSTRUCTION,
        planner=PlanReActPlanner(),
        sub_agents=[create_competitor_evaluation_pipeline()],
        before_agent_callback=setup_orchestrator_callback,
        # after_agent_callback=synthesis_callback,
        generate_content_config=types.GenerateContentConfig(
            temperature=config.TEMPERATURE,
        ),
        include_contents="default",
    )


# Root orchestrator agent
root_agent = create_competitor_profile_orchestrator()

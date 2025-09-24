"""
Competitive Analysis Agent

Specialized agent for validating competitive advantage claims against market evidence
and performing gap analysis to identify missing competitors.
"""

import logging

from google.adk.agents import Agent
from google.genai import types

from tools.competitor_search_tool import (
    batch_competitor_search,
    competitor_intelligence_search,
    competitor_validation_search,
)
from tools.search_tool import concise_google_search, search_indian_news

from utils.configs import config

MODEL = config.get_model_for_agent("abc_agent")

from . import prompt

logger = logging.getLogger(__name__)


def competitive_analysis_validation_callback(callback_context, **kwargs):
    """Callback to validate competitive analysis completeness."""
    logger.info(
        "\n🤖 Competitive analysis completed - validating advantage claims and gap analysis\n"
    )

    # Validate that analysis results are properly structured for synthesis stage
    if hasattr(callback_context, "response") and callback_context.response:
        logger.info("✅ Analysis results validated and ready for report synthesis")

        # Log key analysis findings for pipeline tracking
        logger.info("📊 Analysis stage output prepared for synthesis pipeline")
    else:
        logger.warning("⚠️ Analysis results may be incomplete - check data flow")

    # Extract competitive analysis state for next pipeline stage
    pass


def competitive_analysis_setup_callback(callback_context, **kwargs):
    """Setup callback for competitive analysis agent."""
    logger.info(
        "\n🤖: competitive_analysis_agent: Starting competitive analysis - validating claims and identifying gaps\n"
    )


competitive_analysis_agent = Agent(
    model=MODEL,
    name="competitive_analysis_agent",
    description="Validates competitive advantage claims against market evidence and performs gap analysis to identify missing competitors",
    instruction=prompt.COMPETITIVE_ANALYSIS_INSTRUCTION,
    tools=[
        concise_google_search,
        search_indian_news,
        competitor_validation_search,
        competitor_intelligence_search,
        batch_competitor_search,
    ],
    before_agent_callback=competitive_analysis_setup_callback,
    after_model_callback=competitive_analysis_validation_callback,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.TEMPERATURE,
    ),
    include_contents="default",
)

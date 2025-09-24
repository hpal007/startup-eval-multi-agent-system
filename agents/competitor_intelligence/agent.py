"""
Competitor Intelligence Agent

Specialized agent for gathering detailed competitor profiles and market positioning.
Adapts comprehensive_founder_search tool for competitor intelligence gathering.
"""

import logging

from google.adk.agents import Agent
from google.genai import types

from tools.competitor_search_tool import (
    batch_competitor_search,
    competitor_funding_search,
    competitor_intelligence_search,
    competitor_leadership_search,
    competitor_validation_search,
)
from tools.search_tool import (
    comprehensive_founder_search,
    concise_google_search,
    search_indian_news,
)

from utils.configs import config

MODEL = config.get_model_for_agent("abc_agent")

from . import prompt

logger = logging.getLogger(__name__)


# TODO - use single callbacks for all agents
def competitor_intelligence_validation_callback(callback_context, **kwargs):
    """Callback to validate competitor intelligence gathering completeness."""
    logger.info(
        "\n🤖 Competitor intelligence gathering completed - validating profile data\n"
    )
    # Extract intelligence gathering state if needed
    pass


def competitor_intelligence_setup_callback(callback_context, **kwargs):
    """Setup callback for competitor intelligence agent."""
    logger.info(
        "\n🤖: competitor_intelligence_agent: Starting competitor intelligence gathering - building detailed profiles\n"
    )


def create_competitor_intelligence_agent():
    """Create a fresh instance of the competitor intelligence agent."""
    return Agent(
        model=MODEL,
        name="competitor_intelligence_agent",
        description="Gathers detailed competitor intelligence profiles and market positioning using adapted search tools",
        instruction=prompt.COMPETITOR_INTELLIGENCE_INSTRUCTION,
        tools=[
            concise_google_search,
            search_indian_news,
            comprehensive_founder_search,
            competitor_intelligence_search,
            competitor_validation_search,
            competitor_funding_search,
            competitor_leadership_search,
            batch_competitor_search,
        ],
        before_agent_callback=competitor_intelligence_setup_callback,
        after_model_callback=competitor_intelligence_validation_callback,
        generate_content_config=types.GenerateContentConfig(
            temperature=config.TEMPERATURE,
        ),
        include_contents="default",
    )


competitor_intelligence_agent = create_competitor_intelligence_agent()

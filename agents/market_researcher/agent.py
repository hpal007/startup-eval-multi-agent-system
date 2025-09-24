"""
Market Researcher Agent

Specialized agent for discovering unlisted competitors through comprehensive market research.
Uses search tools to identify direct, indirect, and substitute competitors not mentioned by the startup.
"""

import logging

from google.adk.agents import Agent
from google.genai import types

from tools.competitor_search_tool import (
    batch_competitor_search,
    competitor_intelligence_search,
    competitor_market_search,
)
from tools.search_tool import (
    comprehensive_founder_search,
    concise_google_search,
    search_indian_news,
)

from utils.configs import config

from . import prompt

logger = logging.getLogger(__name__)
MODEL = config.get_model_for_agent("abc_agent")


def market_research_validation_callback(callback_context, **kwargs):
    """Callback to validate market research completeness."""
    logger.info(
        "\n🤖 Market research completed - validating competitor discovery results\n"
    )
    # Extract market research state if needed
    pass


def market_research_setup_callback(callback_context, **kwargs):
    """Setup callback for market researcher agent."""
    logger.info(
        "\n🤖: market_researcher_agent: Starting market research - discovering unlisted competitors\n"
    )


def create_market_researcher_agent():
    """Create a fresh instance of the market researcher agent."""
    return Agent(
        model=MODEL,
        name="market_researcher_agent",
        description="Discovers unlisted competitors through comprehensive market research using search tools",
        instruction=prompt.MARKET_RESEARCHER_INSTRUCTION,
        tools=[
            concise_google_search,
            search_indian_news,
            comprehensive_founder_search,
            competitor_market_search,
            competitor_intelligence_search,
            batch_competitor_search,
        ],
        before_agent_callback=market_research_setup_callback,
        after_model_callback=market_research_validation_callback,
        generate_content_config=types.GenerateContentConfig(
            temperature=config.TEMPERATURE,
        ),
        include_contents="default",
    )


market_researcher_agent = create_market_researcher_agent()

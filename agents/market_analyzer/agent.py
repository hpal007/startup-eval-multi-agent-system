"""
Market Analysis Agent

Specialized agent for analyzing target markets, competitive landscape, and market opportunities.
Evaluates market size, growth potential, competition, and go-to-market strategy.
"""

import logging

from google.adk.agents import Agent
from google.genai import types

from utils.configs import config

from . import prompt

logger = logging.getLogger(__name__)

MODEL = config.get_model_for_agent("abc_agent")


def market_validation_callback(callback_context, **kwargs):
    """Callback to validate market analysis completeness."""
    logger.info(
        "\n🤖 Market analysis completed - validating competitive landscape results\n"
    )
    # Extract market analysis state if needed
    pass


def market_setup_callback(callback_context, **kwargs):
    """Setup callback for market analyzer agent."""
    logger.info(
        "\n🤖: market_analyzer_agent: Starting market analysis - evaluating competitive landscape\n"
    )


market_analyzer_agent = Agent(
    model=MODEL,
    name="market_analyzer_agent",
    description="Analyzes target markets, competitive landscape, and market opportunities",
    instruction=prompt.MARKET_ANALYZER_INSTRUCTION,
    before_agent_callback=market_setup_callback,
    after_model_callback=market_validation_callback,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.TEMPERATURE,
    ),
    include_contents="default",
)

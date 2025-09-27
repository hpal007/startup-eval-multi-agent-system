"""
Market Size Validator Agent

Specialized agent for validating startup TAM/SAM/SOM claims against authoritative market research sources.
Compares startup market size claims with data from reputable sources like Gartner, Forrester, and industry reports.
"""

import logging

from google.adk.agents import Agent
from google.genai import types

from tools.market_research_tools import (
    comprehensive_market_research,
    funding_validation_search,
    industry_report_search,
    market_size_validation_search,
)
from tools.market_validation_tools import (
    assess_data_recency,
    calculate_confidence_score,
    calculate_market_variance,
    extract_market_data_from_search,
    identify_discrepancy_flags,
    validate_tam_sam_som_logic,
)
from tools.search_tool import concise_google_search, search_indian_news
from utils.configs import config

MODEL = config.get_model_for_agent("abc_agent")

from . import prompt

logger = logging.getLogger(__name__)


def market_validation_callback(callback_context, **kwargs):
    """Callback to validate market size validation completeness."""
    logger.info(
        "\n🤖 Market size validation completed - reviewing validation results\n"
    )
    # Extract validation state if needed
    pass


def market_validation_setup_callback(callback_context, **kwargs):
    """Setup callback for market size validator agent."""
    logger.info(
        "\n🤖: market_size_validator_agent: Starting market size validation - comparing claims with authoritative sources\n"
    )


market_size_validator_agent = Agent(
    model=MODEL,
    name="market_size_validator_agent",
    description="Validates startup TAM/SAM/SOM claims against authoritative market research sources",
    instruction=prompt.MARKET_SIZE_VALIDATOR_INSTRUCTION,
    tools=[
        concise_google_search,
        search_indian_news,
        market_size_validation_search,
        industry_report_search,
        funding_validation_search,
        comprehensive_market_research,
        calculate_market_variance,
        assess_data_recency,
        calculate_confidence_score,
        identify_discrepancy_flags,
        extract_market_data_from_search,
        validate_tam_sam_som_logic,
    ],
    before_agent_callback=market_validation_setup_callback,
    after_model_callback=market_validation_callback,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.TEMPERATURE,
    ),
    include_contents="default",
)

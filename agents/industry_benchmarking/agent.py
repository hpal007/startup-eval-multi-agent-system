"""
Industry Benchmarking Agent

Specialized agent for comparing startup KPIs against industry benchmarks and peer performance.
Provides percentile rankings, performance gap analysis, and improvement recommendations.
"""

import logging

from google.adk.agents import Agent
from google.genai import types

from utils.configs import config
from tools.search_tool import concise_google_search, search_indian_news
from tools.market_research_tools import (
    industry_benchmark_search,
    industry_report_search,
    comprehensive_market_research
)
from tools.industry_benchmarking_tools import (
    calculate_percentile_ranking,
    analyze_performance_gaps,
    generate_improvement_recommendations,
    calculate_industry_position,
    validate_exceptional_performance,
    correlate_market_trends,
    generate_typical_ranges_context
)

MODEL = config.get_model_for_agent("abc_agent")

from . import prompt

logger = logging.getLogger(__name__)


def industry_benchmarking_callback(callback_context, **kwargs):
    """Callback to validate industry benchmarking analysis completeness."""
    logger.info(
        "\n🤖 Industry benchmarking analysis completed - reviewing performance comparisons\n"
    )
    # Extract benchmarking state if needed
    pass


def industry_benchmarking_setup_callback(callback_context, **kwargs):
    """Setup callback for industry benchmarking agent."""
    logger.info(
        "\n🤖: industry_benchmarking_agent: Starting industry benchmarking analysis - comparing KPIs against industry standards\n"
    )


industry_benchmarking_agent = Agent(
    model=MODEL,
    name="industry_benchmarking_agent",
    description="Compares startup KPIs against industry benchmarks and peer performance",
    instruction=prompt.INDUSTRY_BENCHMARKING_INSTRUCTION,
    tools=[
        concise_google_search,
        search_indian_news,
        industry_benchmark_search,
        industry_report_search,
        comprehensive_market_research,
        calculate_percentile_ranking,
        analyze_performance_gaps,
        generate_improvement_recommendations,
        calculate_industry_position,
        validate_exceptional_performance,
        correlate_market_trends,
        generate_typical_ranges_context
    ],
    before_agent_callback=industry_benchmarking_setup_callback,
    after_model_callback=industry_benchmarking_callback,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.TEMPERATURE,
    ),
    include_contents="default",
)
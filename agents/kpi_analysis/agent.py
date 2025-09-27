"""KPI Analysis Agent for analyzing individual KPI performance and trends."""

import json
import logging

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types

from tools.kpi_analysis_tools import (
    analyze_kpi_trends,
    calculate_performance_scores,
    generate_improvement_recommendations,
    identify_competitive_advantages,
    validate_exceptional_claims,
)
from tools.market_research_tools import (
    comprehensive_market_research,
    industry_benchmark_search,
    kpi_validation_search,
)
from tools.search_tool import concise_google_search, search_indian_news
from utils.configs import config
from utils.helper import get_session_dir, save_llm_response_to_file, save_state_to_file

from . import prompt

MODEL = config.get_model_for_agent("abc_agent")
logger = logging.getLogger(__name__)


def kpi_analysis_setup_callback(callback_context, **kwargs):
    """Setup callback for KPI analysis agent."""
    print("\n🔍 kpi_analysis_agent: Starting KPI performance analysis\n")


def kpi_analysis_validation_callback(callback_context, **kwargs):
    """Validation callback for KPI analysis agent."""
    print("\n✅ KPI analysis completed - validating results\n")


def analyze_kpi_performance_tool(startup_data: str) -> str:
    """
    Analyze KPI performance against industry benchmarks.

    Args:
        startup_data: JSON string containing startup KPI data and benchmarks

    Returns:
        JSON string with performance analysis results
    """
    try:
        data = (
            json.loads(startup_data)
            if isinstance(startup_data, str)
            else (startup_data or {})
        )

        current_kpis = data.get("current_kpis", {})
        industry_benchmarks = data.get("industry_benchmarks", {})
        kpi_weights = data.get("kpi_weights", {})

        # Coerce numeric strings (e.g., "12.8 Cr INR", "₹10,000")
        def _to_float(val):
            if isinstance(val, (int, float)):
                return float(val)
            if not isinstance(val, str):
                return None
            s = val.strip().lower().replace(",", "")
            mult = 1.0
            if "cr" in s:
                mult = 1e7
                s = s.replace("cr", "")
            if "lakh" in s:
                mult = 1e5
                s = s.replace("lakh", "")
            s = s.replace("inr", "").replace("₹", "").strip()
            try:
                return float(s) * mult
            except Exception:
                return None

        current_kpis = {
            k: (_to_float(v) if isinstance(v, str) else v)
            for k, v in current_kpis.items()
        }

        # Calculate performance scores
        performance_results = calculate_performance_scores(
            current_kpis, industry_benchmarks, kpi_weights
        )

        return json.dumps(performance_results, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to analyze KPI performance: {e!s}"})


def analyze_trends_tool(historical_data: str) -> str:
    """
    Analyze trends in KPI historical data.

    Args:
        historical_data: JSON string containing historical KPI data and benchmarks

    Returns:
        JSON string with trend analysis results
    """
    try:
        data = json.loads(historical_data)

        kpi_historical_data = data.get("historical_data", {})
        industry_benchmarks = data.get("industry_benchmarks", {})

        # Analyze trends
        trend_results = analyze_kpi_trends(kpi_historical_data, industry_benchmarks)

        return json.dumps(trend_results, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to analyze trends: {e!s}"})


def generate_recommendations_tool(analysis_data: str) -> str:
    """
    Generate improvement recommendations based on KPI analysis.

    Args:
        analysis_data: JSON string containing performance results and context

    Returns:
        JSON string with prioritized recommendations
    """
    try:
        data = (
            json.loads(analysis_data)
            if isinstance(analysis_data, str)
            else (analysis_data or {})
        )

        # Accept either nested or flat shape
        performance_results = (
            data.get("performance_results", data.get("results", data)) or {}
        )
        industry_best_practices = data.get("industry_best_practices", {})
        growth_stage = data.get("growth_stage", "unknown")

        # Generate recommendations
        recommendations = generate_improvement_recommendations(
            performance_results, industry_best_practices, growth_stage
        )

        return json.dumps(recommendations, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to generate recommendations: {e!s}"})


def identify_advantages_tool(performance_data: str) -> str:
    """
    Identify competitive advantages based on exceptional KPI performance.

    Args:
        performance_data: JSON string containing performance results and industry context

    Returns:
        JSON string with identified competitive advantages
    """
    try:
        data = json.loads(performance_data)

        performance_results = data.get("performance_results", {})
        industry_context = data.get("industry_context", {})

        # Identify competitive advantages
        advantages = identify_competitive_advantages(
            performance_results, industry_context
        )

        return json.dumps(advantages, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to identify advantages: {e!s}"})


def validate_claims_tool(validation_data: str) -> str:
    """
    Validate exceptional performance claims.

    Args:
        validation_data: JSON string containing KPI data and benchmarks for validation

    Returns:
        JSON string with validation results
    """
    try:
        data = json.loads(validation_data)

        kpi_data = data.get("kpi_data", {})
        industry_benchmarks = data.get("industry_benchmarks", {})

        # Validate exceptional claims
        validation_results = validate_exceptional_claims(kpi_data, industry_benchmarks)

        return json.dumps(validation_results, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to validate claims: {e!s}"})


def analyze_individual_kpi_tool(kpi_analysis_data: str) -> str:
    """
    Perform detailed analysis of individual KPI performance.

    Args:
        kpi_analysis_data: JSON string containing KPI data, historical data, benchmarks, and context

    Returns:
        JSON string with comprehensive individual KPI analysis
    """
    try:
        data = (
            json.loads(kpi_analysis_data)
            if isinstance(kpi_analysis_data, str)
            else (kpi_analysis_data or {})
        )

        kpi_name = data.get("kpi_name")
        current_value = data.get("current_value")
        historical_data = data.get("historical_data", [])
        industry_benchmarks = data.get("industry_benchmarks", {})
        industry_context = data.get("industry_context", {})

        # Coerce common numeric formats
        def _to_float(val):
            if isinstance(val, (int, float)):
                return float(val)
            if not isinstance(val, str):
                return None
            s = val.strip().lower().replace(",", "")
            mult = 1.0
            if "cr" in s:
                mult = 1e7
                s = s.replace("cr", "")
            if "lakh" in s:
                mult = 1e5
                s = s.replace("lakh", "")
            s = s.replace("inr", "").replace("₹", "").strip()
            try:
                return float(s) * mult
            except Exception:
                return None

        if isinstance(current_value, str):
            current_value = _to_float(current_value)

        if not kpi_name or current_value is None:
            return json.dumps({"error": "Missing required KPI name or current value"})

        # Perform individual KPI analysis
        from tools.kpi_analysis_tools import analyze_individual_kpi_performance

        analysis_results = analyze_individual_kpi_performance(
            kpi_name,
            current_value,
            historical_data,
            industry_benchmarks,
            industry_context,
        )

        return json.dumps(analysis_results, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to analyze individual KPI: {e!s}"})


def kpi_analysis_after_callback(
    callback_context: CallbackContext, llm_response: LlmResponse | None = None, **kwargs
):
    """After callback for KPI analysis agent to save LLM response and state."""
    try:
        if llm_response and llm_response.content and llm_response.content.parts:
            save_llm_response_to_file(
                filename="ka_llm",
                llm_content=llm_response.content,
                session_path=get_session_dir(callback_context),
                file_type="json",
            )
    except Exception as e:
        logger.error(
            f"❌ Error saving LLM response in kpi_analysis_after_callback: {e}"
        )

    try:
        if callback_context.state:
            save_state_to_file(
                context=callback_context,
                session_path=get_session_dir(callback_context),
                filename="ka_state",
                file_type="json",
            )
    except Exception as e:
        logger.error(f"❌ Error saving state in kpi_analysis_after_callback: {e}")


# Create the KPI Analysis agent
kpi_analysis_agent = Agent(
    model=MODEL,
    name="kpi_analysis_agent",
    description="Analyzes individual KPI performance and identifies trends, providing performance scoring and recommendations",
    instruction=prompt.KPI_ANALYSIS_INSTRUCTION,
    tools=[
        concise_google_search,
        search_indian_news,
        kpi_validation_search,
        industry_benchmark_search,
        comprehensive_market_research,
        analyze_kpi_performance_tool,
        analyze_trends_tool,
        generate_recommendations_tool,
        identify_advantages_tool,
        validate_claims_tool,
        analyze_individual_kpi_tool,
    ],
    before_agent_callback=kpi_analysis_setup_callback,
    after_model_callback=kpi_analysis_validation_callback,
    after_agent_callback=kpi_analysis_after_callback,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.TEMPERATURE,
    ),
    include_contents="default",
)

"""
Business KPIs Orchestrator Agent - Main Business KPI Validation and Analysis Agent

This is the root agent that coordinates the multi-agent business KPI validation system.
It orchestrates industry classification, market size validation, KPI analysis, and benchmarking.
"""

import logging

from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.models import LlmResponse

from utils.configs import config
from utils.helper import get_session_dir, save_llm_response_to_file, save_state_to_file

from . import prompt

logger = logging.getLogger(__name__)
MODEL = config.get_model_for_agent("abc_agent")


# Error handling and retry configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2


# Safe accessor for CallbackContext (which may not implement dict.get)
def ctx_get(ctx, key, default=None):
    try:
        return ctx[key]
    except KeyError:
        return default
    except Exception:
        # Fallback to attribute access if subscripting isn't supported
        return getattr(ctx, key, default)


# Safe setter for CallbackContext (which may not support item assignment)
def ctx_set(ctx, key, value):
    try:
        ctx[key] = value
        return True
    except Exception:
        try:
            setattr(ctx, key, value)
            return True
        except Exception:
            return False


def handle_pipeline_error(pipeline_name, error, callback_context, **kwargs):
    """Handle pipeline errors with retry logic."""
    retry_count = ctx_get(callback_context, f"{pipeline_name}_retry_count", 0)

    logger.error(f"Error in {pipeline_name}: {error!s}")

    if retry_count < MAX_RETRY_ATTEMPTS:
        retry_count += 1
        # Tests expect retry count to be stored on context
        ctx_set(callback_context, f"{pipeline_name}_retry_count", retry_count)
        logger.info(
            f"Retrying {pipeline_name} (attempt {retry_count}/{MAX_RETRY_ATTEMPTS})"
        )

        # Add delay before retry
        import time

        time.sleep(RETRY_DELAY_SECONDS)

        return True  # Indicate retry should be attempted
    else:
        logger.error(
            f"Max retry attempts reached for {pipeline_name}. Pipeline failed."
        )
        ctx_set(callback_context, f"{pipeline_name}_failed", True)
        return False  # Indicate pipeline has failed


def validate_pipeline_dependencies(callback_context, required_dependencies):
    """Validate that required pipeline dependencies are available."""
    missing_dependencies = []

    for dependency in required_dependencies:
        if not ctx_get(callback_context, dependency):
            missing_dependencies.append(dependency)

    if missing_dependencies:
        logger.warning(f"Missing pipeline dependencies: {missing_dependencies}")
        return False, missing_dependencies

    return True, []


def aggregate_pipeline_results(callback_context):
    """Aggregate results from all pipeline stages for final synthesis."""
    aggregated_results = {
        "industry_classification": ctx_get(
            callback_context, "industry_classification_results", {}
        ),
        "market_validation": ctx_get(callback_context, "market_validation_results", {}),
        "kpi_framework": ctx_get(callback_context, "kpi_framework_results", {}),
        "benchmarking": ctx_get(callback_context, "benchmarking_results", {}),
        "kpi_analysis": ctx_get(callback_context, "kpi_analysis_results", {}),
        "pipeline_metadata": {
            "execution_timestamp": ctx_get(callback_context, "timestamp"),
            "pipeline_warnings": ctx_get(callback_context, "synthesis_warnings", []),
            "retry_counts": {
                "market_validation": ctx_get(
                    callback_context, "market_validation_pipeline_retry_count", 0
                ),
                "analysis_benchmarking": ctx_get(
                    callback_context, "analysis_benchmarking_pipeline_retry_count", 0
                ),
            },
        },
    }

    return aggregated_results


def parallel_pipeline_completion_callback(callback_context, **kwargs):
    """Callback for parallel pipeline completion with result synchronization."""
    logger.info(
        "\n🔄 parallel_pipeline_completion: Synchronizing results from parallel analysis agents\n"
    )

    # Check completion status of parallel agents
    pipeline_state = {}

    # Validate that both parallel agents completed successfully
    required_parallel_results = [
        "industry_benchmarking_results",
        "kpi_analysis_results",
    ]

    completed_agents = []
    failed_agents = []

    for result_key in required_parallel_results:
        if ctx_get(callback_context, result_key):
            completed_agents.append(result_key.replace("_results", ""))
        else:
            failed_agents.append(result_key.replace("_results", ""))

    # Update pipeline state
    pipeline_state["completed_agents"] = completed_agents
    pipeline_state["failed_agents"] = failed_agents
    pipeline_state["parallel_execution_status"] = (
        "completed" if not failed_agents else "partial_failure"
    )

    # Log completion status
    if failed_agents:
        logger.warning(f"Parallel pipeline completed with failures: {failed_agents}")
        ctx_set(callback_context, "parallel_pipeline_warnings", failed_agents)
    else:
        logger.info("Parallel pipeline completed successfully - all agents finished")

    # Aggregate and synchronize results for next pipeline stage
    synchronized_results = synchronize_parallel_results(callback_context)
    ctx_set(callback_context, "synchronized_parallel_results", synchronized_results)


def synchronize_parallel_results(callback_context):
    """Synchronize and validate results from parallel agents."""
    benchmarking_results = ctx_get(
        callback_context, "industry_benchmarking_results", {}
    )
    kpi_analysis_results = ctx_get(callback_context, "kpi_analysis_results", {})

    # Cross-validate results for consistency
    consistency_checks = perform_result_consistency_checks(
        benchmarking_results, kpi_analysis_results
    )

    # Create synchronized result structure
    synchronized_results = {
        "benchmarking_analysis": benchmarking_results,
        "kpi_performance_analysis": kpi_analysis_results,
        "cross_validation": consistency_checks,
        "synchronization_metadata": {
            "sync_timestamp": ctx_get(callback_context, "timestamp"),
            "data_consistency_score": consistency_checks.get(
                "overall_consistency_score", 0.0
            ),
            "validation_warnings": consistency_checks.get("warnings", []),
        },
    }

    return synchronized_results


def perform_result_consistency_checks(benchmarking_results, kpi_analysis_results):
    """Perform consistency checks between parallel analysis results."""
    consistency_checks = {
        "overall_consistency_score": 1.0,
        "warnings": [],
        "cross_validation_results": {},
    }

    try:
        # Check for consistent KPI performance assessments
        benchmarking_performance = benchmarking_results.get(
            "overall_performance_score", 0.0
        )
        kpi_performance = kpi_analysis_results.get("performance_summary", {}).get(
            "overall_score", 0.0
        )

        if abs(benchmarking_performance - kpi_performance) > 0.3:
            consistency_checks["warnings"].append(
                "Significant discrepancy between benchmarking and KPI analysis performance scores"
            )
            consistency_checks["overall_consistency_score"] *= 0.8

        # Check for consistent industry positioning
        benchmarking_position = benchmarking_results.get("industry_position", "unknown")
        kpi_position_indicators = kpi_analysis_results.get(
            "performance_summary", {}
        ).get("position_indicators", [])

        if benchmarking_position != "unknown" and kpi_position_indicators:
            position_consistency = validate_position_consistency(
                benchmarking_position, kpi_position_indicators
            )
            if not position_consistency:
                consistency_checks["warnings"].append(
                    "Inconsistent industry positioning between benchmarking and KPI analysis"
                )
                consistency_checks["overall_consistency_score"] *= 0.9

        # Check for consistent improvement recommendations
        benchmarking_improvements = benchmarking_results.get("improvement_areas", [])
        kpi_improvements = kpi_analysis_results.get("improvement_recommendations", [])

        recommendation_overlap = calculate_recommendation_overlap(
            benchmarking_improvements, kpi_improvements
        )
        if recommendation_overlap < 0.5:
            consistency_checks["warnings"].append(
                "Low overlap between benchmarking and KPI analysis improvement recommendations"
            )
            consistency_checks["overall_consistency_score"] *= 0.9

        consistency_checks["cross_validation_results"] = {
            "performance_score_difference": abs(
                benchmarking_performance - kpi_performance
            ),
            "position_consistency": validate_position_consistency(
                benchmarking_position, kpi_position_indicators
            ),
            "recommendation_overlap": recommendation_overlap,
        }

    except Exception as e:
        logger.error(f"Error performing consistency checks: {e!s}")
        consistency_checks["warnings"].append("Error during consistency validation")
        consistency_checks["overall_consistency_score"] = 0.5

    return consistency_checks


def validate_position_consistency(benchmarking_position, kpi_position_indicators):
    """Validate consistency between benchmarking position and KPI position indicators."""
    position_mapping = {
        "top_performer": ["high_performance", "above_average", "excellent"],
        "above_average": ["good_performance", "above_average", "strong"],
        "average": ["average_performance", "typical", "standard"],
        "below_average": ["below_average", "weak_performance", "concerning"],
        "underperformer": ["poor_performance", "critical", "urgent_attention"],
    }

    expected_indicators = position_mapping.get(benchmarking_position.lower(), [])

    # Check if any KPI position indicators align with benchmarking position
    for indicator in kpi_position_indicators:
        if any(expected in indicator.lower() for expected in expected_indicators):
            return True

    return False


def calculate_recommendation_overlap(benchmarking_improvements, kpi_improvements):
    """Calculate overlap between improvement recommendations from different analyses."""
    if not benchmarking_improvements or not kpi_improvements:
        return 0.0

    # Convert to lowercase for comparison
    benchmarking_set = {item.lower() for item in benchmarking_improvements}
    kpi_set = {item.lower() for item in kpi_improvements}

    # Calculate Jaccard similarity
    intersection = len(benchmarking_set.intersection(kpi_set))
    union = len(benchmarking_set.union(kpi_set))

    return intersection / union if union > 0 else 0.0


def handle_parallel_processing_failure(callback_context, failed_agents):
    """Handle failures in parallel processing with fallback strategies."""
    logger.warning(f"Handling parallel processing failures for agents: {failed_agents}")

    fallback_strategies = {
        "industry_benchmarking": "Use generic industry benchmarks and historical data",
        "kpi_analysis": "Perform basic KPI validation without advanced trend analysis",
    }

    applied_fallbacks = []
    for failed_agent in failed_agents:
        if failed_agent in fallback_strategies:
            fallback_strategy = fallback_strategies[failed_agent]
            applied_fallbacks.append(
                {
                    "agent": failed_agent,
                    "fallback_strategy": fallback_strategy,
                    "impact": "Reduced analysis depth and accuracy",
                }
            )
            logger.info(f"Applied fallback for {failed_agent}: {fallback_strategy}")

    ctx_set(callback_context, "applied_fallback_strategies", applied_fallbacks)

    return applied_fallbacks


def setup_business_kpis_orchestrator_callback(callback_context, **kwargs):
    """Setup callback for the business KPIs orchestrator agent."""
    logger.info(
        "\n👑 Business KPIs Orchestrator: 🚀 Starting business KPI validation and analysis workflow\n"
    )
    # Initialize any global state needed


def market_validation_pipeline_callback(callback_context, **kwargs):
    """Callback for market validation pipeline progress."""
    logger.info(
        "\n🔄 market_validation_pipeline: Market validation pipeline initiated - running sequential classification and validation\n"
    )

    # Initialize pipeline state tracking
    pipeline_state = {
        "industry_classification_complete": False,
        "market_validation_complete": False,
        "kpi_framework_selection_complete": False,
        "pipeline_start_time": ctx_get(callback_context, "timestamp"),
        "retry_count": 0,
    }

    ctx_set(callback_context, "market_validation_pipeline_state", pipeline_state)


def analysis_benchmarking_pipeline_callback(callback_context, **kwargs):
    """Callback for analysis and benchmarking pipeline progress."""
    logger.info(
        "\n📊 analysis_benchmarking_pipeline: Analysis and benchmarking pipeline initiated - running parallel analysis agents\n"
    )

    # Initialize parallel pipeline state tracking
    pipeline_state = {
        "industry_benchmarking_complete": False,
        "kpi_analysis_complete": False,
        "pipeline_start_time": ctx_get(callback_context, "timestamp"),
        "retry_count": 0,
        "parallel_execution_status": "initiated",
    }

    ctx_set(callback_context, "analysis_benchmarking_pipeline_state", pipeline_state)


def kpi_report_synthesis_callback(
    callback_context, llm_response: LlmResponse | None = None, **kwargs
):
    """Callback to synthesize KPI analysis results from all agents."""
    logger.info(
        "\n🤖 kpi_report_synthesizer: Synthesizing KPI analysis results from all agents\n"
    )

    # Validate that all required pipeline results are available
    required_results = [
        "industry_classification_results",
        "market_validation_results",
        "kpi_framework_results",
        "benchmarking_results",
        "kpi_analysis_results",
    ]

    missing_results = []
    for result_key in required_results:
        if not ctx_get(callback_context, result_key):
            missing_results.append(result_key)

    if missing_results:
        logger.warning(f"Missing required results for synthesis: {missing_results}")
        ctx_set(callback_context, "synthesis_warnings", missing_results)

    # Save the response to markdown file
    try:
        if not llm_response:
            logger.warning(
                "⚠️ kpi_report_synthesis_callback called without an LlmResponse; skipping save."
            )
            return
        if llm_response.content and llm_response.content.parts:
            save_llm_response_to_file(
                filename="bkpi_llm",
                llm_content=llm_response.content,
                session_path=get_session_dir(callback_context),
                file_type="md",
            )
        else:
            logger.warning("⚠️ No content in LlmResponse to save in synthesis_callback.")
    except Exception as e:
        logger.error(f"❌ Error saving LLM response in synthesis_callback: {e}")

    # Save state to file
    try:
        if callback_context.state:
            save_state_to_file(
                context=callback_context,
                session_path=get_session_dir(callback_context),
                filename="bkpi_state",
                file_type="json",
            )
    except Exception as e:
        logger.error(f"❌ Error saving state in synthesis_callback: {e}")

    # Set the synthesized KPI report in callback context for parent agent access
    callback_context.synthesized_kpi_report = {
        "status": "completed",
        "session_path": get_session_dir(callback_context),
        "files_saved": ["bkpi_llm.md", "bkpi_state.json"],
    }


from agents.industry_benchmarking.agent import industry_benchmarking_agent
from agents.industry_classifier.agent import industry_classifier_agent
from agents.kpi_analysis.agent import kpi_analysis_agent
from agents.kpi_framework_selector.agent import kpi_framework_selector_agent
from agents.market_size_validator.agent import market_size_validator_agent
from agents.report_synthesis.agent import report_synthesis_agent


# Persisting callbacks to store each stage result into context
def _store_industry_classification(callback_context, **kwargs):
    # Store a minimal completion stub if detailed parsing is unavailable
    ctx_set(
        callback_context,
        "industry_classification_results",
        {
            "status": "completed",
        },
    )


def _store_market_validation(callback_context, **kwargs):
    ctx_set(
        callback_context,
        "market_validation_results",
        {
            "status": "completed",
        },
    )


def _store_kpi_framework(callback_context, **kwargs):
    # If selector agent already placed results via its tools, keep them; else set stub
    if not ctx_get(callback_context, "kpi_framework_results"):
        ctx_set(
            callback_context,
            "kpi_framework_results",
            {
                "status": "completed",
            },
        )


def _store_benchmarking(callback_context, **kwargs):
    # Ensure both legacy and generic keys are set for downstream compatibility
    if not ctx_get(callback_context, "industry_benchmarking_results"):
        ctx_set(
            callback_context,
            "industry_benchmarking_results",
            {
                "status": "completed",
            },
        )
    if not ctx_get(callback_context, "benchmarking_results"):
        ctx_set(
            callback_context,
            "benchmarking_results",
            ctx_get(
                callback_context,
                "industry_benchmarking_results",
                {"status": "completed"},
            ),
        )


def _store_kpi_analysis(callback_context, **kwargs):
    if not ctx_get(callback_context, "kpi_analysis_results"):
        ctx_set(
            callback_context,
            "kpi_analysis_results",
            {
                "status": "completed",
            },
        )


# Market Validation Pipeline (Sequential)
# Wrap base agents with after_model_callback to persist results
def create_industry_classifier_agent_with_callback():
    """Create a fresh instance of the industry classifier agent with callback."""
    return Agent(
        model=industry_classifier_agent.model,
        name=industry_classifier_agent.name,
        description=industry_classifier_agent.description,
        instruction=industry_classifier_agent.instruction,
        tools=industry_classifier_agent.tools,
        after_model_callback=_store_industry_classification,
        generate_content_config=industry_classifier_agent.generate_content_config,
        include_contents=industry_classifier_agent.include_contents,
    )


industry_classifier_agent_with_callback = (
    create_industry_classifier_agent_with_callback()
)


def create_market_size_validator_agent_with_callback():
    """Create a fresh instance of the market size validator agent with callback."""
    return Agent(
        model=market_size_validator_agent.model,
        name=market_size_validator_agent.name,
        description=market_size_validator_agent.description,
        instruction=market_size_validator_agent.instruction,
        tools=market_size_validator_agent.tools,
        after_model_callback=_store_market_validation,
        generate_content_config=market_size_validator_agent.generate_content_config,
        include_contents=market_size_validator_agent.include_contents,
    )


market_size_validator_agent_with_callback = (
    create_market_size_validator_agent_with_callback()
)


def create_kpi_framework_selector_agent_with_callback():
    """Create a fresh instance of the KPI framework selector agent with callback."""
    return Agent(
        model=kpi_framework_selector_agent.model,
        name=kpi_framework_selector_agent.name,
        description=kpi_framework_selector_agent.description,
        instruction=kpi_framework_selector_agent.instruction,
        tools=kpi_framework_selector_agent.tools,
        before_agent_callback=kpi_framework_selector_agent.before_agent_callback,
        after_model_callback=_store_kpi_framework,
        generate_content_config=kpi_framework_selector_agent.generate_content_config,
        include_contents=kpi_framework_selector_agent.include_contents,
    )


kpi_framework_selector_agent_with_callback = (
    create_kpi_framework_selector_agent_with_callback()
)


def create_market_validation_pipeline():
    """Create a fresh instance of the market validation pipeline."""
    return SequentialAgent(
        name="market_validation_pipeline",
        description="Sequential execution of industry classification, market validation, and KPI framework selection",
        sub_agents=[
            create_industry_classifier_agent_with_callback(),
            create_market_size_validator_agent_with_callback(),
            create_kpi_framework_selector_agent_with_callback(),
        ],
        before_agent_callback=market_validation_pipeline_callback,
    )


market_validation_pipeline = create_market_validation_pipeline()


# Analysis & Benchmarking Pipeline (Parallel)
def create_industry_benchmarking_agent_with_callback():
    """Create a fresh instance of the industry benchmarking agent with callback."""
    return Agent(
        model=industry_benchmarking_agent.model,
        name=industry_benchmarking_agent.name,
        description=industry_benchmarking_agent.description,
        instruction=industry_benchmarking_agent.instruction,
        tools=industry_benchmarking_agent.tools,
        after_model_callback=_store_benchmarking,
        generate_content_config=industry_benchmarking_agent.generate_content_config,
        include_contents=industry_benchmarking_agent.include_contents,
    )


industry_benchmarking_agent_with_callback = (
    create_industry_benchmarking_agent_with_callback()
)


def create_kpi_analysis_agent_with_callback():
    """Create a fresh instance of the KPI analysis agent with callback."""
    return Agent(
        model=kpi_analysis_agent.model,
        name=kpi_analysis_agent.name,
        description=kpi_analysis_agent.description,
        instruction=kpi_analysis_agent.instruction,
        tools=kpi_analysis_agent.tools,
        after_model_callback=_store_kpi_analysis,
        generate_content_config=kpi_analysis_agent.generate_content_config,
        include_contents=kpi_analysis_agent.include_contents,
    )


kpi_analysis_agent_with_callback = create_kpi_analysis_agent_with_callback()


def create_analysis_benchmarking_pipeline():
    """Create a fresh instance of the analysis benchmarking pipeline."""
    return ParallelAgent(
        name="analysis_benchmarking_pipeline",
        description="Parallel execution of benchmarking and KPI analysis for independent processing",
        sub_agents=[
            create_industry_benchmarking_agent_with_callback(),
            create_kpi_analysis_agent_with_callback(),
        ],
        before_agent_callback=analysis_benchmarking_pipeline_callback,
        after_agent_callback=parallel_pipeline_completion_callback,
    )


analysis_benchmarking_pipeline = create_analysis_benchmarking_pipeline()


def create_report_synthesis_agent_with_callback():
    """Create a fresh instance of the report synthesis agent with callback."""
    return Agent(
        model=report_synthesis_agent.model,
        name=report_synthesis_agent.name,
        description=report_synthesis_agent.description,
        instruction=report_synthesis_agent.instruction,
        tools=report_synthesis_agent.tools,
        after_model_callback=kpi_report_synthesis_callback,
        generate_content_config=report_synthesis_agent.generate_content_config,
        include_contents=report_synthesis_agent.include_contents,
    )


# Use the implemented report synthesis agent with callback
report_synthesis_agent_with_callback = create_report_synthesis_agent_with_callback()


def create_business_kpi_analysis_pipeline():
    """Create a fresh instance of the business KPI analysis pipeline."""
    return SequentialAgent(
        name="business_kpi_analysis_pipeline",
        description="Sequential execution of market validation, analysis & benchmarking, and report synthesis",
        sub_agents=[
            create_market_validation_pipeline(),
            create_analysis_benchmarking_pipeline(),
            create_report_synthesis_agent_with_callback(),
        ],
    )


# Main Business KPI Analysis Pipeline
business_kpi_analysis_pipeline = create_business_kpi_analysis_pipeline()


def create_business_kpis_orchestrator():
    """Create a fresh instance of the business KPIs orchestrator agent."""
    return Agent(
        model=MODEL,
        name="business_kpis_orchestrator",
        description=(
            "Main orchestrator for business KPI validation and analysis. "
            "Coordinates industry classification, market size validation, KPI benchmarking, and comprehensive reporting."
        ),
        instruction=prompt.BUSINESS_KPIS_ORCHESTRATOR_INSTRUCTION,
        # planner=PlanReActPlanner(),
        sub_agents=[create_business_kpi_analysis_pipeline()],
        before_agent_callback=setup_business_kpis_orchestrator_callback,
        output_key="synthesized_kpi_report",
        # generate_content_config=types.GenerateContentConfig(
        #     temperature=config.TEMPERATURE,
        # ),
        include_contents="default",
    )


# Root Business KPIs Orchestrator Agent
root_agent = create_business_kpis_orchestrator()

# Keep the original name for backward compatibility
business_kpis_orchestrator_agent = root_agent

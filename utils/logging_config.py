"""
Logging configuration for the startup analyst multi-agent system.
"""

import logging
import sys
from pathlib import Path

# from utils.file_utils import write_to_file


def setup_logging(
    level: str = "INFO", log_file: str | None = None, include_timestamp: bool = True
) -> None:
    """
    Set up logging configuration for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        include_timestamp: Whether to include timestamps in log messages
    """
    # Convert string level to logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create formatter
    if include_timestamp:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add file handler if log file specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Set specific logger levels
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_callback_event(
    event_type: str,
    agent_name: str,
    agent_type: str = "agent",
    workflow_id: str | None = None,
):
    """
    Create a callback function that logs agent events with structured information.

    Args:
        event_type: Type of event ('starting', 'completed', 'failed')
        agent_name: Name of the agent
        agent_type: Type of agent ('agent', 'workflow', 'tool')
        workflow_id: Optional workflow ID for context injection

    """
    logger = get_logger(f"agents.{agent_name}")
    emoji_map = {
        ("starting", "agent"): "🤖",
        ("starting", "workflow"): "👑",
        ("starting", "tool"): "🔧",
        ("completed", "agent"): "✅",
        ("completed", "workflow"): "🏁",
        ("completed", "tool"): "✅",
        ("failed", "agent"): "❌",
        ("failed", "workflow"): "💥",
        ("failed", "tool"): "🚨",
    }

    emoji = emoji_map.get((event_type, agent_type), "📋")

    context_info = f" (workflow: {workflow_id})" if workflow_id else ""

    if event_type == "starting":
        logger.info(
            f"\n{emoji} {agent_name}: {event_type.title()} {agent_type} execution{context_info}\n"
        )
    elif event_type == "completed":
        logger.info(
            f"\n{emoji} {agent_name}: {event_type.title()} {agent_type} execution successfully{context_info}\n"
        )
    elif event_type == "failed":
        logger.info(
            f"\n{emoji} {agent_name}: {event_type.title()} {agent_type} execution with errors{context_info}\n"
        )
    else:
        logger.info(
            f"\n{emoji} {agent_name}: {event_type} - {agent_type}{context_info}\n"
        )


# def log_error(component: str, error: Exception, context: str | None = None):
#     """
#     Log error details with context.

#     Args:
#         component: Component where error occurred
#         error: Exception instance
#         context: Optional context information
#     """
#     logger = get_logger(component)

#     message = f"Error in {component}: {str(error)}"
#     if context:
#         message += f" (Context: {context})"

#     logger.error(message, exc_info=True)


# def configure_competitor_logging() -> None:
#     """
#     Configure logging specifically for competitor analysis workflow.
#     Sets up specialized loggers for competitor analysis agents.
#     """
#     # Configure competitor analysis specific loggers
#     competitor_agents = [
#         "competitor_extractor",
#         "market_researcher",
#         "competitor_intelligence",
#         "competitive_analysis",
#         "report_synthesis",
#         "competitor_profile_orchestrator"
#     ]

#     for agent_name in competitor_agents:
#         logger = logging.getLogger(f"agents.{agent_name}")
#         # Competitor agents may need more detailed logging for research activities
#         logger.setLevel(logging.INFO)

#     # Configure workflow orchestrator logger
#     orchestrator_logger = logging.getLogger("workflow.competitor_profile_orchestrator")
#     orchestrator_logger.setLevel(logging.INFO)

#     # Configure search and research activity loggers
#     search_logger = logging.getLogger("competitor.search")
#     search_logger.setLevel(logging.INFO)

#     research_logger = logging.getLogger("competitor.research")
#     research_logger.setLevel(logging.INFO)


# def log_competitor_discovery(agent_name: str, discovered_count: int, search_terms: list[str]):
#     """
#     Log competitor discovery results.

#     Args:
#         agent_name: Name of the agent performing discovery
#         discovered_count: Number of competitors discovered
#         search_terms: Search terms used for discovery
#     """
#     logger = get_logger(f"agents.{agent_name}")

#     message = f"Discovered {discovered_count} competitors using terms: {', '.join(search_terms)}"
#     logger.info(message)


# def log_competitor_analysis(agent_name: str, competitor_name: str, analysis_type: str, result: str):
#     """
#     Log competitor analysis activities.

#     Args:
#         agent_name: Name of the agent performing analysis
#         competitor_name: Name of competitor being analyzed
#         analysis_type: Type of analysis (intelligence, validation, etc.)
#         result: Analysis result summary
#     """
#     logger = get_logger(f"agents.{agent_name}")

#     message = f"{analysis_type} for '{competitor_name}': {result}"
#     logger.info(message)


# def log_search_activity(search_type: str, query: str, results_count: int, duration: float):
#     """
#     Log search activity for competitor research.

#     Args:
#         search_type: Type of search (google, news, etc.)
#         query: Search query used
#         results_count: Number of results returned
#         duration: Search duration in seconds
#     """
#     logger = get_logger("competitor.search")

#     message = f"{search_type} search: '{query}' -> {results_count} results ({duration:.2f}s)"
#     logger.info(message)


# def log_validation_result(agent_name: str, claim: str, validation_status: str, confidence: float):
#     """
#     Log competitive advantage validation results.

#     Args:
#         agent_name: Name of the agent performing validation
#         claim: Competitive advantage claim being validated
#         validation_status: Validation result (supported, contradicted, unclear)
#         confidence: Confidence score (0.0 to 1.0)
#     """
#     logger = get_logger(f"agents.{agent_name}")

#     message = f"Validation: '{claim}' -> {validation_status} (confidence: {confidence:.2f})"
#     logger.info(message)


# def log_orchestrator_progress(stage: str, details: str, progress_percent: int = None):
#     """
#     Log orchestrator workflow progress.

#     Args:
#         stage: Current workflow stage
#         details: Stage details
#         progress_percent: Optional progress percentage
#     """
#     logger = get_logger("workflow.competitor_profile_orchestrator")

#     message = f"Stage: {stage} - {details}"
#     if progress_percent is not None:
#         message += f" ({progress_percent}% complete)"

#     logger.info(message)

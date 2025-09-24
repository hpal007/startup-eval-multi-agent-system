"""
PDF Processing Agent

Specialized agent for processing PDF documents and extracting structured content.
Uses PyMuPDF for page-by-page text extraction and outputs structured JSON format.
"""

import json
import logging

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

from tools.file_tool import upload_tool
from tools.pdf_tool import process_pdf_with_llm
from utils import save_to_state
from utils.configs import config
from utils.helper import (
    check_uploaded_pdf,
    get_session_dir,
    save_llm_response_to_file,
    save_state_to_file,
)
from utils.logging_config import log_callback_event

from . import prompt

logger = logging.getLogger(__name__)
MODEL = config.get_model_for_agent("abc_agent")


async def data_consolidation_setup_callback(callback_context, **_kwargs):
    """Setup callback for data consolidation agent."""
    logger.info("🚀 PDF Processor Agent SETUP - Starting execution")

    report_bytes = check_uploaded_pdf(callback_context)

    if report_bytes:
        # Create a session-unique filename to avoid collisions
        try:
            session_id = None
            if hasattr(callback_context, "_invocation_context") and getattr(
                callback_context._invocation_context, "session", None
            ):
                session_id = callback_context._invocation_context.session.id
            fname = f"report_{session_id or 'anon'}.pdf"
        except Exception:
            fname = "report_uploaded.pdf"

        await upload_tool.run(callback_context, file_bytes=report_bytes, filename=fname)
        # Optionally store filename in state for later tools to discover
        try:
            if hasattr(callback_context, "state"):
                callback_context.state["uploaded_report_filename"] = fname
        except Exception:
            pass

    log_callback_event(event_type="starting", agent_name="pdf_processor_agent")


def data_consolidation_after_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
):
    log_callback_event(event_type="completed", agent_name="data_consolidation_agent")
    # Save LlmResponse content and state to files
    if llm_response.content and llm_response.content.parts:
        save_llm_response_to_file(
            filename="pdf_llm",
            llm_content=llm_response.content,
            session_path=get_session_dir(callback_context),
            file_type="json",
        )

    if callback_context.state:
        save_state_to_file(
            context=callback_context,
            session_path=get_session_dir(callback_context),
            filename="pdf_state",
            file_type="json",
        )

    elif llm_response.error_message:
        print(
            f"[Callback] Inspected response: Contains error '{llm_response.error_message}'. No modification."
        )
        return None
    else:
        print("[Callback] Inspected response: Empty LlmResponse.")
        return None  # Nothing to modify


async def process_pdf_tool(tool_context: ToolContext) -> str:
    """
    Processes PDF documents page-by-page and extracts text content.

    This tool loads PDF artifacts and extracts text from each page using OCR/vision models.
    Returns structured JSON with page numbers as keys and extracted text as values.

    Returns:
        JSON string with format: {"1": "page 1 text", "2": "page 2 text", ...}
    """

    try:
        # Load the latest available artifact; prefer session stored filename if available
        report_artifact = None
        try:
            # Try to find uploaded filename in session/tool state
            candidate_name = None
            try:
                candidate_name = getattr(tool_context, "state", {}).get(
                    "uploaded_report_filename"
                )
            except Exception:
                candidate_name = None

            if candidate_name:
                report_artifact = await tool_context.load_artifact(
                    filename=candidate_name
                )

            if not report_artifact:
                # Fallback to listing artifacts and picking the most recent
                available = await tool_context.list_artifacts()
                if available:
                    # Use the last item in the list (assumed latest)
                    last_name = available[-1]
                    report_artifact = await tool_context.load_artifact(
                        filename=last_name
                    )

        except Exception as e:
            logger.warning(f"Could not load artifact by name: {e}")

        if report_artifact and getattr(report_artifact, "inline_data", None):
            print("Successfully loaded latest Python artifact for PDF processing.")
            print(f"MIME Type: {report_artifact.inline_data.mime_type}")
            print(f"Report size: {len(report_artifact.inline_data.data)} bytes.")
            # Process the report_artifact.inline_data.data (bytes)
            pdf_data = report_artifact.inline_data.data
            result = process_pdf_with_llm(pdf_data)
            logger.info("✅ PDF processing completed with data")
            if save_to_state("pdf_content", result, tool_context):
                logger.info("✅ PDF content saved to session state")
            return result

        else:
            return json.dumps({"error": "No PDF found in context to process"})

    except ValueError as e:
        logger.error(
            f"Error loading Python artifact: {e}. Is ArtifactService configured?"
        )
        return json.dumps({"error": f"Artifact loading failed: {e!s}"})
    except Exception as e:
        # Handle potential storage errors
        logger.error(f"An unexpected error occurred during Python artifact load: {e}")
        return json.dumps({"error": f"Unexpected error: {e!s}"})


def create_pdf_processor_agent():
    """Create a fresh instance of the PDF processor agent."""
    return Agent(
        model=MODEL,
        name="pdf_processor_agent",
        description=(
            "PDF Processing Agent that MUST call process_pdf_tool to extract and format text from PDF documents. "
            "ALWAYS starts by calling the process_pdf_tool function to load PDF artifacts and extract page-by-page content. "
            "Then processes the extracted text to remove special characters and format it into clean, structured JSON output. "
            "The agent cannot function without calling the tool first - it has no other way to access PDF content."
        ),
        instruction=prompt.PDF_PROCESSOR_INSTRUCTION,
        tools=[FunctionTool(process_pdf_tool)],
        before_agent_callback=data_consolidation_setup_callback,
        after_model_callback=data_consolidation_after_callback,
        include_contents="default",
        output_key="pdf_processor_agent_output",
    )


# Create a default instance for backward compatibility
pdf_processor_agent = create_pdf_processor_agent()
root_agent = pdf_processor_agent

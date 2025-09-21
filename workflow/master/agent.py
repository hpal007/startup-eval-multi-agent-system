# from google.adk.agents.llm_agent import Agent
from google.adk.agents import Agent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import FunctionTool

from agents.process_pdf.agent import create_pdf_processor_agent
from tools.file_tool import upload_tool
from utils.configs import config
from utils.helper import check_uploaded_pdf, create_session_dir, list_user_files_py
from utils.logging_config import get_logger
from workflow.competitor_profile_orchestrator.agent import (
    create_competitor_profile_orchestrator,
)
from workflow.founder_profile_orchestrator.agent import (
    create_founder_profile_orchestrator,
)

from . import prompt

logger = get_logger(__name__)
file_path = "/Users/harish/Desktop/se-system/files/test_startup_pitch.pdf"

# Use configuration system to get the model
MODEL = config.get_model_for_agent("abc_agent")


async def before_agent_callback(callback_context: CallbackContext):
    # Example callback logic
    logger.info("Before agent callback executed")

    report_bytes = check_uploaded_pdf(callback_context)

    # File upload logic
    if file_path:
        await upload_tool.run(
            callback_context, file_path=file_path, filename="file_path.pdf"
        )
    if report_bytes:
        await upload_tool.run(
            callback_context, file_bytes=report_bytes, filename="file_path.pdf"
        )

    # Create Session directory
    if hasattr(callback_context, "_invocation_context"):
        create_session_dir(
            callback_context._invocation_context.session.id,
            callback_context._invocation_context.session.user_id,
            callback_context._invocation_context.session.app_name,
        )


# after_agent_callback
def after_agent_callback(callback_context: CallbackContext):
    logger.info(f"After agent callback executed {callback_context.invocation_id}")


# Main founder evaluation pipeline
startup_evaluation_pipeline = SequentialAgent(
    name="startup_evaluation_pipeline",
    description="Processes startup pitch documents and generates comprehensive founder team evaluations",
    sub_agents=[
        create_pdf_processor_agent(),  # Extract and process pitch deck content
        create_founder_profile_orchestrator(),  # Analyze founders and generate team report
        create_competitor_profile_orchestrator(),  # Analyze competitors and market positioning
    ],
)


root_agent = Agent(
    model=MODEL,
    name="master_agent",
    description="Comprehensive startup evaluation system that processes pitch documents and generates in-depth analysis including PDF content extraction, founder team verification, competitive landscape assessment, and market positioning reports.",
    instruction=prompt.MASTER_AGENT_PROMPT,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    tools=[FunctionTool(list_user_files_py)],
    sub_agents=[startup_evaluation_pipeline],
    include_contents="default",
)

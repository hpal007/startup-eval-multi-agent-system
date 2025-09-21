from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool

from agents.process_pdf.agent import pdf_processor_agent
from tools.file_tool import upload_tool
from utils.configs import config
from utils.helper import check_uploaded_pdf, create_session_dir, list_user_files_py
from utils.logging_config import get_logger

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
    logger.info("After agent callback executed")

root_agent = Agent(
    model=MODEL,
    name="master_agent",
    description="A helpful assistant for file processing and user questions.",
    instruction="Answer user questions to the best of your knowledge you have access to the user files using using tool `list_user_files_py`. Use them if relevant.",
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    tools=[FunctionTool(list_user_files_py), AgentTool(pdf_processor_agent)],
    include_contents="default",
)

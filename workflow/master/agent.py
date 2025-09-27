from google.adk.agents import SequentialAgent
from google.adk.agents.callback_context import CallbackContext

from agents.process_pdf.agent import create_pdf_processor_agent
from tools.file_tool import upload_tool
from utils.configs import config
from utils.helper import (
    check_uploaded_pdf,
    create_session_dir,
)
from utils.logging_config import get_logger
from workflow.founder_profile_orchestrator.agent import (
    create_founder_profile_orchestrator,
)
from workflow.competitor_profile_orchestrator.agent import (
    create_competitor_profile_orchestrator,
)

logger = get_logger(__name__)

file_path = None
# Use configuration system to get the model
MODEL = config.get_model_for_agent("OLLAMA")

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


root_agent = SequentialAgent(
    name="master_agent",
    description="Comprehensive startup evaluation system that processes pitch documents and generates in-depth analysis including PDF content extraction, founder team verification, competitive landscape assessment, and market positioning reports.",
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    sub_agents=[
        create_pdf_processor_agent(),
        create_founder_profile_orchestrator(),
        create_competitor_profile_orchestrator()
        # create_business_kpis_orchestrator(),  # Then validate business KPIs
        # create_competitor_profile_orchestrator(),  # Finally analyze competitors
    ],
)

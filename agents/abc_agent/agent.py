from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool

from tools.file_tool import upload_tool
from utils.configs import config
from utils.helper import check_uploaded_pdf, list_user_files_py
from utils.logging_config import get_logger

logger = get_logger(__name__)
file_path = "/Users/harish/Desktop/se-system/files/test_startup_pitch.pdf"

# Use configuration system to get the model
MODEL = config.get_model_for_agent('abc_agent')

async def before_agent_callback(callback_context: CallbackContext):
    # Example callback logic
    logger.info("Before agent callback executed")

    report_bytes = check_uploaded_pdf(callback_context)

    if file_path:
        await upload_tool.run(callback_context, file_path=file_path, filename="file_path.pdf")

    if not report_bytes:
        logger.warning("⚠️ No PDF found in user_content parts during before_agent_callback.")
        return


# after_agent_callback
def after_agent_callback(callback_context: CallbackContext):
    print("After agent callback executed")


root_agent = Agent(
    model=MODEL,
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge you have access to the user files using using tool `list_user_files_py`. Use them if relevant.',
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    tools=[FunctionTool(list_user_files_py)],
    include_contents="default",
)

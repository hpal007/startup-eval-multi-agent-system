from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext
import google.genai.types as types

from utils.logging_config import get_logger
logger = get_logger(__name__)

# Check for uploaded PDF in user_content parts
def check_uploaded_pdf(callback_context: CallbackContext):
    report_bytes = None
    if hasattr(callback_context, "user_content"):
        logger.info(f"User content available with {len(callback_context.user_content.parts) if callback_context.user_content and hasattr(callback_context.user_content, 'parts') else 0} parts.")
        if callback_context.user_content and hasattr(callback_context.user_content, "parts"):
            for i, part in enumerate(callback_context.user_content.parts):
                if (
                    hasattr(part, "inline_data")
                    and part.inline_data
                    and hasattr(part.inline_data, "mime_type")
                    and part.inline_data.mime_type == "application/pdf"
                ):
                    logger.info(f"✅ Found uploaded PDF in user_content part {i}")
                    report_bytes = part.inline_data.data

        # Check contents attribute as backup
    if hasattr(callback_context, "contents") and callback_context.contents:
            logger.info(f"Contents available with {len(callback_context.contents) if callback_context.contents else 0} items.")
            for content in callback_context.contents:
                if (
                    hasattr(content, "mime_type")
                    and content.mime_type == "application/pdf"
                    and hasattr(content, "data")
                ):
                    logger.info("✅ Found uploaded PDF in contents")
                    report_bytes = content.data
    return report_bytes

# Check for uploaded PDF in artifacts in tools
async def list_user_files_py(tool_context: ToolContext) -> str:
    try:
        available_files = await tool_context.list_artifacts()
        if not available_files:
            return "You have no saved artifacts."
        else:
            # Format the list for the user/LLM
            file_list_str = "\n".join([f"- {fname}" for fname in available_files])
            return f"Here are your available Python artifacts:\n{file_list_str}"
    except ValueError as e:
        print(f"Error listing Python artifacts: {e}. Is ArtifactService configured?")
        return "Error: Could not list Python artifacts."
    except Exception as e:
        print(f"An unexpected error occurred during Python artifact list: {e}")
        return "Error: An unexpected error occurred while listing Python artifacts."

# Convert a file to bytes and return as a types.Part artifact object
def files_to_bytes(file_path, file_type="application/pdf"):
    """
    Convert a file to bytes and return as a types.Part object.
    
    Args:
        file_path (str): Path to the file to convert
        file_type (str): MIME type of the file (default: "application/pdf")
        
    Returns:
        types.Part: Part object containing the file data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If unable to read the file
        Exception: For other file operation errors
    """
    try:
        with open(file_path, "rb") as f:
            data_bytes = f.read()
        
        logger.info(f"Successfully read {len(data_bytes)} bytes from {file_path}")
        data_artifact = types.Part.from_bytes(data=data_bytes, mime_type=file_type)
        
        return data_artifact
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except PermissionError:
        logger.error(f"Permission denied reading file: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise


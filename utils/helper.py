import os
from pathlib import Path

import google.genai.types as types
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext

from utils.logging_config import get_logger

logger = get_logger(__name__)


# Check for uploaded PDF in user_content parts
def check_uploaded_pdf(callback_context: CallbackContext):
    report_bytes = None
    if hasattr(callback_context, "user_content"):
        logger.info(
            f"User content available with {len(callback_context.user_content.parts) if callback_context.user_content and hasattr(callback_context.user_content, 'parts') else 0} parts."
        )
        if callback_context.user_content and hasattr(
            callback_context.user_content, "parts"
        ):
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
        logger.info(
            f"Contents available with {len(callback_context.contents) if callback_context.contents else 0} items."
        )
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


def create_session_dir(session_id, user_id, app_name, base_dir="sessions"):
    project_root = Path(__file__).parent.parent
    session_dir = os.path.join(
        project_root, base_dir, f"{user_id}_{session_id}_{app_name}"
    )

    # Check if path already exists and return if it does
    if os.path.exists(session_dir):
        logger.info(f"Session directory already exists: {session_dir}")
        return session_dir

    # Create directory if it doesn't exist
    try:
        os.makedirs(session_dir, exist_ok=True)
        logger.info(f"Session directory created: {session_dir}")
    except Exception as e:
        logger.error(f"Error creating session directory {session_dir}: {e}")
        raise
    return session_dir


def get_session_dir(callback_context):
    if hasattr(callback_context, "_invocation_context"):
        return create_session_dir(
            callback_context._invocation_context.session.id,
            callback_context._invocation_context.session.user_id,
            callback_context._invocation_context.session.app_name,
        )
    return None


def remove_ticks(content_text: str) -> str:
    """Remove markdown code fences from start and end of content."""
    content_text = content_text.strip()
    if not content_text:
        return content_text

    # Split into lines for easier processing
    lines = content_text.splitlines()

    # Remove opening code fence (``` or ```json, ```markdown, etc.)
    if lines and lines[0].startswith("```"):
        lines = lines[1:]

    # Remove closing code fence
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    return "\n".join(lines).strip()


def save_to_file(filename: str, data: str, session_path: str, file_type: str = "json"):
    """
    Save data to a file in the specified session directory.

    Args:
        filename (str): The filename for the file
        data (str): The content to save
        session_path (str): Directory path where the file will be saved
        file_type (str): File extension (default: "json")

    Raises:
        OSError: If there's an issue creating directories or writing the file
        ValueError: If inputs are invalid
    """
    if not filename or not isinstance(filename, str):
        raise ValueError("Filename must be a non-empty string")

    if not session_path:
        raise ValueError("Session path must be provided")

    # Sanitize filename to be filesystem-safe
    safe_filename = "".join(
        c for c in filename if c.isalnum() or c in ("-", "_")
    ).strip()
    if not safe_filename:
        safe_filename = "data"

    # Ensure session directory exists
    session_dir = Path(session_path)
    session_dir.mkdir(parents=True, exist_ok=True)

    # Create file path
    report_file = session_dir / f"{safe_filename}.{file_type}"

    try:
        with open(report_file, "w", encoding="utf-8") as fp:
            fp.write(str(data) if data is not None else "")

        logger.info(f"✅ Data saved successfully to: {report_file}")
        return str(report_file)

    except OSError as e:
        logger.error(f"❌ Failed to save data to {report_file}: {e}")
        raise


def save_state_to_file(
    context: CallbackContext, session_path: str, filename="state", file_type="json"
):
    """Save all state data to file using save_to_file."""
    try:
        # Get all state data
        logger.info(f"Saving state data to files in session path: {context.state}")
        state_data = dict(context.state.to_dict())
        logger.info(f"Dict data to files in session path: {state_data}")

        for key, value in state_data.items():
            logger.info(f"State key: {key}, Value type: {type(value)}")
            save_to_file(
                filename=f"{filename}_{key}",
                data=value,
                session_path=session_path,
                file_type=file_type,
            )

        logger.info("✅ State data saved successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to save state data: {e}")
        return False


# save llm_response to file
def save_llm_response_to_file(llm_content, session_path: str, file_type="json"):
    """Save LlmResponse from a tool execution to a JSON file."""
    if not llm_content.parts[0].text:
        logger.warning("No LlmResponse content to save.")
        return

    save_to_file(
        "llm_response", llm_content.parts[0].text, session_path, file_type=file_type
    )

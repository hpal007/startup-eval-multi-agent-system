import mimetypes

from google.genai import types

# from google.adk.tools import FunctionTool, BaseTool
from utils.helper import files_to_bytes
from utils.logging_config import get_logger

logger = get_logger(__name__)


class UploadArtifactTool:
    """
    Uploads any file as an artifact so agents/tools can access it later.

    Args:
        file_path (str): The absolute or relative file path on disk.
        filename (str): The name under which to save the artifact (if None, uses actual file's name).
    Returns:
        dict: {'status': 'success', 'filename': ..., 'mime_type': ...} or error details.
    """

    async def run(
        self,
        callback_context,
        file_path: str = None,
        file_bytes: bytes = None,
        filename: str = "tool_uploaded.pdf",
    ) -> dict:
        try:
            if not file_path and not file_bytes:
                return {
                    "status": "error",
                    "message": "Either file_path or file_bytes must be provided.",
                }

            if file_path:
                logger.info(f"Uploading file from path: {file_path}")
                # Use provided filename, else derive from file_path.
                fname = filename or file_path.split("/")[-1]
                mime_type = (
                    mimetypes.guess_type(file_path)[0] or "application/octet-stream"
                )
                artifact = files_to_bytes(file_path=file_path, file_type=mime_type)

            if file_bytes:
                logger.info(f"Uploading file from bytes, saving as: {filename}")
                fname = filename
                artifact = types.Part.from_bytes(
                    data=file_bytes, mime_type="application/pdf"
                )

            await callback_context.save_artifact(fname, artifact)
            logger.info(f"Successfully saved artifact '{fname}'")
            return {"status": "success", "filename": fname, "mime_type": mime_type}

        except ValueError as e:
            logger.error(
                f"Error saving Python artifact: {e}. Is ArtifactService configured in Runner?"
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}


upload_tool = UploadArtifactTool()

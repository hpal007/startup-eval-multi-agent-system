import base64
import io
import json
from pathlib import Path

import fitz  # PyMuPDF
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.genai import Client
from PIL import Image

from utils.configs import config
from utils.helper import create_session_dir
from utils.logging_config import get_logger

logger = get_logger(__name__)

def get_session_dir(callback_context):
    if hasattr(callback_context, "_invocation_context"):
        return create_session_dir(
            callback_context._invocation_context.session.id,
            callback_context._invocation_context.session.user_id,
            callback_context._invocation_context.session.app_name,
        )
    return None

def process_pdf_page_by_page(pdf_input: str | bytes) -> dict[str, str]:
    """
    Tool-B: Process PDF page-by-page with LLM vision model.

    Args:
        pdf_input: Either a file path string or PDF content as bytes

    Returns:
        Dictionary with page numbers as string keys and extracted text as values
    """
    try:
        logger.info("🔧 Tool-B: Processing PDF page-by-page with LLM")
        client = Client()
        MODEL = config.get_model_for_agent("abc_agent")


        # Open PDF document
        if isinstance(pdf_input, str):
            # File path
            if not Path(pdf_input).exists():
                logger.error(f"PDF file not found: {pdf_input}")
                return {}
            doc = fitz.open(pdf_input)
            logger.info(f"📄 Processing PDF from file: {pdf_input}")
        elif isinstance(pdf_input, bytes):
            # PDF content from context
            doc = fitz.open(stream=pdf_input, filetype="pdf")
            logger.info(f"📄 Processing PDF from context ({len(pdf_input)} bytes)")
        else:
            logger.error(f"Invalid PDF input type: {type(pdf_input)}")
            return {}

        page_texts = {}

        # Process each page
        for page_num in range(len(doc)):
            try:
                logger.info(f"📄 Processing page {page_num + 1}")

                # Load page and convert to image
                page = doc.load_page(page_num)
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)

                # Convert to PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))

                # Convert to base64 for LLM
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                img_bytes = buffer.getvalue()
                image_b64 = base64.b64encode(img_bytes).decode("utf-8")

                # Create prompt for text extraction
                prompt = f"""
                Extract all text content from this PDF page image (page {page_num + 1}).
                
                Instructions:
                - Extract ALL visible text accurately
                - Maintain structure and formatting where possible
                - Include headers, body text, captions, and any other readable content
                - If text is unclear, note it as [UNCLEAR TEXT]
                - Return only the extracted text content, no additional commentary
                """

                # Use LLM to extract text
                response = client.models.generate_content(
                    model=MODEL,
                    contents=[
                        {
                            "parts": [
                                {"text": prompt},
                                {
                                    "inline_data": {
                                        "mime_type": "image/png",
                                        "data": image_b64,
                                    }
                                },
                            ]
                        }
                    ],
                )

                if response and response.text:
                    page_texts[str(page_num + 1)] = response.text.strip()
                    logger.info(f"✅ Extracted text from page {page_num + 1}")
                else:
                    page_texts[str(page_num + 1)] = "[Error: No text extracted]"
                    logger.warning(f"⚠️ Failed to extract text from page {page_num + 1}")

            except Exception as page_error:
                logger.error(f"❌ Error processing page {page_num + 1}: {page_error}")
                page_texts[str(page_num + 1)] = (
                    f"[Error processing page: {page_error!s}]"
                )

        doc.close()
        logger.info(f"✅ Completed processing {len(page_texts)} pages")
        return page_texts

    except Exception as e:
        logger.error(f"❌ Tool-B error: {e}")
        return {}

def process_pdf_with_llm(pdf_input: str | bytes) -> str:
    """
    Tool wrapper: Process PDF and return JSON string.
    Handles both file paths and uploaded PDF data.
    """
    try:
        page_texts = process_pdf_page_by_page(pdf_input)
        data = json.dumps(page_texts, indent=2, ensure_ascii=False)
        # Note: save_response_from_tool will be called from the agent with session_path
        return data
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        return json.dumps({"error": f"PDF processing failed: {e!s}"})

def save_to_state(key: str, value, tool_context: ToolContext):
    tool_context.state[key] = value
    return True

def save_to_file(part: str | int, data: str, session_path: str):
    """Save results from a tool execution to a JSON file."""
    report_file = Path(session_path) / f"processed_pdf_part_{part}.json"

    try:
        with open(report_file, "w") as fp:
            fp.write(data)
        logger.info(f"✅ Tool result saved to: {report_file}")
    except Exception as e:
        logger.error(f"❌ Failed to save tool result: {e}")
        raise


def save_state_to_file(context: CallbackContext, session_path: str):
    """Save all state data to file using save_to_file."""
    try:
        # Get all state data
        logger.info(f"Saving state data to files in session path: {context.state}")
        state_data = dict(context.state.to_dict())
        logger.info(f"Dict data to files in session path: {state_data}")

        for key, value in state_data.items():
            logger.info(f"State key: {key}, Value type: {type(value)}")
            save_to_file(key, value, session_path)

        logger.info("✅ State data saved successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to save state data: {e}")
        return False

# save llm_response to file
def save_llm_response_to_file(llm_content, session_path: str):
    """Save LlmResponse from a tool execution to a JSON file."""
    if not llm_content.parts[0].text:
        logger.warning("No LlmResponse content to save.")
        return

    save_to_file("llm_response", llm_content.parts[0].text, session_path)

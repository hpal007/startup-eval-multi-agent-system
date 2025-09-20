"""
PDF Processing Agent

Specialized agent for processing PDF documents and extracting structured content.
Uses PyMuPDF for page-by-page text extraction and outputs structured JSON format.
"""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

from utils.configs import config

MODEL = config.get_model_for_agent('process_pdf')


process_pdf = Agent(
    model=MODEL,
    name="process_pdf",
    description=(
        "Processes PDF documents page-by-page using vision models "
        "and extracts structured JSON content"
    ),
    instruction=prompt.PDF_PROCESSOR_INSTRUCTION,
    tools=[
        FunctionTool(func=check_uploaded_pdf),
        FunctionTool(func=process_pdf_from_context),
        FunctionTool(func=process_pdf_from_path),
        AgentTool(agent=data_consolidation_agent),
    ],
    before_agent_callback=pdf_setup_callback,
    after_model_callback=log_callback_event(
        event_type="completed", agent_name="process_pdf"
    ),
    generate_content_config=types.GenerateContentConfig(
        temperature=config["temperature"],
    ),
    include_contents="default",
    output_key="process_pdf_output",
)

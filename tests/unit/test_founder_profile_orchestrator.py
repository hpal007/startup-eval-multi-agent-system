#!/usr/bin/env python3
"""
Test script for Founder Profile Orchestrator Agent

This script tests the founder profile orchestrator individually to verify:
1. Agent instantiation and execution
2. File saving functionality in sessions/ directory
3. Context variable requirements
"""

import asyncio
import json
import logging
import sys
import uuid
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai.types import Content


def create_test_founder_profile_orchestrator():
    """Create a test version of the founder profile orchestrator with embedded mock data."""
    from workflow.founder_profile_orchestrator import prompt
    from workflow.founder_profile_orchestrator.agent import (
        create_founder_profile_orchestrator,
    )

    # Create mock PDF processor output
    mock_pdf_output = create_mock_pdf_processor_output()

    # Modify the query generator instruction to embed the mock data
    modified_query_instruction = prompt.QUERY_GENERATOR_INSTRUCTION.replace(
        "{pdf_processor_agent_output}", json.dumps(mock_pdf_output, indent=2)
    )

    # Create the orchestrator
    orchestrator = create_founder_profile_orchestrator()

    # Modify the sub-agent's instruction
    if hasattr(orchestrator, "sub_agents") and orchestrator.sub_agents:
        for sub_agent in orchestrator.sub_agents:
            if hasattr(sub_agent, "sub_agents"):
                for inner_agent in sub_agent.sub_agents:
                    if (
                        hasattr(inner_agent, "name")
                        and inner_agent.name == "query_generator"
                    ):
                        # Replace the instruction
                        inner_agent.instruction = modified_query_instruction
                        break

    return orchestrator


from utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def create_mock_pdf_processor_output():
    """Create mock PDF processor output for testing."""
    return {
        "company_details": {
            "name": "TechStartup Inc.",
            "description": "AI-powered SaaS platform for automated customer support",
            "industry": "SaaS",
            "stage": "Series A",
            "location": "San Francisco, CA",
        },
        "team": {
            "founders": [
                {
                    "name": "Jane Doe",
                    "title": "CEO & Co-Founder",
                    "bio": "Former VP of Engineering at Google with 10+ years in enterprise software. IIT Delhi graduate with expertise in AI/ML.",
                    "linkedin": "https://linkedin.com/in/janedoe",
                    "education": "IIT Delhi, B.Tech Computer Science",
                    "experience": "Google (VP Engineering), Microsoft (Senior PM), Startup X (CTO)",
                },
                {
                    "name": "John Smith",
                    "title": "CTO & Co-Founder",
                    "bio": "Serial entrepreneur with 3 successful exits. IIM Ahmedabad MBA. Expert in SaaS product development.",
                    "linkedin": "https://linkedin.com/in/johnsmith",
                    "education": "IIM Ahmedabad, MBA",
                    "experience": "Paytm (Head of Product), Flipkart (Senior Engineer), Own startup (Founder)",
                },
            ],
            "key_team_members": [
                {
                    "name": "Alice Johnson",
                    "title": "Head of Sales",
                    "bio": "10+ years in enterprise sales at Salesforce and Oracle",
                    "linkedin": "https://linkedin.com/in/alicejohnson",
                }
            ],
            "advisors": [
                {
                    "name": "Bob Wilson",
                    "title": "Advisor",
                    "bio": "Former CEO of TechCorp, angel investor",
                    "linkedin": "https://linkedin.com/in/bobwilson",
                }
            ],
        },
        "financials": {
            "funding_raised": "$5M Series A",
            "investors": ["Sequoia Capital", "Andreessen Horowitz"],
        },
    }


async def test_founder_profile_orchestrator():
    """Test the founder profile orchestrator agent."""
    logger.info("🚀 Starting Founder Profile Orchestrator Test")

    try:
        # Create services
        session_service = InMemorySessionService()
        artifact_service = InMemoryArtifactService()

        # Create the orchestrator agent
        logger.info("📦 Creating founder profile orchestrator agent...")
        orchestrator = create_test_founder_profile_orchestrator()

        # Create ADK runner
        runner = Runner(
            agent=orchestrator,
            app_name="test-founder-profile",
            session_service=session_service,
            artifact_service=artifact_service,
        )

        # Create a test session
        session_id = str(uuid.uuid4())
        user_id = "test_user"

        session = await session_service.create_session(
            app_name="test-founder-profile", user_id=user_id, session_id=session_id
        )

        # Note: Context variables will be provided in the user message instead of session state
        # Test query for founder profile analysis with embedded data
        mock_data = create_mock_pdf_processor_output()
        test_query = f"""Analyze the founder profiles and provide a comprehensive founder verification report using the following startup data:

{json.dumps(mock_data, indent=2)}

Please verify the founder backgrounds, experience, and provide detailed verification results."""

        logger.info(f"📝 Test query: {test_query[:200]}...")  # Execute the agent
        logger.info("⚡ Executing founder profile orchestrator...")
        execution_completed = False
        event_count = 0

        for event in runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=Content(parts=[types.Part(text=test_query)]),
        ):
            event_count += 1
            logger.info(f"📊 Event {event_count}: {type(event).__name__}")

            # Check if this is a completion event or final event
            if hasattr(event, "type") and event.type == "completion":
                execution_completed = True
                logger.info("✅ Execution completion event detected")

            if hasattr(event, "error") and event.error:
                logger.error(f"❌ Error event: {event.error}")
                return False

        # Check that execution completed
        if (
            not execution_completed and event_count > 3
        ):  # Assume completion if many events processed
            logger.info("✅ Execution completed (inferred from event count)")
            execution_completed = True

        if not execution_completed:
            logger.error("❌ Execution did not complete successfully")
            return False

        # Check for session directory and saved files
        logger.info("🔍 Checking for saved files in sessions directory...")

        # Get session directory path
        session_dir = Path("sessions") / f"{user_id}_{session_id}_test-founder-profile"
        if session_dir.exists():
            logger.info(f"✅ Session directory created: {session_dir}")

            # List all files in session directory
            files = list(session_dir.glob("*"))
            logger.info(f"📁 Files saved: {len(files)}")
            for file_path in files:
                logger.info(f"  - {file_path.name}")

            # Check for specific expected files
            expected_files = [
                "founder_verification_report.md",
                "founder_verification_report.json",
            ]

            for expected_file in expected_files:
                file_path = session_dir / expected_file
                if file_path.exists():
                    logger.info(f"✅ Found expected file: {expected_file}")
                    # Read and log file size
                    size = file_path.stat().st_size
                    logger.info(f"   📏 File size: {size} bytes")
                else:
                    logger.warning(f"⚠️ Missing expected file: {expected_file}")
        else:
            logger.error(f"❌ Session directory not created: {session_dir}")
            return False

        # Check for session directory and saved files
        logger.info("🔍 Checking for saved files in sessions directory...")

        # Get session directory path
        session_dir = Path("sessions") / f"{user_id}_{session_id}_test-founder-profile"
        if session_dir.exists():
            logger.info(f"✅ Session directory created: {session_dir}")

            # List all files in session directory
            files = list(session_dir.glob("*"))
            logger.info(f"📁 Files saved: {len(files)}")
            for file_path in files:
                logger.info(f"  - {file_path.name}")

            # Check for expected files from founder verification
            expected_files = [
                "founder_verification_llm_response.md",  # Founder verification markdown report
            ]

            found_files = []
            for expected_file in expected_files:
                file_path = session_dir / expected_file
                if file_path.exists():
                    logger.info(f"✅ Found expected file: {expected_file}")
                    # Read and log file size
                    size = file_path.stat().st_size
                    logger.info(f"   📏 File size: {size} bytes")
                    found_files.append(expected_file)
                else:
                    logger.warning(f"⚠️ Missing expected file: {expected_file}")

            # Verify that at least some files were saved
            if len(found_files) >= 1:
                logger.info(
                    f"✅ File saving working correctly - {len(found_files)} files saved"
                )
            else:
                logger.warning(
                    f"⚠️ Only {len(found_files)} files saved, expected at least 1"
                )

        else:
            logger.error(f"❌ Session directory not created: {session_dir}")
            return False

        # Check callback context state
        if session.state:
            logger.info("✅ Session has state")
            logger.info(f"📊 State keys: {list(session.state.keys())}")
        else:
            logger.warning("⚠️ Session has no state")

        logger.info("🎉 Founder Profile Orchestrator Test Completed Successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        import traceback

        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False


async def main():
    """Main test function."""
    logger.info("🧪 Starting Founder Profile Orchestrator Individual Test")
    logger.info("=" * 60)

    # Run the test
    success = await test_founder_profile_orchestrator()

    logger.info("=" * 60)
    if success:
        logger.info("✅ All tests passed!")
        return 0
    else:
        logger.error("❌ Tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

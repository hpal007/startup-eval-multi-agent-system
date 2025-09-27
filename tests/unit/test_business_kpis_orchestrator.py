#!/usr/bin/env python3
"""
Test script for business_kpis_orchestrator individual functionality
"""

import asyncio
import json
import uuid
from pathlib import Path

from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai.types import Content

from workflow.business_kpis_orchestrator.agent import create_business_kpis_orchestrator

# Mock PDF processor output
MOCK_PDF_OUTPUT = {
    "financials": {
        "key_metrics": {
            "monthly_recurring_revenue": 50000,
            "customer_acquisition_cost": 500,
            "customer_lifetime_value": 5000,
            "churn_rate": 0.05,
        }
    },
    "market": {
        "total_addressable_market_TAM": 5000000000,
        "serviceable_available_market_SAM": 1000000000,
    },
    "company_purpose": {"one_liner": "AI-powered customer support platform"},
}


async def test_business_kpis_orchestrator():
    """Test the business KPIs orchestrator individually."""
    print("🧪 Testing Business KPIs Orchestrator individually...")

    # Create services
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()

    # Create the orchestrator agent
    agent = create_business_kpis_orchestrator()

    runner = Runner(
        agent=agent,
        app_name="test-business-kpis",
        session_service=session_service,
        artifact_service=artifact_service,
    )

    # Create a test session
    session_id = str(uuid.uuid4())
    user_id = "test_user"

    session = await session_service.create_session(
        app_name="test-business-kpis", user_id=user_id, session_id=session_id
    )

    # Note: Context variables will be provided in the user message instead of session state

    # Test query for business KPI analysis with embedded data
    test_query = f"""Analyze the business KPIs for this startup using the following data:

{json.dumps(MOCK_PDF_OUTPUT, indent=2)}

Please provide a comprehensive KPI analysis including industry classification, framework selection, and detailed KPI assessment."""

    print(f"📝 Test query: {test_query[:200]}...")

    # Run the agent
    try:
        results = []
        event_count = 0
        for event in runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=Content(parts=[types.Part(text=test_query)]),
        ):
            results.append(event)
            event_count += 1
            if event_count <= 5:  # Print more events to see progress
                print(f"📄 Event {event_count}: {type(event).__name__}")
                # Try to get content if available
                try:
                    if hasattr(event, "content") and event.content:
                        content_preview = str(event.content)[:100]
                        print(f"    Content: {content_preview}...")
                except:
                    pass

        print(f"✅ Business KPIs orchestrator completed with {len(results)} events")

        # Check if files were saved to sessions directory
        sessions_dir = Path("sessions")

        # Check multiple possible directory patterns
        found_session_dir = None
        for pattern in [
            f"{user_id}_{session_id}_test-business-kpis",
            f"{user_id}_session_{session_id}_test-business-kpis",
            f"{user_id}_{session_id}_test-business-kpis",
        ]:
            candidate_dir = sessions_dir / pattern
            if candidate_dir.exists():
                found_session_dir = candidate_dir
                break

        if found_session_dir:
            print(f"📁 Session directory created: {found_session_dir}")
            files = list(found_session_dir.glob("*"))
            print(f"📄 Files saved: {len(files)}")
            for file in files:
                print(f"  - {file.name}")
                # Read and show a bit of the content
                try:
                    content = file.read_text()
                    preview = content[:500] + "..." if len(content) > 500 else content
                    print(f"    Content preview: {preview}")
                except Exception as e:
                    print(f"    (binary file or read error: {e})")
        else:
            print("❌ No session directory found")
            # List all session directories to see what's there
            if sessions_dir.exists():
                all_dirs = [d for d in sessions_dir.iterdir() if d.is_dir()]
                print(f"📁 Existing session directories: {all_dirs}")

        return len(results) > 0  # Success if we got any events

    except Exception as e:
        print(f"❌ Business KPIs orchestrator test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_business_kpis_orchestrator())
    print(
        f"\n{'✅ PASSED' if success else '❌ FAILED'}: Business KPIs Orchestrator individual test"
    )

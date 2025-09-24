import asyncio
import logging
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from workflow.master.agent import root_agent

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async def test_master_agent():
    """Test the master agent to see if it generates files for all sub-orchestrators."""

    # Session Service for managing conversation history and state
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()

    # Runner for orchestrating the agent execution
    runner = Runner(
        agent=root_agent,
        app_name="test_app",
        session_service=session_service,
        artifact_service=artifact_service,
    )

    user_id = "test_user"
    session_id = "test_session"

    try:
        await session_service.create_session(
            app_name="test_app", user_id=user_id, session_id=session_id
        )
        print("Session created successfully")
    except Exception as e:
        print(f"Warning: Could not create session: {e}")

    # Test query
    query = "Please evaluate the startup pitch document and provide a comprehensive analysis."

    print(f"Running master agent with query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role="user", parts=[types.Part(text=query)])

    # Run the agent
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
                print(f"Final response: {final_response}")
            break

    print("Master agent execution completed")

if __name__ == "__main__":
    asyncio.run(test_master_agent())
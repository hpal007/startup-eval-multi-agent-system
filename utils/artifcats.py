from google.adk.tools.tool_context import ToolContext


def save_to_state(key: str, value, tool_context: ToolContext):
    tool_context.state[key] = value
    return True

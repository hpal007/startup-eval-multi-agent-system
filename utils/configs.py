import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class to manage environment variables for agents."""

    # Gemini/LLM Model configurations
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

    # Other model configurations
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")

    # Agent-specific configurations
    ABC_AGENT_MODEL: str = os.getenv("ABC_AGENT_MODEL", GEMINI_MODEL)
    PROCESS_PDF_AGENT_MODEL: str = os.getenv("PROCESS_PDF_AGENT_MODEL", GEMINI_MODEL)

    # System configurations
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes", "on")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # LLM Generation configurations
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))

    @classmethod
    def get_model_for_agent(cls, agent_name: str) -> str:
        """
        Get the model configuration for a specific agent.

        Args:
            agent_name: Name of the agent (e.g., 'abc_agent', 'process_pdf')

        Returns:
            Model name to use for the agent
        """
        env_var = f"{agent_name.upper()}_MODEL"
        return os.getenv(env_var, cls.GEMINI_MODEL)

    @classmethod
    def validate_required_configs(cls) -> None:
        """Validate that required configurations are set."""
        required_configs = []

        if not cls.GEMINI_API_KEY and cls.GEMINI_MODEL.startswith("gemini"):
            required_configs.append("GEMINI_API_KEY")

        if not cls.OPENAI_API_KEY and (
            cls.GEMINI_MODEL.startswith("gpt") or cls.OPENAI_MODEL.startswith("gpt")
        ):
            required_configs.append("OPENAI_API_KEY")

        if required_configs:
            raise ValueError(
                f"Missing required environment variables: {', '.join(required_configs)}"
            )


# Create a global config instance
config = Config()

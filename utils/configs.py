import logging
import os
from typing import Any

from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Configuration class to manage environment variables for agents."""

    OLLAMA = True
    # Gemini/LLM Model configurations
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "ollama/gemma3:latest")

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
        if "OLLAMA" in env_var:

            MODEL = LiteLlm(
                model=f"ollama/{os.getenv('OLLAMA_MODEL', 'gemma3:latest')}",
                api_base=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            )
            return MODEL
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

    @classmethod
    def get_config_value(
        cls, key: str, default: Any = None, type_cast: type = str
    ) -> Any:
        """
        Get a configuration value from environment variables with type casting.

        Args:
            key: Environment variable key
            default: Default value if not found
            type_cast: Type to cast the value to

        Returns:
            Configuration value
        """
        value = os.environ.get(key, default)
        if value is not None and type_cast != str:
            try:
                if type_cast == bool:
                    return str(value).lower() in ("true", "1", "yes", "on")
                return type_cast(value)
            except (ValueError, TypeError):
                logger.warning(
                    f"Could not cast {key}='{value}' to {type_cast.__name__}, using default"
                )
                return default
        return value


# Create a global config instance
config = Config()

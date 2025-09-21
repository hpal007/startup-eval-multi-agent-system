"""
Competitor Extractor Agent

Specialized agent for parsing and categorizing competitor information from input data.
Extracts competitor mentions, competitive advantages, and validates data completeness.
"""

import json
import logging

from google.adk.agents import Agent
from google.genai import types

from utils.configs import config
from utils.models import (
    CompetitiveAdvantage,
    CompetitiveAdvantageCategory,
    CompetitorExtractionResult,
    CompetitorMention,
    CompetitorType,
    DataQuality,
    MarketPositioning,
    ValidationStatus,
)

from . import prompt

logger = logging.getLogger(__name__)
MODEL = config.get_model_for_agent("abc_agent")


def competitor_validation_callback(callback_context, **kwargs):
    """Callback to validate competitor extraction completeness."""
    # TODO - need to update this
    logger.info("\n🤖 Competitor extraction completed - validating results\n")

    # Extract and validate the response
    llm_response = kwargs.get("llm_response")
    if llm_response:
        # Extract text content from the response
        try:
            response_dict = llm_response.dict()
            content = response_dict.get("content", "")
            response = content.get("parts", [{}])[0].get("text", "")
        except (AttributeError, IndexError):
            response = getattr(llm_response, "content", "")
    else:
        response = ""

    if response:
        try:
            # Try to parse JSON response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_content = response[json_start:json_end].strip()
            else:
                json_content = response

            parsed_data = json.loads(json_content)

            # Validate required fields
            required_fields = [
                "extraction_summary",
                "competitors",
                "competitive_advantages",
                "market_positioning",
                "data_quality",
            ]

            missing_fields = [
                field for field in required_fields if field not in parsed_data
            ]
            if missing_fields:
                logger.warning(
                    f"Missing required fields in extraction result: {missing_fields}"
                )
            else:
                logger.info("✅ Competitor extraction validation passed")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse competitor extraction JSON: {e}")
        except Exception as e:
            logger.error(f"Error validating competitor extraction: {e}")


def competitor_setup_callback(callback_context, **kwargs):
    """Setup callback for competitor extractor agent."""
    logger.info(
        "\n🤖: competitor_extractor_agent: Starting competitor extraction - parsing competitor information\n"
    )


def parse_extraction_result(response: str) -> CompetitorExtractionResult:
    """
    Parse the agent response into a structured CompetitorExtractionResult.

    Args:
        response: Raw response from the agent

    Returns:
        Parsed CompetitorExtractionResult
    """
    # TODO - need to update this
    try:
        # Extract JSON from response
        if "```json" in response:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            json_content = response[json_start:json_end].strip()
        else:
            json_content = response

        parsed_data = json.loads(json_content)

        # Parse competitors
        competitors = []
        for comp_data in parsed_data.get("competitors", []):
            competitor = CompetitorMention(
                name=comp_data.get("name", ""),
                category=CompetitorType(comp_data.get("category", "direct")),
                description=comp_data.get("description", ""),
                claimed_differentiator=comp_data.get("claimed_differentiator", ""),
                validation_status=ValidationStatus(
                    comp_data.get("validation_status", "incomplete")
                ),
            )
            competitors.append(competitor)

        # Parse competitive advantages
        advantages = []
        for adv_data in parsed_data.get("competitive_advantages", []):
            advantage = CompetitiveAdvantage(
                claim=adv_data.get("claim", ""),
                category=CompetitiveAdvantageCategory(
                    adv_data.get("category", "features")
                ),
                evidence_provided=adv_data.get("evidence_provided", ""),
                validation_needed=adv_data.get("validation_needed", True),
            )
            advantages.append(advantage)

        # Parse market positioning
        positioning_data = parsed_data.get("market_positioning", {})
        positioning = MarketPositioning(
            target_market=positioning_data.get("target_market", ""),
            market_segment=positioning_data.get("market_segment", ""),
            positioning_statement=positioning_data.get("positioning_statement", ""),
        )

        # Parse data quality
        quality_data = parsed_data.get("data_quality", {})
        data_quality = DataQuality(
            completeness_score=quality_data.get("completeness_score", 0.0),
            consistency_score=quality_data.get("consistency_score", 0.0),
            missing_information=quality_data.get("missing_information", []),
            validation_flags=quality_data.get("validation_flags", []),
        )

        # Create result
        result = CompetitorExtractionResult(
            extraction_summary=parsed_data.get("extraction_summary", {}),
            competitors=competitors,
            competitive_advantages=advantages,
            market_positioning=positioning,
            data_quality=data_quality,
        )

        return result

    except Exception as e:
        logger.error(f"Error parsing competitor extraction result: {e}")
        # Return empty result on error
        return CompetitorExtractionResult(
            extraction_summary={},
            competitors=[],
            competitive_advantages=[],
            market_positioning=MarketPositioning(
                target_market="", market_segment="", positioning_statement=""
            ),
            data_quality=DataQuality(),
        )


def create_competitor_extractor_agent():
    """Create a fresh instance of the competitor extractor agent."""
    return Agent(
        model=MODEL,
        name="competitor_extractor_agent",
        description="Extracts and categorizes competitor information from startup input data",
        instruction=prompt.COMPETITOR_EXTRACTOR_INSTRUCTION,
        tools=[],  # No external tools needed for extraction
        before_agent_callback=competitor_setup_callback,
        after_model_callback=competitor_validation_callback,
        generate_content_config=types.GenerateContentConfig(
            temperature=config.TEMPERATURE,
        ),
        include_contents="default",
    )


competitor_extractor_agent = create_competitor_extractor_agent()

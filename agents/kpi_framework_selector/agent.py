"""KPI Framework Selector agent for industry-specific KPI framework selection."""

import logging

from google.adk.agents import Agent
from google.genai import types

from utils.configs import config

from . import prompt

MODEL = config.get_model_for_agent("abc_agent")


logger = logging.getLogger(__name__)


def kpi_framework_setup_callback(callback_context, **kwargs):
    """Setup callback for KPI Framework Selector agent."""
    logger.info(
        "\n🤖: kpi_framework_selector_agent: Starting KPI framework selection and customization\n"
    )


def kpi_framework_validation_callback(callback_context, **kwargs):
    """Validation callback for KPI Framework Selector agent."""
    logger.info(
        "\n🤖 KPI framework selection completed - validating framework completeness\n"
    )


# KPI Framework Selection Tools
def select_industry_kpi_framework(
    industry_classification: dict,
    growth_stage: str,
    business_model: str,
    current_kpis: dict
) -> dict:
    """
    Select and customize appropriate KPI framework for the startup.
    
    Args:
        industry_classification: Industry classification results with primary_industry, confidence_score, etc.
        growth_stage: Current growth stage (seed, early, growth, mature)
        business_model: Description of the business model
        current_kpis: Current KPI values provided by the startup
        
    Returns:
        Customized KPI framework with primary and secondary KPIs
    """
    from tools.kpi_framework_tools import (
        convert_framework_dict_to_model,
        select_kpi_framework,
        validate_framework_completeness,
    )
    from utils.models import GrowthStage, IndustryClassification

    # Convert inputs to proper models
    industry_class = IndustryClassification(**industry_classification)

    # Normalize growth stage to enum-friendly value
    def _normalize_growth_stage(value: str) -> str:
        if not value:
            return "early"
        text = value.strip().lower().replace("-", " ").replace("_", " ")
        text = text.replace("stage", "").strip()
        if "seed" in text:
            return "seed"
        if "early" in text:
            return "early"
        if "growth" in text:
            return "growth"
        if "mature" in text or "late" in text:
            return "mature"
        # default fallback
        return text

    growth_stage_normalized = _normalize_growth_stage(growth_stage)
    growth_stage_enum = GrowthStage(growth_stage_normalized)

    # Select and customize framework
    framework_dict = select_kpi_framework(
        industry_class, growth_stage_enum, business_model, current_kpis
    )

    # Convert to KPIFramework model
    framework_model = convert_framework_dict_to_model(framework_dict)

    # Validate completeness
    validation_status = validate_framework_completeness(framework_model, current_kpis)

    return {
        "framework": framework_model.dict(),
        "validation_status": validation_status.value,
        "customization_notes": f"Framework customized for {growth_stage} stage {industry_class.primary_industry} company"
    }


def validate_kpi_framework_completeness(framework: dict, current_kpis: dict) -> dict:
    """
    Validate the completeness and relevance of a KPI framework.
    
    Args:
        framework: KPI framework dictionary
        current_kpis: Available KPI data
        
    Returns:
        Validation results with status and recommendations
    """
    from tools.kpi_framework_tools import validate_framework_completeness
    from utils.models import KPIFramework

    def _coerce_kpi_list(kpis):
        # Accept strings or dicts; convert strings to minimal KPIDefinition-like dicts
        if not isinstance(kpis, list):
            return []
        coerced = []
        for item in kpis:
            if isinstance(item, dict):
                # Ensure required fields exist and meet minimal constraints
                name = item.get("name") or item.get("kpi_name") or "Unknown KPI"
                desc = item.get("description") or "Auto-generated description"
                calc = item.get("calculation_method") or item.get("formula") or "Auto-generated calculation method"
                weight = item.get("importance_weight", 1.0)
                rationale = item.get("rationale") or "Auto-coerced from LLM output"
                coerced.append({
                    "name": name,
                    "description": desc,
                    "calculation_method": calc,
                    "importance_weight": float(weight) if isinstance(weight, (int, float)) else 1.0,
                    "rationale": rationale,
                })
            elif isinstance(item, str):
                coerced.append({
                    "name": item,
                    "description": "Auto-generated description",
                    "calculation_method": "Auto-generated calculation method",
                    "importance_weight": 1.0,
                    "rationale": "Auto-coerced from LLM output",
                })
        # Normalize weights if present
        weights = [k.get("importance_weight") for k in coerced if isinstance(k, dict) and isinstance(k.get("importance_weight"), (int, float))]
        total = sum(weights) if weights else 0.0
        if total > 0:
            for k in coerced:
                if isinstance(k, dict) and isinstance(k.get("importance_weight"), (int, float)):
                    k["importance_weight"] = float(k["importance_weight"]) / total
        return coerced

    def _coerce_framework_dict(raw):
        # Allow nested {"framework": {...}}
        data = raw.get("framework") if isinstance(raw, dict) and "framework" in raw else raw
        if not isinstance(data, dict):
            data = {}
        industry = data.get("industry") or data.get("primary_industry") or "Unknown Industry"
        primary_kpis = _coerce_kpi_list(data.get("primary_kpis") or [])
        secondary_kpis = _coerce_kpi_list(data.get("secondary_kpis") or [])
        return {
            "industry": industry,
            "primary_kpis": primary_kpis,
            "secondary_kpis": secondary_kpis,
        }

    # Coerce potentially free-form LLM output into a valid KPIFramework dict
    framework = _coerce_framework_dict(framework)
    try:
        framework_model = KPIFramework(**framework)
    except Exception as e:
        # Last-resort fallback to prevent runtime hangs: return incomplete with basic recommendations
        logger = logging.getLogger(__name__)
        logger.error("KPIFramework validation failed after coercion; returning incomplete result", exc_info=e)
        primary_names = [k.get("name", "KPI") for k in framework.get("primary_kpis", []) if isinstance(k, dict)]
        missing_kpis = primary_names[:5]
        return {
            "validation_status": "incomplete",
            "coverage_ratio": 0.0,
            "matched_kpis": [],
            "missing_kpis": missing_kpis,
            "recommendations": _generate_framework_recommendations(type("S", (), {"value": "incomplete"})(), missing_kpis),
        }

    validation_status = validate_framework_completeness(framework_model, current_kpis)

    # Calculate coverage metrics
    primary_kpi_names = {kpi.name for kpi in framework_model.primary_kpis}
    available_kpi_names = set(current_kpis.keys())

    matched_kpis = []
    missing_kpis = []

    for kpi_name in primary_kpi_names:
        if (kpi_name in available_kpi_names or
            any(kpi_name.lower() in available_name.lower() or
                available_name.lower() in kpi_name.lower()
                for available_name in available_kpi_names)):
            matched_kpis.append(kpi_name)
        else:
            missing_kpis.append(kpi_name)

    coverage_ratio = len(matched_kpis) / len(primary_kpi_names) if primary_kpi_names else 0

    return {
        "validation_status": validation_status.value,
        "coverage_ratio": coverage_ratio,
        "matched_kpis": matched_kpis,
        "missing_kpis": missing_kpis,
        "recommendations": _generate_framework_recommendations(validation_status, missing_kpis)
    }


def _generate_framework_recommendations(validation_status, missing_kpis):
    """Generate recommendations based on framework validation."""
    recommendations = []

    if validation_status.value == "missing_info":
        recommendations.append("Critical KPI data is missing. Consider collecting data for the following metrics:")
        recommendations.extend([f"- {kpi}" for kpi in missing_kpis[:5]])  # Top 5 missing KPIs
    elif validation_status.value == "incomplete":
        recommendations.append("Some important KPIs are missing. Consider tracking:")
        recommendations.extend([f"- {kpi}" for kpi in missing_kpis[:3]])  # Top 3 missing KPIs
    else:
        recommendations.append("KPI framework is well-aligned with available data.")
        recommendations.append("Consider expanding tracking to secondary KPIs for deeper insights.")

    return recommendations


kpi_framework_selector_agent = Agent(
    model=MODEL,
    name="kpi_framework_selector_agent",
    description="Selects and customizes industry-specific KPI frameworks based on industry classification, growth stage, and business model",
    instruction=prompt.KPI_FRAMEWORK_SELECTOR_INSTRUCTION,
    tools=[select_industry_kpi_framework, validate_kpi_framework_completeness],
    before_agent_callback=kpi_framework_setup_callback,
    after_model_callback=kpi_framework_validation_callback,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.TEMPERATURE,
    ),
    include_contents="default",
)

"""
Industry Classifier Agent

Specialized agent for classifying startups into appropriate industry sectors
for KPI framework selection and benchmarking analysis.
"""

import logging
from typing import Any

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types


from utils.configs import config
from utils.helper import get_session_dir, save_llm_response_to_file, save_state_to_file

from . import prompt

logger = logging.getLogger(__name__)
MODEL = config.get_model_for_agent("abc_agent")


def industry_taxonomy_matching_tool(
    startup_description: str, business_model: str
) -> dict[str, Any]:
    """
    Advanced tool for matching startup characteristics to industry taxonomy with weighted scoring.

    Args:
        startup_description: Description of the startup's business
        business_model: Business model description

    Returns:
        Dictionary with industry matching results and confidence scores
    """
    # Enhanced industry keyword mappings with weights
    industry_keywords = {
        "saas": {
            "high_weight": [
                "saas",
                "software as a service",
                "subscription software",
                "cloud software",
            ],
            "medium_weight": [
                "software",
                "subscription",
                "cloud",
                "platform",
                "api",
                "dashboard",
            ],
            "low_weight": ["analytics", "automation", "integration", "workflow"],
        },
        "ecommerce": {
            "high_weight": [
                "ecommerce",
                "e-commerce",
                "online store",
                "retail platform",
            ],
            "medium_weight": [
                "retail",
                "marketplace",
                "shopping",
                "store",
                "products",
                "inventory",
            ],
            "low_weight": ["fulfillment", "shipping", "catalog", "checkout"],
        },
        "fintech": {
            "high_weight": [
                "fintech",
                "financial technology",
                "payment processing",
                "digital banking",
            ],
            "medium_weight": [
                "financial",
                "payment",
                "banking",
                "lending",
                "investment",
                "insurance",
            ],
            "low_weight": ["crypto", "blockchain", "wallet", "trading"],
        },
        "healthcare": {
            "high_weight": [
                "healthcare",
                "health tech",
                "medical technology",
                "digital health",
            ],
            "medium_weight": [
                "medical",
                "health",
                "biotech",
                "pharmaceutical",
                "clinical",
            ],
            "low_weight": ["patient", "therapy", "diagnosis", "treatment"],
        },
        "marketplace": {
            "high_weight": [
                "marketplace",
                "two-sided platform",
                "multi-sided platform",
            ],
            "medium_weight": [
                "platform",
                "network",
                "connect",
                "matching",
                "gig economy",
            ],
            "low_weight": ["commission", "take rate", "network effects"],
        },
        "consumer": {
            "high_weight": ["consumer app", "b2c platform", "lifestyle brand"],
            "medium_weight": [
                "consumer",
                "lifestyle",
                "entertainment",
                "gaming",
                "social",
            ],
            "low_weight": ["mobile app", "user engagement", "viral"],
        },
        "enterprise": {
            "high_weight": [
                "enterprise software",
                "b2b services",
                "business solutions",
            ],
            "medium_weight": [
                "enterprise",
                "b2b",
                "business",
                "consulting",
                "services",
            ],
            "low_weight": ["professional", "corporate", "workflow"],
        },
        "hardware": {
            "high_weight": [
                "hardware",
                "iot platform",
                "smart devices",
                "manufacturing",
            ],
            "medium_weight": ["device", "physical product", "sensor", "embedded"],
            "low_weight": ["connectivity", "firmware", "components"],
        },
    }

    # Revenue model indicators with confidence weights
    revenue_models = {
        "subscription": {
            "indicators": [
                "subscription",
                "recurring",
                "monthly",
                "annual",
                "mrr",
                "arr",
                "saas",
            ],
            "confidence_boost": 0.2,
        },
        "transaction": {
            "indicators": [
                "transaction",
                "commission",
                "take rate",
                "gmv",
                "marketplace",
                "payment",
            ],
            "confidence_boost": 0.15,
        },
        "product_sales": {
            "indicators": [
                "sales",
                "product",
                "unit",
                "inventory",
                "retail",
                "ecommerce",
            ],
            "confidence_boost": 0.1,
        },
        "advertising": {
            "indicators": [
                "advertising",
                "ads",
                "sponsored",
                "monetization",
                "impressions",
            ],
            "confidence_boost": 0.1,
        },
        "freemium": {
            "indicators": ["freemium", "free tier", "premium", "upgrade", "conversion"],
            "confidence_boost": 0.15,
        },
        "licensing": {
            "indicators": [
                "licensing",
                "royalty",
                "ip",
                "patent",
                "technology licensing",
            ],
            "confidence_boost": 0.1,
        },
    }

    text_to_analyze = f"{startup_description} {business_model}".lower()

    # Calculate weighted industry scores
    industry_scores = {}
    for industry, keyword_groups in industry_keywords.items():
        total_score = 0
        max_possible_score = 0

        # High weight keywords (3x)
        for keyword in keyword_groups["high_weight"]:
            max_possible_score += 3
            if keyword in text_to_analyze:
                total_score += 3

        # Medium weight keywords (2x)
        for keyword in keyword_groups["medium_weight"]:
            max_possible_score += 2
            if keyword in text_to_analyze:
                total_score += 2

        # Low weight keywords (1x)
        for keyword in keyword_groups["low_weight"]:
            max_possible_score += 1
            if keyword in text_to_analyze:
                total_score += 1

        if max_possible_score > 0:
            industry_scores[industry] = total_score / max_possible_score

    # Calculate revenue model scores and confidence boosts
    revenue_scores = {}
    confidence_boosts = {}
    for model, config in revenue_models.items():
        score = sum(1 for keyword in config["indicators"] if keyword in text_to_analyze)
        if score > 0:
            revenue_scores[model] = score / len(config["indicators"])
            confidence_boosts[model] = config["confidence_boost"]

    # Determine top classifications
    top_industry = (
        max(industry_scores.items(), key=lambda x: x[1]) if industry_scores else None
    )
    top_revenue_model = (
        max(revenue_scores.items(), key=lambda x: x[1]) if revenue_scores else None
    )

    return {
        "industry_scores": industry_scores,
        "revenue_model_scores": revenue_scores,
        "confidence_boosts": confidence_boosts,
        "top_industry": top_industry,
        "top_revenue_model": top_revenue_model,
        "classification_strength": max(industry_scores.values())
        if industry_scores
        else 0.0,
    }


def business_model_analysis_tool(
    business_model: str, target_customers: str
) -> dict[str, Any]:
    """
    Enhanced tool for analyzing business model characteristics and customer segments.

    Args:
        business_model: Business model description
        target_customers: Target customer description

    Returns:
        Dictionary with comprehensive business model analysis results
    """
    # Customer segment indicators with confidence weights
    customer_segments = {
        "b2b": {
            "strong": [
                "enterprise",
                "b2b",
                "business-to-business",
                "corporate clients",
            ],
            "medium": ["business", "company", "organization", "professional"],
            "weak": ["workplace", "office", "team", "department"],
        },
        "b2c": {
            "strong": ["consumer", "b2c", "business-to-consumer", "individual users"],
            "medium": ["individual", "personal", "customer", "user"],
            "weak": ["people", "person", "end-user", "retail"],
        },
        "b2b2c": {
            "strong": ["b2b2c", "white label", "partner platform"],
            "medium": ["partner", "reseller", "channel", "distributor"],
            "weak": ["indirect", "through partners", "via partners"],
        },
        "government": {
            "strong": ["government", "public sector", "municipal"],
            "medium": ["federal", "state", "local government"],
            "weak": ["civic", "public", "administration"],
        },
    }

    # Scalability indicators with impact scores
    scalability_factors = {
        "network_effects": {
            "indicators": [
                "network",
                "viral",
                "referral",
                "community",
                "social",
                "network effects",
            ],
            "impact_score": 3,
        },
        "automation": {
            "indicators": [
                "automated",
                "ai",
                "machine learning",
                "algorithm",
                "self-service",
                "no-code",
            ],
            "impact_score": 2,
        },
        "digital_delivery": {
            "indicators": [
                "digital",
                "cloud",
                "online",
                "remote",
                "virtual",
                "software",
            ],
            "impact_score": 2,
        },
        "recurring_revenue": {
            "indicators": [
                "recurring",
                "subscription",
                "retention",
                "lifetime value",
                "mrr",
                "arr",
            ],
            "impact_score": 3,
        },
        "marketplace_dynamics": {
            "indicators": [
                "marketplace",
                "platform",
                "two-sided",
                "multi-sided",
                "ecosystem",
            ],
            "impact_score": 3,
        },
        "data_network_effects": {
            "indicators": [
                "data",
                "machine learning",
                "personalization",
                "recommendation",
                "intelligence",
            ],
            "impact_score": 2,
        },
    }

    text_to_analyze = f"{business_model} {target_customers}".lower()

    # Analyze customer segments with weighted scoring
    segment_scores = {}
    for segment, indicators in customer_segments.items():
        total_score = 0
        max_score = 0

        # Strong indicators (3x weight)
        for indicator in indicators["strong"]:
            max_score += 3
            if indicator in text_to_analyze:
                total_score += 3

        # Medium indicators (2x weight)
        for indicator in indicators["medium"]:
            max_score += 2
            if indicator in text_to_analyze:
                total_score += 2

        # Weak indicators (1x weight)
        for indicator in indicators["weak"]:
            max_score += 1
            if indicator in text_to_analyze:
                total_score += 1

        if max_score > 0:
            segment_scores[segment] = total_score / max_score

    # Analyze scalability factors with impact weighting
    scalability_analysis = {}
    total_scalability_score = 0
    for factor, config in scalability_factors.items():
        matches = sum(
            1 for indicator in config["indicators"] if indicator in text_to_analyze
        )
        if matches > 0:
            factor_score = (matches / len(config["indicators"])) * config[
                "impact_score"
            ]
            scalability_analysis[factor] = {
                "presence": matches > 0,
                "strength": matches / len(config["indicators"]),
                "weighted_score": factor_score,
            }
            total_scalability_score += factor_score

    # Determine primary customer segment
    primary_segment = (
        max(segment_scores.items(), key=lambda x: x[1])[0]
        if segment_scores
        else "unknown"
    )

    return {
        "customer_segments": segment_scores,
        "scalability_analysis": scalability_analysis,
        "primary_segment": primary_segment,
        "total_scalability_score": total_scalability_score,
        "scalability_rating": "high"
        if total_scalability_score >= 6
        else "medium"
        if total_scalability_score >= 3
        else "low",
        "segment_confidence": max(segment_scores.values()) if segment_scores else 0.0,
    }


def industry_classification_algorithm(
    startup_description: str,
    business_model: str,
    target_customers: str,
    current_kpis: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Comprehensive industry classification algorithm with confidence scoring.

    Args:
        startup_description: Description of the startup's business
        business_model: Business model description
        target_customers: Target customer description
        current_kpis: Current KPI data (optional)

    Returns:
        Dictionary with complete classification results and confidence scores
    """
    # Get taxonomy matching results
    taxonomy_results = industry_taxonomy_matching_tool(
        startup_description, business_model
    )

    # Get business model analysis
    business_analysis = business_model_analysis_tool(business_model, target_customers)

    # Industry-specific KPI indicators (if KPI data is available)
    kpi_indicators = {}
    if current_kpis:
        kpi_indicators = analyze_kpi_indicators(current_kpis)

    # Calculate overall confidence score
    confidence_factors = {
        "taxonomy_strength": taxonomy_results.get("classification_strength", 0.0),
        "business_model_clarity": business_analysis.get("segment_confidence", 0.0),
        "scalability_indicators": min(
            business_analysis.get("total_scalability_score", 0) / 10, 1.0
        ),
        "kpi_alignment": kpi_indicators.get("alignment_score", 0.0)
        if kpi_indicators
        else 0.0,
    }

    # Weighted confidence calculation
    weights = {
        "taxonomy_strength": 0.4,
        "business_model_clarity": 0.3,
        "scalability_indicators": 0.2,
        "kpi_alignment": 0.1,
    }

    overall_confidence = sum(
        confidence_factors[factor] * weights[factor] for factor in confidence_factors
    )

    # Determine primary and secondary industries
    industry_scores = taxonomy_results.get("industry_scores", {})
    sorted_industries = sorted(
        industry_scores.items(), key=lambda x: x[1], reverse=True
    )

    primary_industry = sorted_industries[0][0] if sorted_industries else "unknown"
    secondary_industries = [
        industry for industry, score in sorted_industries[1:3] if score > 0.3
    ]

    # Generate industry code (simplified NAICS-like)
    industry_codes = {
        "saas": "541511",
        "ecommerce": "454110",
        "fintech": "522320",
        "healthcare": "621111",
        "marketplace": "425110",
        "consumer": "713290",
        "enterprise": "541611",
        "hardware": "334111",
    }

    return {
        "primary_industry": primary_industry,
        "secondary_industries": secondary_industries,
        "confidence_score": round(overall_confidence, 3),
        "industry_code": industry_codes.get(primary_industry, "999999"),
        "business_model_type": business_analysis.get("primary_segment", "unknown"),
        "classification_rationale": generate_classification_rationale(
            taxonomy_results, business_analysis, confidence_factors
        ),
        "key_indicators": extract_key_indicators(taxonomy_results, business_analysis),
        "recommended_kpi_frameworks": get_recommended_kpi_frameworks(primary_industry),
        "industry_characteristics": {
            "revenue_model": taxonomy_results.get("top_revenue_model", ["unknown", 0])[
                0
            ]
            if taxonomy_results.get("top_revenue_model")
            else "unknown",
            "customer_segment": business_analysis.get("primary_segment", "unknown"),
            "delivery_mechanism": determine_delivery_mechanism(
                startup_description, business_model
            ),
            "scalability_factors": list(
                business_analysis.get("scalability_analysis", {}).keys()
            ),
        },
        "confidence_factors": {
            "supporting_evidence": generate_supporting_evidence(
                taxonomy_results, business_analysis
            ),
            "uncertainty_factors": identify_uncertainty_factors(confidence_factors),
            "additional_info_needed": suggest_additional_info(
                overall_confidence, confidence_factors
            ),
        },
    }


def analyze_kpi_indicators(current_kpis: dict[str, Any]) -> dict[str, Any]:
    """Analyze KPI data to infer industry alignment."""
    kpi_industry_mapping = {
        "saas": ["arr", "mrr", "churn_rate", "cac", "ltv", "nps"],
        "ecommerce": [
            "gmv",
            "conversion_rate",
            "aov",
            "cart_abandonment",
            "inventory_turnover",
        ],
        "fintech": [
            "transaction_volume",
            "aum",
            "loan_origination",
            "compliance_score",
        ],
        "healthcare": [
            "patient_outcomes",
            "clinical_trials",
            "regulatory_approvals",
            "r_and_d_spend",
        ],
        "marketplace": ["gmv", "take_rate", "network_effects", "user_engagement"],
        "consumer": [
            "dau",
            "mau",
            "engagement_rate",
            "viral_coefficient",
            "retention_rate",
        ],
        "enterprise": [
            "revenue_per_client",
            "client_retention",
            "utilization_rate",
            "project_margin",
        ],
        "hardware": [
            "unit_sales",
            "manufacturing_cost",
            "inventory_turnover",
            "product_margin",
        ],
    }

    kpi_keys = [key.lower().replace(" ", "_") for key in current_kpis]

    industry_alignment = {}
    for industry, expected_kpis in kpi_industry_mapping.items():
        matches = sum(1 for kpi in expected_kpis if kpi in kpi_keys)
        if matches > 0:
            industry_alignment[industry] = matches / len(expected_kpis)

    best_alignment = (
        max(industry_alignment.items(), key=lambda x: x[1])
        if industry_alignment
        else ("unknown", 0.0)
    )

    return {
        "industry_alignment": industry_alignment,
        "best_match": best_alignment[0],
        "alignment_score": best_alignment[1],
    }


def generate_classification_rationale(
    taxonomy_results, business_analysis, confidence_factors
):
    """Generate human-readable rationale for classification."""
    rationale_parts = []

    if taxonomy_results.get("top_industry"):
        industry, score = taxonomy_results["top_industry"]
        rationale_parts.append(f"Strong {industry} indicators (score: {score:.2f})")

    if business_analysis.get("primary_segment") != "unknown":
        segment = business_analysis["primary_segment"]
        rationale_parts.append(f"Clear {segment} business model")

    scalability_rating = business_analysis.get("scalability_rating", "unknown")
    if scalability_rating != "unknown":
        rationale_parts.append(f"{scalability_rating} scalability potential")

    return (
        "; ".join(rationale_parts)
        if rationale_parts
        else "Limited classification indicators available"
    )


def extract_key_indicators(taxonomy_results, business_analysis):
    """Extract key indicators that led to classification."""
    indicators = []

    if taxonomy_results.get("top_industry"):
        indicators.append(f"Industry: {taxonomy_results['top_industry'][0]}")

    if taxonomy_results.get("top_revenue_model"):
        indicators.append(f"Revenue Model: {taxonomy_results['top_revenue_model'][0]}")

    if business_analysis.get("primary_segment") != "unknown":
        indicators.append(f"Customer Segment: {business_analysis['primary_segment']}")

    scalability_factors = list(business_analysis.get("scalability_analysis", {}).keys())
    if scalability_factors:
        indicators.append(f"Scalability: {', '.join(scalability_factors[:2])}")

    return indicators


def get_recommended_kpi_frameworks(industry):
    """Get recommended KPI frameworks for the classified industry."""
    frameworks = {
        "saas": [
            "SaaS Metrics Framework",
            "Recurring Revenue Framework",
            "Customer Success Framework",
        ],
        "ecommerce": [
            "E-commerce Performance Framework",
            "Retail Analytics Framework",
            "Customer Journey Framework",
        ],
        "fintech": [
            "Financial Services Framework",
            "Regulatory Compliance Framework",
            "Risk Management Framework",
        ],
        "healthcare": [
            "Healthcare Outcomes Framework",
            "Clinical Development Framework",
            "Regulatory Milestone Framework",
        ],
        "marketplace": [
            "Platform Economics Framework",
            "Network Effects Framework",
            "Multi-sided Market Framework",
        ],
        "consumer": [
            "Consumer Engagement Framework",
            "Mobile App Framework",
            "Viral Growth Framework",
        ],
        "enterprise": [
            "B2B Services Framework",
            "Client Success Framework",
            "Professional Services Framework",
        ],
        "hardware": [
            "Product Development Framework",
            "Manufacturing Efficiency Framework",
            "Hardware Sales Framework",
        ],
    }

    return frameworks.get(industry, ["Generic Business Framework"])


def determine_delivery_mechanism(startup_description, business_model):
    """Determine primary delivery mechanism."""
    text = f"{startup_description} {business_model}".lower()

    if any(term in text for term in ["cloud", "saas", "online", "digital", "software"]):
        return "digital"
    elif any(
        term in text
        for term in ["physical", "product", "hardware", "device", "manufacturing"]
    ):
        return "physical"
    elif any(
        term in text for term in ["service", "consulting", "professional", "human"]
    ):
        return "service"
    else:
        return "hybrid"


def generate_supporting_evidence(taxonomy_results, business_analysis):
    """Generate list of supporting evidence for classification."""
    evidence = []

    if taxonomy_results.get("industry_scores"):
        top_industries = sorted(
            taxonomy_results["industry_scores"].items(),
            key=lambda x: x[1],
            reverse=True,
        )[:2]
        evidence.extend(
            [
                f"{industry} indicators present"
                for industry, score in top_industries
                if score > 0.3
            ]
        )

    if business_analysis.get("scalability_analysis"):
        scalability_factors = [
            factor
            for factor, data in business_analysis["scalability_analysis"].items()
            if data["presence"]
        ]
        evidence.extend(
            [
                f"{factor.replace('_', ' ')} identified"
                for factor in scalability_factors[:2]
            ]
        )

    return evidence


def identify_uncertainty_factors(confidence_factors):
    """Identify factors contributing to classification uncertainty."""
    uncertainty = []

    if confidence_factors["taxonomy_strength"] < 0.5:
        uncertainty.append("Weak industry keyword matching")

    if confidence_factors["business_model_clarity"] < 0.5:
        uncertainty.append("Unclear business model description")

    if confidence_factors["scalability_indicators"] < 0.3:
        uncertainty.append("Limited scalability indicators")

    return uncertainty


def suggest_additional_info(overall_confidence, confidence_factors):
    """Suggest additional information needed for better classification."""
    suggestions = []

    if overall_confidence < 0.7:
        if confidence_factors["taxonomy_strength"] < 0.5:
            suggestions.append("More detailed business description")

        if confidence_factors["business_model_clarity"] < 0.5:
            suggestions.append("Clearer revenue model explanation")

        if confidence_factors["kpi_alignment"] == 0.0:
            suggestions.append("Current KPI data for validation")

    return suggestions


def industry_classification_after_callback(
    callback_context: CallbackContext, llm_response: LlmResponse | None = None, **kwargs
):
    """After callback for industry classifier agent to save LLM response and state."""
    try:
        if llm_response and llm_response.content and llm_response.content.parts:
            save_llm_response_to_file(
                filename="ic_llm",
                llm_content=llm_response.content,
                session_path=get_session_dir(callback_context),
                file_type="json",
            )
    except Exception as e:
        logger.error(
            f"❌ Error saving LLM response in industry_classification_after_callback: {e}"
        )

    try:
        if callback_context.state:
            save_state_to_file(
                context=callback_context,
                session_path=get_session_dir(callback_context),
                filename="ic_state",
                file_type="json",
            )
    except Exception as e:
        logger.error(
            f"❌ Error saving state in industry_classification_after_callback: {e}"
        )


def industry_classification_validation_callback(callback_context, **kwargs):
    """Callback to validate industry classification completeness."""
    logger.info(
        "\n🤖 Industry classification completed - validating classification results\n"
    )
    # Extract classification results if needed for validation
    pass


def industry_classification_setup_callback(callback_context, **kwargs):
    """Setup callback for industry classifier agent."""
    logger.info(
        "\n🤖: industry_classifier_agent: Starting industry classification analysis\n"
    )


industry_classifier_agent = Agent(
    model=MODEL,
    name="industry_classifier_agent",
    description="Classifies startups into appropriate industry sectors for KPI framework selection",
    instruction=prompt.INDUSTRY_CLASSIFIER_INSTRUCTION,
    tools=[
        industry_taxonomy_matching_tool,
        business_model_analysis_tool,
        industry_classification_algorithm,
    ],
    before_agent_callback=industry_classification_setup_callback,
    after_model_callback=industry_classification_validation_callback,
    after_agent_callback=industry_classification_after_callback,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.TEMPERATURE,
    ),
    include_contents="default",
)

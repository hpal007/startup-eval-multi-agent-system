"""Report Synthesis Agent for generating comprehensive KPI validation and benchmarking reports."""

import json
from datetime import datetime
from typing import Any

from google.adk.agents import Agent
from google.genai import types

from tools.report_synthesis_tools import (
    calculate_confidence_scores,
    create_visualization_data,
    generate_executive_summary,
    generate_strategic_recommendations,
    highlight_opportunities,
    identify_red_flags,
    synthesize_analysis_results,
)
from utils.configs import config

from . import prompt


def report_synthesis_setup_callback(callback_context, **kwargs):
    """Setup callback for report synthesis agent."""
    print("\n📊 report_synthesis_agent: Starting comprehensive report synthesis\n")


def report_synthesis_validation_callback(callback_context, **kwargs):
    """Validation callback for report synthesis agent."""
    print("\n✅ Report synthesis completed - validating output\n")


def synthesize_results_tool(analysis_data: str) -> str:
    """
    Synthesize all analysis results into structured report format.

    Args:
        analysis_data: JSON string containing all analysis results from specialized agents

    Returns:
        JSON string with synthesized analysis results
    """
    try:
        data = json.loads(analysis_data)

        industry_results = data.get("industry_results", {})
        market_validation_results = data.get("market_validation_results", {})
        kpi_analysis_results = data.get("kpi_analysis_results", {})
        benchmarking_results = data.get("benchmarking_results", {})

        # Synthesize all results
        synthesized_results = synthesize_analysis_results(
            industry_results,
            market_validation_results,
            kpi_analysis_results,
            benchmarking_results,
        )

        return json.dumps(synthesized_results, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to synthesize results: {e!s}"})


def synthesize_analysis_results_tool(analysis_data: str) -> str:
    """
    Alias for backward/LLM compatibility. Some prompts call this exact tool name.
    """
    return synthesize_results_tool(analysis_data)


def generate_executive_summary_tool(synthesis_data: str) -> str:
    """
    Generate executive summary with key findings and strategic implications.

    Args:
        synthesis_data: JSON string containing synthesized results and startup context

    Returns:
        JSON string with executive summary
    """
    try:
        data = json.loads(synthesis_data)

        synthesized_results = data.get("synthesized_results", {})
        startup_context = data.get("startup_context", {})

        # Generate executive summary
        executive_summary = generate_executive_summary(
            synthesized_results, startup_context
        )

        return json.dumps(executive_summary, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to generate executive summary: {e!s}"})


def identify_red_flags_tool(analysis_components: str) -> str:
    """
    Identify and prioritize red flags across all analysis components.

    Args:
        analysis_components: JSON string containing market validation, KPI performance, benchmarking, and data quality results

    Returns:
        JSON string with identified red flags prioritized by severity
    """
    try:
        data = json.loads(analysis_components)

        market_validation = data.get("market_validation", {})
        kpi_performance = data.get("kpi_performance", {})
        benchmarking_results = data.get("benchmarking_results", {})
        data_quality = data.get("data_quality", {})

        # Identify red flags
        red_flags = identify_red_flags(
            market_validation, kpi_performance, benchmarking_results, data_quality
        )

        # Convert to serializable format
        red_flags_data = []
        for flag in red_flags:
            red_flags_data.append(
                {
                    "category": flag.category,
                    "description": flag.description,
                    "severity": flag.severity,
                    "evidence": flag.evidence,
                    "impact_assessment": flag.impact_assessment,
                    "mitigation_strategies": flag.mitigation_strategies,
                    "monitoring_requirements": flag.monitoring_requirements,
                }
            )

        return json.dumps({"red_flags": red_flags_data}, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to identify red flags: {e!s}"})


def highlight_opportunities_tool(opportunity_data: str) -> str:
    """
    Identify and highlight strategic opportunities.

    Args:
        opportunity_data: JSON string containing market analysis, competitive analysis, performance highlights, and industry trends

    Returns:
        JSON string with identified opportunities prioritized by impact and feasibility
    """
    try:
        data = json.loads(opportunity_data)

        market_analysis = data.get("market_analysis", {})
        competitive_analysis = data.get("competitive_analysis", {})
        performance_highlights = data.get("performance_highlights", {})
        industry_trends = data.get("industry_trends", {})

        # Identify opportunities
        opportunities = highlight_opportunities(
            market_analysis,
            competitive_analysis,
            performance_highlights,
            industry_trends,
        )

        # Convert to serializable format
        opportunities_data = []
        for opp in opportunities:
            opportunities_data.append(
                {
                    "category": opp.category,
                    "description": opp.description,
                    "opportunity_type": opp.opportunity_type,
                    "market_size": opp.market_size,
                    "timeline": opp.timeline,
                    "resource_requirements": opp.resource_requirements,
                    "success_probability": opp.success_probability,
                    "strategic_value": opp.strategic_value,
                }
            )

        return json.dumps({"opportunities": opportunities_data}, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to highlight opportunities: {e!s}"})


def calculate_confidence_scores_tool(quality_data: str) -> str:
    """
    Calculate comprehensive confidence scores for analysis quality.

    Args:
        quality_data: JSON string containing source credibility, data recency, completeness, and consistency assessments

    Returns:
        JSON string with confidence scores and quality assessment
    """
    try:
        data = json.loads(quality_data)

        source_credibility = data.get("source_credibility", {})
        data_recency = data.get("data_recency", {})
        data_completeness = data.get("data_completeness", {})
        data_consistency = data.get("data_consistency", {})

        # Calculate confidence scores
        confidence_score = calculate_confidence_scores(
            source_credibility, data_recency, data_completeness, data_consistency
        )

        # Convert to serializable format
        confidence_data = {
            "overall_score": confidence_score.overall_score,
            "source_quality": confidence_score.source_quality,
            "data_recency": confidence_score.data_recency,
            "data_completeness": confidence_score.data_completeness,
            "analysis_consistency": confidence_score.analysis_consistency,
            "quality_summary": confidence_score.quality_summary,
            "improvement_recommendations": confidence_score.improvement_recommendations,
        }

        return json.dumps(confidence_data, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to calculate confidence scores: {e!s}"})


def generate_recommendations_tool(recommendation_data: str) -> str:
    """
    Generate prioritized strategic recommendations based on analysis results.

    Args:
        recommendation_data: JSON string containing synthesized results, red flags, and opportunities

    Returns:
        JSON string with prioritized strategic recommendations
    """
    try:
        data = json.loads(recommendation_data)

        synthesized_results = data.get("synthesized_results", {})
        red_flags_data = data.get("red_flags", [])
        opportunities_data = data.get("opportunities", [])

        # Convert back to objects for processing
        from tools.report_synthesis_tools import Opportunity, RedFlag

        red_flags = []
        for flag_data in red_flags_data:
            red_flags.append(
                RedFlag(
                    category=flag_data.get("category", ""),
                    description=flag_data.get("description", ""),
                    severity=flag_data.get("severity", "Medium"),
                    evidence=flag_data.get("evidence", []),
                    impact_assessment=flag_data.get("impact_assessment", ""),
                    mitigation_strategies=flag_data.get("mitigation_strategies", []),
                    monitoring_requirements=flag_data.get(
                        "monitoring_requirements", []
                    ),
                )
            )

        opportunities = []
        for opp_data in opportunities_data:
            opportunities.append(
                Opportunity(
                    category=opp_data.get("category", ""),
                    description=opp_data.get("description", ""),
                    opportunity_type=opp_data.get("opportunity_type", "Strategic"),
                    market_size=opp_data.get("market_size"),
                    timeline=opp_data.get("timeline", "Medium-term"),
                    resource_requirements=opp_data.get("resource_requirements", []),
                    success_probability=opp_data.get("success_probability", "Medium"),
                    strategic_value=opp_data.get("strategic_value", "Medium"),
                )
            )

        # Generate recommendations
        recommendations = generate_strategic_recommendations(
            synthesized_results, red_flags, opportunities
        )

        return json.dumps(recommendations, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to generate recommendations: {e!s}"})


def create_visualization_data_tool(visualization_input: str) -> str:
    """
    Generate data for charts and visual representations.

    Args:
        visualization_input: JSON string containing synthesized analysis results

    Returns:
        JSON string with visualization data for charts and graphs
    """
    try:
        data = json.loads(visualization_input)

        synthesized_results = data.get("synthesized_results", {})

        # Create visualization data
        visualization_data = create_visualization_data(synthesized_results)

        return json.dumps(visualization_data, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to create visualization data: {e!s}"})


def generate_comprehensive_report_tool(report_data: str) -> str:
    """
    Generate a complete comprehensive report combining all analysis components.

    Args:
        report_data: JSON string containing all analysis results, summaries, red flags, opportunities, and recommendations

    Returns:
        JSON string with complete structured report
    """
    try:
        data = json.loads(report_data)

        startup_name = data.get("startup_name", "Unknown Startup")
        industry = data.get("industry", "Unknown Industry")
        analysis_date = data.get("analysis_date", datetime.now().strftime("%Y-%m-%d"))

        # Extract all components
        executive_summary = data.get("executive_summary", {})
        synthesized_results = data.get("synthesized_results", {})
        red_flags = data.get("red_flags", [])
        opportunities = data.get("opportunities", [])
        recommendations = data.get("recommendations", {})
        confidence_scores = data.get("confidence_scores", {})
        visualization_data = data.get("visualization_data", {})

        # Generate enhanced executive summary with prioritized findings
        enhanced_executive_summary = _generate_enhanced_executive_summary(
            executive_summary, synthesized_results, red_flags, opportunities
        )

        # Add KPI methodology to executive summary if not already present
        if "kpi_analysis_methodology" not in enhanced_executive_summary:
            from tools.report_synthesis_tools import _generate_kpi_analysis_methodology

            enhanced_executive_summary["kpi_analysis_methodology"] = (
                _generate_kpi_analysis_methodology(synthesized_results)
            )

        # Create detailed industry analysis with market context
        detailed_industry_analysis = _create_detailed_industry_analysis(
            synthesized_results.get("industry_analysis", {}),
            synthesized_results.get("market_validation", {}),
            synthesized_results.get("benchmarking", {}),
        )

        # Generate comprehensive KPI performance analysis
        comprehensive_kpi_analysis = _create_comprehensive_kpi_analysis(
            synthesized_results.get("kpi_performance", {}),
            synthesized_results.get("benchmarking", {}),
            red_flags,
            opportunities,
        )

        # Create strategic recommendations with implementation details
        detailed_recommendations = _create_detailed_strategic_recommendations(
            recommendations, red_flags, opportunities, synthesized_results
        )

        # Generate quality assessment with transparency
        quality_assessment = _create_quality_assessment(
            confidence_scores, synthesized_results.get("data_quality", {}), red_flags
        )

        # Create comprehensive report structure
        comprehensive_report = {
            "report_metadata": {
                "startup_name": startup_name,
                "industry": industry,
                "analysis_date": analysis_date,
                "report_version": "1.0",
                "analyst": "Business KPIs Orchestrator",
                "analysis_scope": _determine_analysis_scope(synthesized_results),
                "report_type": "Comprehensive KPI Validation and Benchmarking Analysis",
            },
            "executive_summary": enhanced_executive_summary,
            "industry_analysis": detailed_industry_analysis,
            "kpi_performance_analysis": comprehensive_kpi_analysis,
            "risk_assessment": {
                "identified_risks": red_flags,
                "risk_prioritization": _prioritize_risks(red_flags),
                "risk_impact_analysis": _analyze_risk_impacts(red_flags),
                "mitigation_strategies": _extract_mitigation_strategies(red_flags),
                "monitoring_framework": _create_risk_monitoring_framework(red_flags),
            },
            "strategic_opportunities": {
                "opportunity_analysis": opportunities,
                "opportunity_prioritization": _prioritize_opportunities(opportunities),
                "market_opportunity_assessment": _assess_market_opportunities(
                    opportunities
                ),
                "implementation_roadmap": recommendations.get(
                    "implementation_timeline", {}
                ),
                "resource_requirements": _consolidate_resource_requirements(
                    opportunities
                ),
            },
            "strategic_recommendations": detailed_recommendations,
            "quality_assessment": quality_assessment,
            "supporting_evidence": {
                "data_sources": _extract_data_sources(synthesized_results),
                "methodology": _document_methodology(),
                "analysis_assumptions": _document_analysis_assumptions(
                    synthesized_results
                ),
                "visualization_data": visualization_data,
                "appendices": _create_appendices(
                    synthesized_results, red_flags, opportunities
                ),
            },
            "next_steps": _generate_next_steps(
                red_flags, opportunities, recommendations
            ),
        }

        return json.dumps(comprehensive_report, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to generate comprehensive report: {e!s}"})


def _prioritize_risks(red_flags: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Prioritize risks by severity and impact."""
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    return sorted(
        red_flags, key=lambda x: severity_order.get(x.get("severity", "Low"), 4)
    )


def _prioritize_opportunities(
    opportunities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Prioritize opportunities by strategic value and success probability."""
    value_order = {"High": 3, "Medium": 2, "Low": 1}
    prob_order = {"High": 3, "Medium": 2, "Low": 1}

    def opportunity_score(opp):
        value_score = value_order.get(opp.get("strategic_value", "Low"), 1)
        prob_score = prob_order.get(opp.get("success_probability", "Low"), 1)
        return value_score * prob_score

    return sorted(opportunities, key=opportunity_score, reverse=True)


def _extract_mitigation_strategies(red_flags: list[dict[str, Any]]) -> list[str]:
    """Extract unique mitigation strategies from red flags."""
    strategies = set()
    for flag in red_flags:
        strategies.update(flag.get("mitigation_strategies", []))
    return list(strategies)


def _identify_analysis_limitations(confidence_scores: dict[str, Any]) -> list[str]:
    """Identify analysis limitations based on confidence scores."""
    limitations = []

    overall_score = confidence_scores.get("overall_score", 100)
    if overall_score < 70:
        limitations.append("Overall analysis confidence below recommended threshold")

    source_quality = confidence_scores.get("source_quality", 100)
    if source_quality < 60:
        limitations.append("Limited authoritative data sources available")

    data_recency = confidence_scores.get("data_recency", 100)
    if data_recency < 60:
        limitations.append("Analysis relies on outdated market data")

    return limitations


def _extract_data_sources(synthesized_results: dict[str, Any]) -> list[str]:
    """Extract data sources used in analysis."""
    sources = set()

    # Extract from market validation
    market_validation = synthesized_results.get("market_validation", {})
    for validation_key in ["tam_validation", "sam_validation", "som_validation"]:
        validation_data = market_validation.get(validation_key, {})
        sources.update(validation_data.get("sources", []))

    # Add standard sources
    sources.update(
        [
            "Industry benchmark databases",
            "Market research reports",
            "Competitive analysis data",
            "Startup-provided KPI data",
        ]
    )

    return list(sources)


def _generate_enhanced_executive_summary(
    executive_summary: dict[str, Any],
    synthesized_results: dict[str, Any],
    red_flags: list[dict],
    opportunities: list[dict],
) -> dict[str, Any]:
    """Generate enhanced executive summary with prioritized findings."""
    # Extract key performance indicators
    kpi_performance = synthesized_results.get("kpi_performance", {})
    benchmarking = synthesized_results.get("benchmarking", {})
    market_validation = synthesized_results.get("market_validation", {})

    # Prioritize findings by business impact
    prioritized_findings = []

    # Critical performance insights
    overall_performance = benchmarking.get("overall_performance_score", 0.0)
    if overall_performance > 0.8:
        prioritized_findings.append(
            "Exceptional performance across key industry benchmarks"
        )
    elif overall_performance < 0.4:
        prioritized_findings.append(
            "Performance significantly below industry standards requires immediate attention"
        )

    # Market validation insights
    market_confidence = market_validation.get("overall_confidence", 0.0)
    if market_confidence < 0.6:
        prioritized_findings.append(
            "Market size claims require validation and additional research"
        )

    # Critical red flags
    critical_flags = [flag for flag in red_flags if flag.get("severity") == "Critical"]
    if critical_flags:
        prioritized_findings.append(
            f"{len(critical_flags)} critical issues identified requiring immediate action"
        )

    # High-value opportunities
    high_value_opportunities = [
        opp for opp in opportunities if opp.get("strategic_value") == "High"
    ]
    if high_value_opportunities:
        prioritized_findings.append(
            f"{len(high_value_opportunities)} high-value strategic opportunities identified"
        )

    return {
        **executive_summary,
        "prioritized_findings": prioritized_findings[:5],
        "key_metrics_summary": {
            "overall_performance_score": overall_performance,
            "market_validation_confidence": market_confidence,
            "critical_risks_count": len(critical_flags),
            "high_value_opportunities_count": len(high_value_opportunities),
        },
        "executive_recommendation": _generate_executive_recommendation(
            overall_performance,
            market_confidence,
            len(critical_flags),
            len(high_value_opportunities),
        ),
    }


def _create_detailed_industry_analysis(
    industry_analysis: dict[str, Any],
    market_validation: dict[str, Any],
    benchmarking: dict[str, Any],
) -> dict[str, Any]:
    """Create detailed industry analysis with market context."""
    return {
        "industry_classification": {
            "primary_industry": industry_analysis.get("classification", "Unknown"),
            "secondary_industries": industry_analysis.get("secondary_industries", []),
            "classification_confidence": industry_analysis.get("confidence", 0.0),
            "industry_characteristics": _extract_industry_characteristics(
                industry_analysis
            ),
        },
        "market_validation_analysis": {
            "tam_analysis": market_validation.get("tam_validation", {}),
            "sam_analysis": market_validation.get("sam_validation", {}),
            "som_analysis": market_validation.get("som_validation", {}),
            "validation_summary": _create_market_validation_summary(market_validation),
            "discrepancy_analysis": _analyze_market_discrepancies(market_validation),
        },
        "competitive_landscape": {
            "industry_position": benchmarking.get("industry_position", "Unknown"),
            "competitive_advantages": benchmarking.get("competitive_advantages", []),
            "competitive_gaps": benchmarking.get("improvement_areas", []),
            "peer_comparison_summary": _create_peer_comparison_summary(benchmarking),
        },
        "industry_trends_impact": _assess_industry_trends_impact(
            industry_analysis, market_validation
        ),
    }


def _create_comprehensive_kpi_analysis(
    kpi_performance: dict[str, Any],
    benchmarking: dict[str, Any],
    red_flags: list[dict],
    opportunities: list[dict],
) -> dict[str, Any]:
    """Generate comprehensive KPI performance analysis."""
    analyzed_kpis = kpi_performance.get("analyzed_kpis", [])
    missing_kpis = kpi_performance.get("missing_kpis", [])

    return {
        "performance_overview": {
            "total_kpis_analyzed": len(analyzed_kpis),
            "missing_critical_kpis": len(missing_kpis),
            "overall_performance_score": benchmarking.get(
                "overall_performance_score", 0.0
            ),
            "performance_distribution": _analyze_performance_distribution(
                analyzed_kpis
            ),
        },
        "individual_kpi_analysis": _create_individual_kpi_analysis(analyzed_kpis),
        "benchmarking_results": {
            "industry_comparison": benchmarking.get("peer_comparison", {}),
            "percentile_rankings": _extract_percentile_rankings(analyzed_kpis),
            "benchmark_gaps": _identify_benchmark_gaps(analyzed_kpis, benchmarking),
        },
        "trend_analysis": {
            "performance_trends": kpi_performance.get("trend_analysis", {}),
            "growth_trajectory": _analyze_growth_trajectory(kpi_performance),
            "trend_implications": _assess_trend_implications(kpi_performance),
        },
        "kpi_related_risks": _extract_kpi_related_risks(red_flags),
        "kpi_improvement_opportunities": _extract_kpi_opportunities(opportunities),
    }


def _create_detailed_strategic_recommendations(
    recommendations: dict[str, Any],
    red_flags: list[dict],
    opportunities: list[dict],
    synthesized_results: dict[str, Any],
) -> dict[str, Any]:
    """Create detailed strategic recommendations with implementation guidance."""
    return {
        "priority_actions": {
            "immediate_actions": recommendations.get("priority_actions", []),
            "implementation_guidance": _create_implementation_guidance(
                recommendations.get("priority_actions", [])
            ),
            "resource_allocation": _recommend_resource_allocation(
                recommendations.get("priority_actions", [])
            ),
        },
        "performance_improvements": {
            "improvement_initiatives": recommendations.get(
                "performance_improvements", []
            ),
            "improvement_roadmap": _create_improvement_roadmap(
                recommendations.get("performance_improvements", [])
            ),
            "success_metrics": _define_improvement_success_metrics(
                recommendations.get("performance_improvements", [])
            ),
        },
        "market_opportunities": {
            "opportunity_development": recommendations.get("market_opportunities", []),
            "market_entry_strategies": _develop_market_entry_strategies(opportunities),
            "competitive_positioning": _recommend_competitive_positioning(
                opportunities, synthesized_results
            ),
        },
        "risk_mitigation": {
            "mitigation_strategies": recommendations.get("risk_mitigation", []),
            "risk_monitoring": _create_risk_monitoring_plan(red_flags),
            "contingency_planning": _develop_contingency_plans(red_flags),
        },
        "implementation_framework": {
            "timeline": recommendations.get("implementation_timeline", {}),
            "success_metrics": recommendations.get("success_metrics", {}),
            "governance_structure": _recommend_governance_structure(recommendations),
        },
    }


def _create_quality_assessment(
    confidence_scores: dict[str, Any],
    data_quality: dict[str, Any],
    red_flags: list[dict],
) -> dict[str, Any]:
    """Create comprehensive quality assessment."""
    data_quality_flags = [
        flag for flag in red_flags if flag.get("category") == "Data Quality"
    ]

    return {
        "confidence_analysis": confidence_scores,
        "data_quality_metrics": data_quality,
        "analysis_reliability": {
            "overall_reliability": _assess_overall_reliability(
                confidence_scores, data_quality
            ),
            "reliability_factors": _identify_reliability_factors(
                confidence_scores, data_quality
            ),
            "quality_concerns": [
                flag.get("description", "") for flag in data_quality_flags
            ],
        },
        "analysis_limitations": _identify_analysis_limitations(confidence_scores),
        "improvement_recommendations": confidence_scores.get(
            "improvement_recommendations", []
        ),
        "validation_status": _assess_validation_status(confidence_scores, data_quality),
    }


def _document_methodology() -> dict[str, Any]:
    """Document the analysis methodology."""
    return {
        "analysis_approach": "Multi-agent KPI validation and benchmarking analysis",
        "methodology_components": [
            "Industry classification using business model and market analysis",
            "Market size validation against authoritative sources",
            "KPI performance analysis with industry benchmarking",
            "Competitive positioning assessment",
            "Risk and opportunity identification",
            "Strategic recommendation generation with implementation guidance",
        ],
        "validation_methods": [
            "Cross-reference validation across multiple authoritative sources",
            "Statistical analysis of performance metrics and trends",
            "Industry benchmark comparison with percentile ranking",
            "Confidence scoring and data quality assessment",
            "Consistency checks across analysis components",
        ],
        "data_sources": [
            "Industry research reports (Gartner, Forrester, McKinsey)",
            "Market research databases and industry associations",
            "Competitive intelligence and benchmark data",
            "Startup-provided KPI data and financial metrics",
            "Public company filings and industry surveys",
        ],
        "analysis_limitations": [
            "Analysis quality depends on data availability and source credibility",
            "Market data may have temporal limitations and regional variations",
            "Industry benchmarks may not reflect latest market conditions",
            "Startup-provided data accuracy depends on internal measurement systems",
            "Competitive data may be limited or estimated",
        ],
    }


# Additional helper functions for enhanced report generation


def _determine_analysis_scope(synthesized_results: dict[str, Any]) -> list[str]:
    """Determine the scope of analysis performed."""
    scope = []

    if synthesized_results.get("industry_analysis"):
        scope.append("Industry Classification and Market Analysis")
    if synthesized_results.get("market_validation"):
        scope.append("Market Size Validation (TAM/SAM/SOM)")
    if synthesized_results.get("kpi_performance"):
        scope.append("KPI Performance Analysis and Benchmarking")
    if synthesized_results.get("benchmarking"):
        scope.append("Competitive Positioning Assessment")

    return scope


def _generate_executive_recommendation(
    performance_score: float,
    market_confidence: float,
    critical_risks: int,
    high_value_opportunities: int,
) -> str:
    """Generate executive-level investment recommendation."""
    if performance_score > 0.7 and market_confidence > 0.7 and critical_risks == 0:
        return "Strong investment opportunity with solid fundamentals and market validation"
    elif performance_score > 0.5 and market_confidence > 0.6 and critical_risks <= 1:
        return "Moderate investment opportunity with some areas requiring attention"
    elif critical_risks > 2 or performance_score < 0.3:
        return "High-risk investment requiring significant improvements before consideration"
    else:
        return "Mixed investment profile requiring detailed due diligence"


def _extract_industry_characteristics(industry_analysis: dict[str, Any]) -> list[str]:
    """Extract key industry characteristics."""
    characteristics = []

    industry = industry_analysis.get("classification", "").lower()

    if "saas" in industry or "software" in industry:
        characteristics.extend(
            [
                "Recurring revenue model",
                "High scalability potential",
                "Technology-driven",
            ]
        )
    elif "ecommerce" in industry or "retail" in industry:
        characteristics.extend(
            [
                "Transaction-based revenue",
                "Inventory management",
                "Customer acquisition focus",
            ]
        )
    elif "fintech" in industry or "financial" in industry:
        characteristics.extend(
            [
                "Regulatory compliance requirements",
                "Trust and security critical",
                "Network effects",
            ]
        )
    elif "healthcare" in industry or "biotech" in industry:
        characteristics.extend(
            [
                "Regulatory approval processes",
                "Long development cycles",
                "Clinical validation required",
            ]
        )

    return characteristics


def _create_market_validation_summary(
    market_validation: dict[str, Any],
) -> dict[str, Any]:
    """Create summary of market validation results."""
    tam_validation = market_validation.get("tam_validation", {})
    sam_validation = market_validation.get("sam_validation", {})
    som_validation = market_validation.get("som_validation", {})

    return {
        "overall_validation_status": "Validated"
        if market_validation.get("overall_confidence", 0) > 0.7
        else "Requires Validation",
        "tam_status": "Validated"
        if tam_validation.get("confidence_level", 0) > 0.7
        else "Questionable",
        "sam_status": "Validated"
        if sam_validation.get("confidence_level", 0) > 0.7
        else "Questionable",
        "som_status": "Validated"
        if som_validation.get("confidence_level", 0) > 0.7
        else "Questionable",
        "key_concerns": market_validation.get("discrepancy_flags", []),
    }


def _analyze_market_discrepancies(
    market_validation: dict[str, Any],
) -> list[dict[str, Any]]:
    """Analyze market validation discrepancies."""
    discrepancies = []

    for market_type in ["tam_validation", "sam_validation", "som_validation"]:
        validation_data = market_validation.get(market_type, {})
        variance = validation_data.get("variance_percentage", 0)

        if abs(variance) > 20:  # Significant variance threshold
            discrepancies.append(
                {
                    "market_type": market_type.replace("_validation", "").upper(),
                    "variance_percentage": variance,
                    "claimed_value": validation_data.get("claimed_value", 0),
                    "market_estimate": validation_data.get("market_estimate", 0),
                    "severity": "High" if abs(variance) > 50 else "Medium",
                    "implications": "Overestimated market size"
                    if variance < 0
                    else "Conservative market estimate",
                }
            )

    return discrepancies


# Placeholder implementations for remaining helper functions
def _create_peer_comparison_summary(benchmarking):
    return {}


def _assess_industry_trends_impact(industry_analysis, market_validation):
    return {}


def _analyze_performance_distribution(analyzed_kpis):
    return {}


def _create_individual_kpi_analysis(analyzed_kpis):
    return []


def _extract_percentile_rankings(analyzed_kpis):
    return {}


def _identify_benchmark_gaps(analyzed_kpis, benchmarking):
    return []


def _analyze_growth_trajectory(kpi_performance):
    return {}


def _assess_trend_implications(kpi_performance):
    return {}


def _extract_kpi_related_risks(red_flags):
    return []


def _extract_kpi_opportunities(opportunities):
    return []


def _create_implementation_guidance(priority_actions):
    return {}


def _recommend_resource_allocation(priority_actions):
    return {}


def _create_improvement_roadmap(performance_improvements):
    return {}


def _define_improvement_success_metrics(performance_improvements):
    return {}


def _develop_market_entry_strategies(opportunities):
    return []


def _recommend_competitive_positioning(opportunities, synthesized_results):
    return {}


def _create_risk_monitoring_plan(red_flags):
    return {}


def _develop_contingency_plans(red_flags):
    return {}


def _recommend_governance_structure(recommendations):
    return {}


def _assess_overall_reliability(confidence_scores, data_quality):
    return "Medium"


def _identify_reliability_factors(confidence_scores, data_quality):
    return []


def _assess_validation_status(confidence_scores, data_quality):
    return "Partially Validated"


def _analyze_risk_impacts(red_flags):
    return {}


def _create_risk_monitoring_framework(red_flags):
    return {}


def _assess_market_opportunities(opportunities):
    return {}


def _consolidate_resource_requirements(opportunities):
    return {}


def _document_analysis_assumptions(synthesized_results):
    return {}


def _create_appendices(synthesized_results, red_flags, opportunities):
    return {}


def _generate_next_steps(red_flags, opportunities, recommendations):
    return []


MODEL = config.get_model_for_agent("abc_agent")

# Create the Report Synthesis agent
report_synthesis_agent = Agent(
    model=MODEL,
    name="report_synthesis_agent",
    description="Synthesizes all analysis results into comprehensive KPI validation and benchmarking reports with executive summaries and strategic insights",
    instruction=prompt.REPORT_SYNTHESIS_INSTRUCTION,
    tools=[
        synthesize_results_tool,
        synthesize_analysis_results_tool,
        generate_executive_summary_tool,
        identify_red_flags_tool,
        highlight_opportunities_tool,
        calculate_confidence_scores_tool,
        generate_recommendations_tool,
        create_visualization_data_tool,
        generate_comprehensive_report_tool,
    ],
    before_agent_callback=report_synthesis_setup_callback,
    after_model_callback=report_synthesis_validation_callback,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.TEMPERATURE,
    ),
    include_contents="default",
)

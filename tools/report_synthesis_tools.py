"""Tools for report synthesis and comprehensive report generation."""

import statistics
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ConfidenceScore:
    """Confidence score with breakdown by component."""

    overall_score: float
    source_quality: float
    data_recency: float
    data_completeness: float
    analysis_consistency: float
    quality_summary: str
    improvement_recommendations: list[str]


@dataclass
class RedFlag:
    """Red flag identification with severity and mitigation."""

    category: str
    description: str
    severity: str  # Critical/High/Medium/Low
    evidence: list[str]
    impact_assessment: str
    mitigation_strategies: list[str]
    monitoring_requirements: list[str]


@dataclass
class Opportunity:
    """Strategic opportunity with implementation details."""

    category: str
    description: str
    opportunity_type: str  # Market/Competitive/Operational/Strategic
    market_size: str | None
    timeline: str  # Short/Medium/Long-term
    resource_requirements: list[str]
    success_probability: str  # High/Medium/Low
    strategic_value: str


def synthesize_analysis_results(
    industry_results: dict[str, Any],
    market_validation_results: dict[str, Any],
    kpi_analysis_results: dict[str, Any],
    benchmarking_results: dict[str, Any],
) -> dict[str, Any]:
    """
    Synthesize all analysis results into a structured report format.

    Args:
        industry_results: Industry classification and analysis results
        market_validation_results: Market size validation results
        kpi_analysis_results: KPI performance analysis results
        benchmarking_results: Industry benchmarking results

    Returns:
        Dictionary containing synthesized analysis results
    """
    try:
        # Extract key information from each analysis component
        industry_classification = industry_results.get("primary_industry", "Unknown")
        confidence_score = industry_results.get("confidence_score", 0.0)

        # Market validation synthesis
        market_validation_summary = {
            "tam_validation": market_validation_results.get("tam_validation", {}),
            "sam_validation": market_validation_results.get("sam_validation", {}),
            "som_validation": market_validation_results.get("som_validation", {}),
            "overall_confidence": market_validation_results.get(
                "overall_confidence", 0.0
            ),
            "discrepancy_flags": market_validation_results.get("discrepancy_flags", []),
        }

        # KPI analysis synthesis
        kpi_summary = {
            "analyzed_kpis": kpi_analysis_results.get("analyzed_kpis", []),
            "missing_kpis": kpi_analysis_results.get("missing_kpis", []),
            "performance_summary": kpi_analysis_results.get("performance_summary", {}),
            "trend_analysis": kpi_analysis_results.get("trend_analysis", {}),
        }

        # Benchmarking synthesis
        benchmarking_summary = {
            "overall_performance_score": benchmarking_results.get(
                "overall_performance_score", 0.0
            ),
            "peer_comparison": benchmarking_results.get("peer_comparison", {}),
            "industry_position": benchmarking_results.get(
                "industry_position", "Unknown"
            ),
            "competitive_advantages": benchmarking_results.get(
                "competitive_advantages", []
            ),
            "improvement_areas": benchmarking_results.get("improvement_areas", []),
        }

        # Create synthesized results
        synthesized_results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "industry_analysis": {
                "classification": industry_classification,
                "confidence": confidence_score,
                "secondary_industries": industry_results.get(
                    "secondary_industries", []
                ),
            },
            "market_validation": market_validation_summary,
            "kpi_performance": kpi_summary,
            "benchmarking": benchmarking_summary,
            "data_quality": {
                "completeness_score": _calculate_data_completeness(
                    industry_results,
                    market_validation_results,
                    kpi_analysis_results,
                    benchmarking_results,
                ),
                "consistency_score": _calculate_data_consistency(
                    market_validation_results,
                    kpi_analysis_results,
                    benchmarking_results,
                ),
            },
        }

        return synthesized_results

    except Exception as e:
        return {
            "error": f"Failed to synthesize analysis results: {e!s}",
            "analysis_timestamp": datetime.now().isoformat(),
        }


def generate_executive_summary(
    synthesized_results: dict[str, Any], startup_context: dict[str, Any]
) -> dict[str, Any]:
    """
    Generate executive summary with key findings and strategic implications.

    Args:
        synthesized_results: Synthesized analysis results
        startup_context: Startup context including funding stage, objectives

    Returns:
        Dictionary containing executive summary
    """
    try:
        startup_name = startup_context.get("startup_name", "Unknown Startup")
        industry = synthesized_results.get("industry_analysis", {}).get(
            "classification", "Unknown"
        )

        # Generate investment thesis
        investment_thesis = _generate_investment_thesis(
            synthesized_results, startup_context
        )

        # Extract critical findings
        critical_findings = _extract_critical_findings(synthesized_results)

        # Generate strategic priorities
        strategic_priorities = _generate_strategic_priorities(synthesized_results)

        # Assess risks
        risk_assessment = _assess_executive_risks(synthesized_results)

        # Generate KPI analysis methodology
        kpi_methodology = _generate_kpi_analysis_methodology(synthesized_results)

        executive_summary = {
            "startup_name": startup_name,
            "industry": industry,
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "investment_thesis": investment_thesis,
            "critical_findings": critical_findings,
            "strategic_priorities": strategic_priorities,
            "risk_assessment": risk_assessment,
            "kpi_analysis_methodology": kpi_methodology,
            "overall_confidence": _calculate_overall_confidence(synthesized_results),
        }

        return executive_summary

    except Exception as e:
        return {
            "error": f"Failed to generate executive summary: {e!s}",
            "startup_name": startup_context.get("startup_name", "Unknown"),
        }


def identify_red_flags(
    market_validation: dict[str, Any],
    kpi_performance: dict[str, Any],
    benchmarking_results: dict[str, Any],
    data_quality: dict[str, Any],
) -> list[RedFlag]:
    """
    Identify and prioritize red flags across all analysis components.

    Args:
        market_validation: Market validation results
        kpi_performance: KPI performance results
        benchmarking_results: Benchmarking results
        data_quality: Data quality assessment

    Returns:
        List of RedFlag objects prioritized by severity
    """
    red_flags = []

    try:
        # Market validation red flags
        red_flags.extend(_identify_market_validation_red_flags(market_validation))

        # KPI performance red flags
        red_flags.extend(_identify_kpi_performance_red_flags(kpi_performance))

        # Benchmarking red flags
        red_flags.extend(_identify_benchmarking_red_flags(benchmarking_results))

        # Data quality red flags
        red_flags.extend(_identify_data_quality_red_flags(data_quality))

        # Sort by severity (Critical > High > Medium > Low)
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        red_flags.sort(key=lambda x: severity_order.get(x.severity, 4))

        return red_flags

    except Exception as e:
        return [
            RedFlag(
                category="Analysis Error",
                description=f"Failed to identify red flags: {e!s}",
                severity="High",
                evidence=[],
                impact_assessment="Analysis reliability compromised",
                mitigation_strategies=[
                    "Review analysis methodology",
                    "Validate data sources",
                ],
                monitoring_requirements=["Monitor analysis quality"],
            )
        ]


def highlight_opportunities(
    market_analysis: dict[str, Any],
    competitive_analysis: dict[str, Any],
    performance_highlights: dict[str, Any],
    industry_trends: dict[str, Any],
) -> list[Opportunity]:
    """
    Identify and highlight strategic opportunities.

    Args:
        market_analysis: Market analysis results
        competitive_analysis: Competitive positioning results
        performance_highlights: Performance strength areas
        industry_trends: Industry trend analysis

    Returns:
        List of Opportunity objects prioritized by impact and feasibility
    """
    opportunities = []

    try:
        # Market opportunities
        opportunities.extend(
            _identify_market_opportunities(market_analysis, industry_trends)
        )

        # Competitive advantages
        opportunities.extend(
            _identify_competitive_opportunities(
                competitive_analysis, performance_highlights
            )
        )

        # Performance optimization opportunities
        opportunities.extend(
            _identify_performance_opportunities(performance_highlights)
        )

        # Strategic initiative opportunities
        opportunities.extend(
            _identify_strategic_opportunities(market_analysis, competitive_analysis)
        )

        # Sort by strategic value and success probability
        opportunities.sort(
            key=lambda x: (
                _get_strategic_value_score(x.strategic_value),
                _get_probability_score(x.success_probability),
            ),
            reverse=True,
        )

        return opportunities

    except Exception as e:
        return [
            Opportunity(
                category="Analysis Error",
                description=f"Failed to identify opportunities: {e!s}",
                opportunity_type="Strategic",
                market_size=None,
                timeline="Unknown",
                resource_requirements=["Review analysis"],
                success_probability="Low",
                strategic_value="Low",
            )
        ]


def calculate_confidence_scores(
    source_credibility: dict[str, Any],
    data_recency: dict[str, Any],
    data_completeness: dict[str, Any],
    data_consistency: dict[str, Any],
) -> ConfidenceScore:
    """
    Calculate comprehensive confidence scores for analysis quality.

    Args:
        source_credibility: Assessment of data source quality
        data_recency: Assessment of data freshness
        data_completeness: Assessment of data completeness
        data_consistency: Assessment of data consistency

    Returns:
        ConfidenceScore object with detailed breakdown
    """
    try:
        # Calculate component scores (0-100)
        source_score = _calculate_source_quality_score(source_credibility)
        recency_score = _calculate_recency_score(data_recency)
        completeness_score = _calculate_completeness_score(data_completeness)
        consistency_score = _calculate_consistency_score(data_consistency)

        # Calculate weighted overall score
        weights = {
            "source": 0.25,
            "recency": 0.20,
            "completeness": 0.25,
            "consistency": 0.30,
        }
        overall_score = (
            source_score * weights["source"]
            + recency_score * weights["recency"]
            + completeness_score * weights["completeness"]
            + consistency_score * weights["consistency"]
        )

        # Generate quality summary
        quality_summary = _generate_quality_summary(
            overall_score,
            source_score,
            recency_score,
            completeness_score,
            consistency_score,
        )

        # Generate improvement recommendations
        improvement_recommendations = _generate_improvement_recommendations(
            source_score, recency_score, completeness_score, consistency_score
        )

        return ConfidenceScore(
            overall_score=round(overall_score, 1),
            source_quality=round(source_score, 1),
            data_recency=round(recency_score, 1),
            data_completeness=round(completeness_score, 1),
            analysis_consistency=round(consistency_score, 1),
            quality_summary=quality_summary,
            improvement_recommendations=improvement_recommendations,
        )

    except Exception as e:
        return ConfidenceScore(
            overall_score=0.0,
            source_quality=0.0,
            data_recency=0.0,
            data_completeness=0.0,
            analysis_consistency=0.0,
            quality_summary=f"Failed to calculate confidence scores: {e!s}",
            improvement_recommendations=[
                "Review analysis methodology",
                "Validate data sources",
            ],
        )


def generate_strategic_recommendations(
    synthesized_results: dict[str, Any],
    red_flags: list[RedFlag],
    opportunities: list[Opportunity],
) -> dict[str, Any]:
    """
    Generate prioritized strategic recommendations based on analysis results.

    Args:
        synthesized_results: Complete analysis results
        red_flags: Identified red flags and risks
        opportunities: Identified opportunities

    Returns:
        Dictionary containing prioritized strategic recommendations
    """
    try:
        # Generate priority actions (addressing critical red flags)
        priority_actions = _generate_priority_actions(red_flags)

        # Generate performance improvement recommendations
        performance_improvements = _generate_performance_improvements(
            synthesized_results.get("kpi_performance", {}),
            synthesized_results.get("benchmarking", {}),
        )

        # Generate market opportunity recommendations
        market_opportunities = _generate_market_opportunity_recommendations(
            opportunities
        )

        # Generate risk mitigation strategies
        risk_mitigation = _generate_risk_mitigation_strategies(red_flags)

        recommendations = {
            "priority_actions": priority_actions,
            "performance_improvements": performance_improvements,
            "market_opportunities": market_opportunities,
            "risk_mitigation": risk_mitigation,
            "implementation_timeline": _create_implementation_timeline(
                priority_actions, performance_improvements, market_opportunities
            ),
            "success_metrics": _define_success_metrics(
                priority_actions, performance_improvements, market_opportunities
            ),
        }

        return recommendations

    except Exception as e:
        return {
            "error": f"Failed to generate strategic recommendations: {e!s}",
            "priority_actions": [],
            "performance_improvements": [],
            "market_opportunities": [],
            "risk_mitigation": [],
        }


def create_visualization_data(synthesized_results: dict[str, Any]) -> dict[str, Any]:
    """
    Generate data for charts and visual representations.

    Args:
        synthesized_results: Complete analysis results

    Returns:
        Dictionary containing visualization data
    """
    try:
        visualization_data = {
            "kpi_performance_chart": _create_kpi_performance_chart_data(
                synthesized_results.get("kpi_performance", {})
            ),
            "benchmarking_radar_chart": _create_benchmarking_radar_data(
                synthesized_results.get("benchmarking", {})
            ),
            "market_validation_chart": _create_market_validation_chart_data(
                synthesized_results.get("market_validation", {})
            ),
            "confidence_score_chart": _create_confidence_score_chart_data(
                synthesized_results.get("data_quality", {})
            ),
            "trend_analysis_chart": _create_trend_analysis_chart_data(
                synthesized_results.get("kpi_performance", {}).get("trend_analysis", {})
            ),
        }

        return visualization_data

    except Exception as e:
        return {
            "error": f"Failed to create visualization data: {e!s}",
            "charts_available": False,
        }


# Helper functions for internal calculations


def _calculate_data_completeness(*analysis_results) -> float:
    """Calculate overall data completeness score."""
    total_fields = 0
    complete_fields = 0

    for result in analysis_results:
        if isinstance(result, dict):
            for key, value in result.items():
                total_fields += 1
                if value is not None and value != "" and value != []:
                    complete_fields += 1

    return (complete_fields / total_fields * 100) if total_fields > 0 else 0.0


def _calculate_data_consistency(market_validation, kpi_analysis, benchmarking) -> float:
    """Calculate data consistency score across analysis components."""
    # Placeholder implementation - would need specific consistency checks
    consistency_checks = []

    # Check market validation consistency
    if market_validation.get("overall_confidence", 0) > 0.7:
        consistency_checks.append(1.0)
    else:
        consistency_checks.append(0.5)

    # Check KPI analysis consistency
    kpi_performance = kpi_analysis.get("performance_summary", {})
    if kpi_performance and len(kpi_performance) > 0:
        consistency_checks.append(1.0)
    else:
        consistency_checks.append(0.3)

    return statistics.mean(consistency_checks) * 100 if consistency_checks else 0.0


def _generate_investment_thesis(
    synthesized_results: dict[str, Any], startup_context: dict[str, Any]
) -> dict[str, Any]:
    """Generate investment thesis based on analysis results."""
    market_validation = synthesized_results.get("market_validation", {})
    benchmarking = synthesized_results.get("benchmarking", {})

    overall_confidence = market_validation.get("overall_confidence", 0.0)
    performance_score = benchmarking.get("overall_performance_score", 0.0)

    if overall_confidence > 0.8 and performance_score > 0.7:
        recommendation = "Strong Investment Opportunity"
        confidence_level = "High"
    elif overall_confidence > 0.6 and performance_score > 0.5:
        recommendation = "Moderate Investment Opportunity"
        confidence_level = "Medium"
    else:
        recommendation = "High Risk Investment"
        confidence_level = "Low"

    return {
        "recommendation": recommendation,
        "confidence_level": confidence_level,
        "key_strengths": benchmarking.get("competitive_advantages", [])[:3],
        "primary_risks": market_validation.get("discrepancy_flags", [])[:3],
    }


def _extract_critical_findings(synthesized_results: dict[str, Any]) -> list[str]:
    """Extract the most critical findings from analysis."""
    findings = []

    # Market validation findings
    market_validation = synthesized_results.get("market_validation", {})
    if market_validation.get("discrepancy_flags"):
        findings.append(
            f"Market size validation identified {len(market_validation['discrepancy_flags'])} discrepancies"
        )

    # Performance findings
    benchmarking = synthesized_results.get("benchmarking", {})
    performance_score = benchmarking.get("overall_performance_score", 0.0)
    if performance_score > 0.8:
        findings.append("Exceptional performance across key industry benchmarks")
    elif performance_score < 0.4:
        findings.append("Performance significantly below industry standards")

    # KPI findings
    kpi_performance = synthesized_results.get("kpi_performance", {})
    missing_kpis = kpi_performance.get("missing_kpis", [])
    if missing_kpis:
        findings.append(f"Missing {len(missing_kpis)} critical industry KPIs")

    return findings[:5]  # Return top 5 findings


def _generate_strategic_priorities(
    synthesized_results: dict[str, Any],
) -> list[dict[str, Any]]:
    """Generate strategic priorities based on analysis."""
    priorities = []

    benchmarking = synthesized_results.get("benchmarking", {})
    improvement_areas = benchmarking.get("improvement_areas", [])

    for area in improvement_areas[:4]:  # Top 4 priorities
        priorities.append(
            {
                "priority": area,
                "timeline": "Medium-term",
                "expected_impact": "High",
                "resource_requirements": ["Team focus", "Process improvement"],
            }
        )

    return priorities


def _assess_executive_risks(synthesized_results: dict[str, Any]) -> dict[str, Any]:
    """Assess risks for executive summary."""
    market_validation = synthesized_results.get("market_validation", {})
    data_quality = synthesized_results.get("data_quality", {})

    critical_risks = []
    if market_validation.get("discrepancy_flags"):
        critical_risks.extend(market_validation["discrepancy_flags"][:2])

    if data_quality.get("completeness_score", 100) < 70:
        critical_risks.append("Insufficient data for comprehensive analysis")

    return {
        "critical_risks": critical_risks,
        "risk_level": "High"
        if len(critical_risks) > 2
        else "Medium"
        if critical_risks
        else "Low",
        "confidence_in_assessment": data_quality.get("consistency_score", 0) / 100,
    }


def _calculate_overall_confidence(synthesized_results: dict[str, Any]) -> float:
    """Calculate overall confidence score."""
    market_confidence = synthesized_results.get("market_validation", {}).get(
        "overall_confidence", 0.0
    )
    data_quality = synthesized_results.get("data_quality", {})
    completeness = data_quality.get("completeness_score", 0.0) / 100
    consistency = data_quality.get("consistency_score", 0.0) / 100

    return statistics.mean([market_confidence, completeness, consistency])


# Additional helper functions would be implemented here for red flag identification,
# opportunity highlighting, confidence scoring, etc. These are abbreviated for brevity.


def _identify_market_validation_red_flags(
    market_validation: dict[str, Any],
) -> list[RedFlag]:
    """Identify red flags in market validation."""
    red_flags = []

    discrepancy_flags = market_validation.get("discrepancy_flags", [])
    for flag in discrepancy_flags:
        red_flags.append(
            RedFlag(
                category="Market Validation",
                description=flag,
                severity="High",
                evidence=[f"Market validation discrepancy: {flag}"],
                impact_assessment="May indicate overestimated market opportunity",
                mitigation_strategies=[
                    "Conduct additional market research",
                    "Validate with industry experts",
                ],
                monitoring_requirements=["Monitor market size assumptions"],
            )
        )

    return red_flags


def _identify_kpi_performance_red_flags(
    kpi_performance: dict[str, Any],
) -> list[RedFlag]:
    """Identify red flags in KPI performance."""
    red_flags = []

    missing_kpis = kpi_performance.get("missing_kpis", [])
    if missing_kpis:
        red_flags.append(
            RedFlag(
                category="KPI Performance",
                description=f"Missing {len(missing_kpis)} critical KPIs",
                severity="Medium",
                evidence=[f"Missing KPIs: {', '.join(missing_kpis[:3])}"],
                impact_assessment="Incomplete performance assessment",
                mitigation_strategies=[
                    "Implement missing KPI tracking",
                    "Establish measurement processes",
                ],
                monitoring_requirements=["Track KPI implementation progress"],
            )
        )

    return red_flags


def _identify_benchmarking_red_flags(
    benchmarking_results: dict[str, Any],
) -> list[RedFlag]:
    """Identify red flags in benchmarking results."""
    red_flags = []

    performance_score = benchmarking_results.get("overall_performance_score", 0.0)
    if performance_score < 0.3:
        red_flags.append(
            RedFlag(
                category="Performance Benchmarking",
                description="Significantly below industry benchmarks",
                severity="Critical",
                evidence=[f"Overall performance score: {performance_score:.1%}"],
                impact_assessment="Poor competitive position",
                mitigation_strategies=[
                    "Focus on performance improvement",
                    "Benchmark against top performers",
                ],
                monitoring_requirements=["Monthly performance tracking"],
            )
        )

    return red_flags


def _identify_data_quality_red_flags(data_quality: dict[str, Any]) -> list[RedFlag]:
    """Identify red flags in data quality."""
    red_flags = []

    completeness_score = data_quality.get("completeness_score", 100)
    if completeness_score < 60:
        red_flags.append(
            RedFlag(
                category="Data Quality",
                description="Insufficient data for reliable analysis",
                severity="High",
                evidence=[f"Data completeness: {completeness_score:.1f}%"],
                impact_assessment="Analysis reliability compromised",
                mitigation_strategies=[
                    "Improve data collection",
                    "Validate data sources",
                ],
                monitoring_requirements=["Monitor data quality metrics"],
            )
        )

    return red_flags


# Comprehensive implementations for opportunity identification and analysis


def _identify_market_opportunities(
    market_analysis: dict[str, Any], industry_trends: dict[str, Any]
) -> list[Opportunity]:
    """Identify market opportunities based on analysis and trends."""
    opportunities = []

    # Market size opportunities
    market_validation = market_analysis.get("market_validation", {})
    tam_validation = market_validation.get("tam_validation", {})

    if tam_validation.get("market_estimate", 0) > tam_validation.get(
        "claimed_value", 0
    ):
        opportunities.append(
            Opportunity(
                category="Market Expansion",
                description="Market size larger than initially estimated",
                opportunity_type="Market",
                market_size=f"${tam_validation.get('market_estimate', 0):,.0f}",
                timeline="Medium-term",
                resource_requirements=["Market research", "Go-to-market strategy"],
                success_probability="High",
                strategic_value="High",
            )
        )

    # Industry trend opportunities
    growth_trends = industry_trends.get("growth_trends", [])
    for trend in growth_trends[:2]:  # Top 2 trends
        opportunities.append(
            Opportunity(
                category="Industry Trends",
                description=f"Capitalize on {trend} trend",
                opportunity_type="Market",
                market_size=None,
                timeline="Short-term",
                resource_requirements=["Product development", "Marketing alignment"],
                success_probability="Medium",
                strategic_value="Medium",
            )
        )

    return opportunities


def _identify_competitive_opportunities(
    competitive_analysis: dict[str, Any], performance_highlights: dict[str, Any]
) -> list[Opportunity]:
    """Identify competitive opportunities based on performance strengths."""
    opportunities = []

    competitive_advantages = competitive_analysis.get("competitive_advantages", [])
    for advantage in competitive_advantages[:3]:  # Top 3 advantages
        opportunities.append(
            Opportunity(
                category="Competitive Advantage",
                description=f"Leverage {advantage} for market differentiation",
                opportunity_type="Competitive",
                market_size=None,
                timeline="Short-term",
                resource_requirements=["Marketing", "Sales enablement"],
                success_probability="High",
                strategic_value="High",
            )
        )

    # Performance-based opportunities
    exceptional_kpis = performance_highlights.get("exceptional_performance", [])
    for kpi in exceptional_kpis[:2]:  # Top 2 exceptional KPIs
        opportunities.append(
            Opportunity(
                category="Performance Excellence",
                description=f"Market leadership position in {kpi}",
                opportunity_type="Competitive",
                market_size=None,
                timeline="Medium-term",
                resource_requirements=["Thought leadership", "Case studies"],
                success_probability="Medium",
                strategic_value="High",
            )
        )

    return opportunities


def _identify_performance_opportunities(
    performance_highlights: dict[str, Any],
) -> list[Opportunity]:
    """Identify performance optimization opportunities."""
    opportunities = []

    improvement_areas = performance_highlights.get("improvement_areas", [])
    for area in improvement_areas[:3]:  # Top 3 improvement areas
        opportunities.append(
            Opportunity(
                category="Performance Optimization",
                description=f"Optimize {area} performance",
                opportunity_type="Operational",
                market_size=None,
                timeline="Short-term",
                resource_requirements=["Process improvement", "Team training"],
                success_probability="High",
                strategic_value="Medium",
            )
        )

    # Quick wins
    quick_wins = performance_highlights.get("quick_wins", [])
    for win in quick_wins[:2]:  # Top 2 quick wins
        opportunities.append(
            Opportunity(
                category="Quick Wins",
                description=f"Implement {win} for immediate impact",
                opportunity_type="Operational",
                market_size=None,
                timeline="Short-term",
                resource_requirements=["Minimal resources"],
                success_probability="High",
                strategic_value="Medium",
            )
        )

    return opportunities


def _identify_strategic_opportunities(
    market_analysis: dict[str, Any], competitive_analysis: dict[str, Any]
) -> list[Opportunity]:
    """Identify strategic initiative opportunities."""
    opportunities = []

    # Partnership opportunities
    market_gaps = market_analysis.get("market_gaps", [])
    for gap in market_gaps[:2]:  # Top 2 market gaps
        opportunities.append(
            Opportunity(
                category="Strategic Partnerships",
                description=f"Partner to address {gap}",
                opportunity_type="Strategic",
                market_size=None,
                timeline="Long-term",
                resource_requirements=["Business development", "Legal support"],
                success_probability="Medium",
                strategic_value="High",
            )
        )

    # Product development opportunities
    unmet_needs = competitive_analysis.get("unmet_customer_needs", [])
    for need in unmet_needs[:2]:  # Top 2 unmet needs
        opportunities.append(
            Opportunity(
                category="Product Development",
                description=f"Develop solution for {need}",
                opportunity_type="Strategic",
                market_size=None,
                timeline="Long-term",
                resource_requirements=["R&D investment", "Product team"],
                success_probability="Medium",
                strategic_value="High",
            )
        )

    return opportunities


def _get_strategic_value_score(value: str) -> float:
    """Convert strategic value to numeric score."""
    value_scores = {"High": 3.0, "Medium": 2.0, "Low": 1.0}
    return value_scores.get(value, 1.0)


def _get_probability_score(probability: str) -> float:
    """Convert success probability to numeric score."""
    prob_scores = {"High": 3.0, "Medium": 2.0, "Low": 1.0}
    return prob_scores.get(probability, 1.0)


def _calculate_source_quality_score(source_credibility: dict[str, Any]) -> float:
    """Calculate source quality score based on credibility assessment."""
    authoritative_sources = source_credibility.get("authoritative_sources", 0)
    industry_reports = source_credibility.get("industry_reports", 0)
    general_sources = source_credibility.get("general_sources", 0)

    total_sources = authoritative_sources + industry_reports + general_sources
    if total_sources == 0:
        return 50.0  # Default score when no source data

    # Weight authoritative sources higher
    weighted_score = (
        authoritative_sources * 100 + industry_reports * 70 + general_sources * 40
    ) / total_sources

    return min(weighted_score, 100.0)


def _calculate_recency_score(data_recency: dict[str, Any]) -> float:
    """Calculate data recency score."""
    recent_data = data_recency.get("recent_data_percentage", 0)  # % of data < 6 months
    medium_data = data_recency.get("medium_data_percentage", 0)  # % of data 6-18 months
    old_data = data_recency.get("old_data_percentage", 0)  # % of data > 18 months

    # Weight recent data higher
    recency_score = recent_data * 1.0 + medium_data * 0.6 + old_data * 0.2
    return min(recency_score, 100.0)


def _calculate_completeness_score(data_completeness: dict[str, Any]) -> float:
    """Calculate data completeness score."""
    required_fields = data_completeness.get("required_fields", 0)
    completed_fields = data_completeness.get("completed_fields", 0)

    if required_fields == 0:
        return 100.0  # No requirements means complete

    completeness_percentage = (completed_fields / required_fields) * 100
    return min(completeness_percentage, 100.0)


def _calculate_consistency_score(data_consistency: dict[str, Any]) -> float:
    """Calculate data consistency score."""
    consistent_findings = data_consistency.get("consistent_findings", 0)
    total_findings = data_consistency.get("total_findings", 0)

    if total_findings == 0:
        return 100.0  # No findings means consistent

    consistency_percentage = (consistent_findings / total_findings) * 100
    return min(consistency_percentage, 100.0)


def _generate_quality_summary(
    overall: float,
    source: float,
    recency: float,
    completeness: float,
    consistency: float,
) -> str:
    """Generate quality assessment summary."""
    if overall >= 80:
        quality_level = "High"
        summary = "Analysis demonstrates high reliability with strong data sources and comprehensive coverage."
    elif overall >= 60:
        quality_level = "Medium"
        summary = "Analysis provides reliable insights with some limitations in data availability or consistency."
    else:
        quality_level = "Low"
        summary = "Analysis has significant limitations due to data quality, completeness, or consistency issues."

    # Add specific insights
    insights = []
    if source < 60:
        insights.append("limited authoritative sources")
    if recency < 60:
        insights.append("outdated market data")
    if completeness < 70:
        insights.append("incomplete data coverage")
    if consistency < 60:
        insights.append("inconsistent findings across sources")

    if insights:
        summary += f" Key concerns include: {', '.join(insights)}."

    return f"{quality_level} quality analysis. {summary}"


def _generate_improvement_recommendations(
    source: float, recency: float, completeness: float, consistency: float
) -> list[str]:
    """Generate recommendations for improving analysis quality."""
    recommendations = []

    if source < 70:
        recommendations.append(
            "Seek additional authoritative data sources (Gartner, Forrester, industry associations)"
        )

    if recency < 70:
        recommendations.append(
            "Update analysis with more recent market data and industry reports"
        )

    if completeness < 80:
        recommendations.append(
            "Collect missing KPI data and market information for comprehensive analysis"
        )

    if consistency < 70:
        recommendations.append(
            "Cross-validate findings across multiple sources to resolve inconsistencies"
        )

    if not recommendations:
        recommendations.append(
            "Maintain current data quality standards and monitor for updates"
        )

    return recommendations


def _generate_priority_actions(red_flags: list[RedFlag]) -> list[dict[str, Any]]:
    """Generate priority actions based on critical red flags."""
    priority_actions = []

    critical_flags = [flag for flag in red_flags if flag.severity == "Critical"]
    high_flags = [flag for flag in red_flags if flag.severity == "High"]

    # Address critical issues first
    for flag in critical_flags[:3]:  # Top 3 critical issues
        priority_actions.append(
            {
                "action": f"Address {flag.category.lower()}: {flag.description}",
                "timeline": "Immediate (1-2 weeks)",
                "priority": "Critical",
                "expected_impact": "High",
                "resource_requirements": flag.mitigation_strategies[:2],
                "success_metrics": ["Issue resolution", "Risk mitigation"],
            }
        )

    # Address high-priority issues
    for flag in high_flags[:2]:  # Top 2 high-priority issues
        priority_actions.append(
            {
                "action": f"Improve {flag.category.lower()}: {flag.description}",
                "timeline": "Short-term (1-3 months)",
                "priority": "High",
                "expected_impact": "Medium",
                "resource_requirements": flag.mitigation_strategies[:2],
                "success_metrics": ["Performance improvement", "Risk reduction"],
            }
        )

    return priority_actions


def _generate_performance_improvements(
    kpi_performance: dict[str, Any], benchmarking: dict[str, Any]
) -> list[dict[str, Any]]:
    """Generate performance improvement recommendations."""
    improvements = []

    improvement_areas = benchmarking.get("improvement_areas", [])
    for area in improvement_areas[:4]:  # Top 4 improvement areas
        improvements.append(
            {
                "improvement": f"Enhance {area} performance",
                "current_status": "Below industry benchmark",
                "target": "Industry median or above",
                "timeline": "Medium-term (3-6 months)",
                "expected_impact": "High",
                "resource_requirements": [
                    "Process optimization",
                    "Team training",
                    "Technology upgrade",
                ],
                "success_metrics": [f"{area} improvement", "Benchmark comparison"],
            }
        )

    # Quick wins from KPI analysis
    analyzed_kpis = kpi_performance.get("analyzed_kpis", [])
    for kpi in analyzed_kpis[:2]:  # Top 2 KPIs with improvement potential
        if isinstance(kpi, dict) and kpi.get("improvement_potential", 0) > 0.2:
            improvements.append(
                {
                    "improvement": f"Optimize {kpi.get('kpi_name', 'KPI')} performance",
                    "current_status": f"Current value: {kpi.get('current_value', 'N/A')}",
                    "target": f"Target: {kpi.get('target_value', 'Industry benchmark')}",
                    "timeline": "Short-term (1-3 months)",
                    "expected_impact": "Medium",
                    "resource_requirements": [
                        "Focused initiative",
                        "Performance monitoring",
                    ],
                    "success_metrics": [f"{kpi.get('kpi_name', 'KPI')} improvement"],
                }
            )

    return improvements


def _generate_market_opportunity_recommendations(
    opportunities: list[Opportunity],
) -> list[dict[str, Any]]:
    """Generate market opportunity recommendations."""
    market_recommendations = []

    market_opportunities = [
        opp for opp in opportunities if opp.opportunity_type == "Market"
    ]
    for opp in market_opportunities[:3]:  # Top 3 market opportunities
        market_recommendations.append(
            {
                "opportunity": opp.description,
                "market_potential": opp.market_size or "Significant",
                "timeline": opp.timeline,
                "implementation_steps": [
                    "Market research and validation",
                    "Go-to-market strategy development",
                    "Resource allocation and planning",
                ],
                "resource_requirements": opp.resource_requirements,
                "success_probability": opp.success_probability,
                "strategic_value": opp.strategic_value,
                "success_metrics": ["Market share growth", "Revenue increase"],
            }
        )

    return market_recommendations


def _generate_risk_mitigation_strategies(
    red_flags: list[RedFlag],
) -> list[dict[str, Any]]:
    """Generate risk mitigation strategies."""
    mitigation_strategies = []

    # Group red flags by category
    risk_categories = {}
    for flag in red_flags:
        if flag.category not in risk_categories:
            risk_categories[flag.category] = []
        risk_categories[flag.category].append(flag)

    # Generate mitigation strategies by category
    for category, flags in risk_categories.items():
        high_severity_flags = [f for f in flags if f.severity in ["Critical", "High"]]
        if high_severity_flags:
            # Combine mitigation strategies
            all_strategies = set()
            for flag in high_severity_flags:
                all_strategies.update(flag.mitigation_strategies)

            mitigation_strategies.append(
                {
                    "risk_category": category,
                    "risk_level": "High"
                    if any(f.severity == "Critical" for f in high_severity_flags)
                    else "Medium",
                    "mitigation_actions": list(all_strategies)[:4],  # Top 4 actions
                    "timeline": "Immediate"
                    if any(f.severity == "Critical" for f in high_severity_flags)
                    else "Short-term",
                    "monitoring_requirements": list(
                        set(
                            req
                            for flag in high_severity_flags
                            for req in flag.monitoring_requirements
                        )
                    )[:3],
                }
            )

    return mitigation_strategies


def _create_implementation_timeline(
    priority_actions: list[dict],
    performance_improvements: list[dict],
    market_opportunities: list[dict],
) -> dict[str, Any]:
    """Create implementation timeline for recommendations."""
    timeline = {
        "immediate_actions": [],
        "short_term_initiatives": [],
        "medium_term_projects": [],
        "long_term_strategic": [],
    }

    # Categorize by timeline
    all_recommendations = (
        priority_actions + performance_improvements + market_opportunities
    )

    for rec in all_recommendations:
        timeline_key = rec.get("timeline", "Medium-term")

        if "Immediate" in timeline_key or "1-2 weeks" in timeline_key:
            timeline["immediate_actions"].append(
                rec.get(
                    "action", rec.get("improvement", rec.get("opportunity", "Unknown"))
                )
            )
        elif "Short-term" in timeline_key or "1-3 months" in timeline_key:
            timeline["short_term_initiatives"].append(
                rec.get(
                    "action", rec.get("improvement", rec.get("opportunity", "Unknown"))
                )
            )
        elif "Medium-term" in timeline_key or "3-6 months" in timeline_key:
            timeline["medium_term_projects"].append(
                rec.get(
                    "action", rec.get("improvement", rec.get("opportunity", "Unknown"))
                )
            )
        else:
            timeline["long_term_strategic"].append(
                rec.get(
                    "action", rec.get("improvement", rec.get("opportunity", "Unknown"))
                )
            )

    return timeline


def _define_success_metrics(
    priority_actions: list[dict],
    performance_improvements: list[dict],
    market_opportunities: list[dict],
) -> dict[str, list[str]]:
    """Define success metrics for recommendations."""
    metrics = {
        "priority_actions": [],
        "performance_improvements": [],
        "market_opportunities": [],
    }

    # Extract metrics from each category
    for action in priority_actions:
        metrics["priority_actions"].extend(action.get("success_metrics", []))

    for improvement in performance_improvements:
        metrics["performance_improvements"].extend(
            improvement.get("success_metrics", [])
        )

    for opportunity in market_opportunities:
        metrics["market_opportunities"].extend(opportunity.get("success_metrics", []))

    # Remove duplicates and limit to top metrics
    for category in metrics:
        metrics[category] = list(set(metrics[category]))[:5]

    return metrics


def _create_kpi_performance_chart_data(
    kpi_performance: dict[str, Any],
) -> dict[str, Any]:
    """Create chart data for KPI performance visualization."""
    analyzed_kpis = kpi_performance.get("analyzed_kpis", [])

    chart_data = {
        "chart_type": "bar_chart",
        "title": "KPI Performance vs Industry Benchmarks",
        "data": [],
        "categories": [],
        "series": [
            {"name": "Current Performance", "data": []},
            {"name": "Industry Benchmark", "data": []},
        ],
    }

    for kpi in analyzed_kpis[:8]:  # Top 8 KPIs for visualization
        if isinstance(kpi, dict):
            kpi_name = kpi.get("kpi_name", "Unknown KPI")
            current_value = kpi.get("current_value", 0)
            benchmark_value = kpi.get("benchmark_value", current_value)

            chart_data["categories"].append(kpi_name)
            chart_data["series"][0]["data"].append(current_value)
            chart_data["series"][1]["data"].append(benchmark_value)

    return chart_data


def _create_benchmarking_radar_data(benchmarking: dict[str, Any]) -> dict[str, Any]:
    """Create radar chart data for benchmarking visualization."""
    peer_comparison = benchmarking.get("peer_comparison", {})

    chart_data = {
        "chart_type": "radar_chart",
        "title": "Performance vs Industry Peers",
        "categories": [],
        "series": [
            {"name": "Company Performance", "data": []},
            {"name": "Industry Average", "data": []},
        ],
    }

    # Extract performance categories
    for category, data in peer_comparison.items():
        if isinstance(data, dict):
            chart_data["categories"].append(category.replace("_", " ").title())
            chart_data["series"][0]["data"].append(data.get("company_score", 50))
            chart_data["series"][1]["data"].append(data.get("industry_average", 50))

    return chart_data


def _create_market_validation_chart_data(
    market_validation: dict[str, Any],
) -> dict[str, Any]:
    """Create chart data for market validation visualization."""
    chart_data = {
        "chart_type": "comparison_chart",
        "title": "Market Size Validation",
        "data": [],
    }

    for market_type in ["tam_validation", "sam_validation", "som_validation"]:
        validation_data = market_validation.get(market_type, {})
        if validation_data:
            chart_data["data"].append(
                {
                    "category": market_type.upper().replace("_VALIDATION", ""),
                    "claimed_value": validation_data.get("claimed_value", 0),
                    "market_estimate": validation_data.get("market_estimate", 0),
                    "variance_percentage": validation_data.get(
                        "variance_percentage", 0
                    ),
                }
            )

    return chart_data


def _create_confidence_score_chart_data(data_quality: dict[str, Any]) -> dict[str, Any]:
    """Create chart data for confidence score visualization."""
    chart_data = {
        "chart_type": "gauge_chart",
        "title": "Analysis Confidence Score",
        "overall_score": data_quality.get("overall_confidence", 0),
        "components": [
            {
                "name": "Data Completeness",
                "score": data_quality.get("completeness_score", 0),
            },
            {
                "name": "Data Consistency",
                "score": data_quality.get("consistency_score", 0),
            },
            {"name": "Source Quality", "score": data_quality.get("source_quality", 0)},
            {"name": "Data Recency", "score": data_quality.get("recency_score", 0)},
        ],
    }

    return chart_data


def _create_trend_analysis_chart_data(trend_analysis: dict[str, Any]) -> dict[str, Any]:
    """Create chart data for trend analysis visualization."""
    chart_data = {
        "chart_type": "line_chart",
        "title": "KPI Trend Analysis",
        "data": [],
        "time_periods": [],
        "series": [],
    }

    # Extract trend data for key KPIs
    kpi_trends = trend_analysis.get("kpi_trends", {})
    for kpi_name, trend_data in kpi_trends.items():
        if isinstance(trend_data, dict) and "historical_values" in trend_data:
            chart_data["series"].append(
                {"name": kpi_name, "data": trend_data["historical_values"]}
            )

    # Extract time periods
    chart_data["time_periods"] = trend_analysis.get("time_periods", [])

    return chart_data


def _generate_kpi_analysis_methodology(
    synthesized_results: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate KPI analysis methodology section showing which KPIs were analyzed and how.

    Args:
        synthesized_results: Complete analysis results

    Returns:
        Dictionary containing KPI analysis methodology details
    """
    kpi_performance = synthesized_results.get("kpi_performance", {})
    benchmarking = synthesized_results.get("benchmarking", {})
    industry_analysis = synthesized_results.get("industry_analysis", {})

    # Extract analyzed KPIs
    analyzed_kpis = kpi_performance.get("analyzed_kpis", [])
    missing_kpis = kpi_performance.get("missing_kpis", [])

    # Extract KPI details
    kpi_details = []
    for kpi in analyzed_kpis:
        if isinstance(kpi, dict):
            kpi_details.append(
                {
                    "kpi_name": kpi.get("kpi_name", "Unknown KPI"),
                    "current_value": kpi.get("current_value", "N/A"),
                    "industry_percentile": kpi.get("industry_percentile", "N/A"),
                    "performance_status": kpi.get("performance_status", "Unknown"),
                    "benchmark_comparison": kpi.get("benchmark_comparison", {}),
                    "trend_direction": kpi.get("trend_analysis", {}).get(
                        "direction", "Unknown"
                    ),
                }
            )

    # Generate analysis approach description
    analysis_approach = _describe_analysis_approach(industry_analysis, benchmarking)

    # Generate data sources used
    data_sources = _extract_kpi_data_sources(synthesized_results)

    # Generate confidence assessment
    confidence_assessment = _assess_kpi_analysis_confidence(
        analyzed_kpis, missing_kpis, benchmarking
    )

    return {
        "analysis_scope": {
            "total_kpis_analyzed": len(analyzed_kpis),
            "missing_critical_kpis": len(missing_kpis),
            "analysis_coverage": f"{len(analyzed_kpis)}/{len(analyzed_kpis) + len(missing_kpis)} KPIs analyzed"
            if analyzed_kpis or missing_kpis
            else "No KPI data available",
        },
        "analyzed_kpis": kpi_details,
        "missing_kpis": missing_kpis[:5],  # Top 5 missing KPIs
        "analysis_approach": analysis_approach,
        "data_sources": data_sources,
        "benchmarking_methodology": {
            "industry_classification": industry_analysis.get(
                "classification", "Unknown"
            ),
            "benchmark_data_quality": benchmarking.get("data_quality", "Unknown"),
            "peer_comparison_method": "Industry percentile ranking",
            "performance_scoring": "Weighted average based on industry benchmarks",
        },
        "confidence_assessment": confidence_assessment,
        "methodology_summary": _generate_methodology_summary(
            analyzed_kpis, missing_kpis, analysis_approach
        ),
    }


def _describe_analysis_approach(
    industry_analysis: dict[str, Any], benchmarking: dict[str, Any]
) -> str:
    """Describe the KPI analysis approach used."""
    industry = industry_analysis.get("classification", "Unknown").lower()
    confidence = industry_analysis.get("confidence", 0.0)

    approach_parts = []

    # Industry-specific approach
    if "saas" in industry or "software" in industry:
        approach_parts.append(
            "SaaS-specific KPI framework focusing on recurring revenue metrics, customer acquisition costs, and retention rates"
        )
    elif "ecommerce" in industry or "retail" in industry:
        approach_parts.append(
            "E-commerce KPI framework emphasizing conversion rates, average order value, and customer lifetime value"
        )
    elif "fintech" in industry or "financial" in industry:
        approach_parts.append(
            "Fintech KPI framework prioritizing transaction volume, user acquisition costs, and regulatory compliance metrics"
        )
    else:
        approach_parts.append(
            "Industry-agnostic KPI framework covering core business performance metrics"
        )

    # Benchmarking approach
    if confidence > 0.7:
        approach_parts.append(
            "High-confidence industry classification enabled precise benchmarking against relevant peer companies"
        )
    else:
        approach_parts.append(
            "General industry benchmarking applied due to limited classification confidence"
        )

    # Performance scoring
    approach_parts.append(
        "Performance scores calculated using weighted percentile rankings against industry benchmarks"
    )

    return ". ".join(approach_parts) + "."


def _extract_kpi_data_sources(synthesized_results: dict[str, Any]) -> list[str]:
    """Extract data sources used for KPI analysis."""
    sources = set()

    # Add standard KPI analysis sources
    sources.update(
        [
            "Startup-provided KPI data",
            "Industry benchmark databases",
            "Competitive analysis reports",
            "Market research data",
        ]
    )

    # Extract from market validation
    market_validation = synthesized_results.get("market_validation", {})
    for validation_key in ["tam_validation", "sam_validation", "som_validation"]:
        validation_data = market_validation.get(validation_key, {})
        sources.update(validation_data.get("sources", []))

    return list(sources)


def _assess_kpi_analysis_confidence(
    analyzed_kpis: list[dict], missing_kpis: list[str], benchmarking: dict[str, Any]
) -> dict[str, Any]:
    """Assess confidence in KPI analysis results."""
    total_kpis = len(analyzed_kpis) + len(missing_kpis)
    analysis_coverage = len(analyzed_kpis) / total_kpis if total_kpis > 0 else 0

    # Assess data quality
    data_quality_score = 0
    if analysis_coverage > 0.8:
        data_quality_score += 40
    elif analysis_coverage > 0.6:
        data_quality_score += 30
    elif analysis_coverage > 0.4:
        data_quality_score += 20

    # Assess benchmark quality
    benchmark_quality = benchmarking.get("data_quality", "Unknown")
    if benchmark_quality == "High":
        data_quality_score += 30
    elif benchmark_quality == "Medium":
        data_quality_score += 20
    else:
        data_quality_score += 10

    # Assess KPI completeness
    if len(missing_kpis) == 0:
        data_quality_score += 30
    elif len(missing_kpis) <= 3:
        data_quality_score += 20
    else:
        data_quality_score += 10

    # Determine confidence level
    if data_quality_score >= 80:
        confidence_level = "High"
        confidence_description = (
            "Comprehensive KPI analysis with reliable industry benchmarks"
        )
    elif data_quality_score >= 60:
        confidence_level = "Medium"
        confidence_description = (
            "Good KPI analysis with some limitations in data availability"
        )
    else:
        confidence_level = "Low"
        confidence_description = (
            "Limited KPI analysis due to insufficient data or benchmarks"
        )

    return {
        "confidence_level": confidence_level,
        "confidence_score": min(data_quality_score, 100),
        "confidence_description": confidence_description,
        "limitations": _identify_kpi_analysis_limitations(
            analyzed_kpis, missing_kpis, analysis_coverage
        ),
    }


def _identify_kpi_analysis_limitations(
    analyzed_kpis: list[dict], missing_kpis: list[str], coverage: float
) -> list[str]:
    """Identify limitations in KPI analysis."""
    limitations = []

    if coverage < 0.5:
        limitations.append(
            "Limited KPI coverage may not provide comprehensive performance assessment"
        )

    if len(missing_kpis) > 5:
        limitations.append(
            "Missing critical industry KPIs limits competitive benchmarking accuracy"
        )

    # Check for data quality issues in analyzed KPIs
    incomplete_kpis = 0
    for kpi in analyzed_kpis:
        if isinstance(kpi, dict):
            if not kpi.get("current_value") or kpi.get("current_value") == "N/A":
                incomplete_kpis += 1

    if incomplete_kpis > len(analyzed_kpis) * 0.3:
        limitations.append(
            "Significant portion of analyzed KPIs have incomplete or missing data"
        )

    if not limitations:
        limitations.append("Analysis appears comprehensive with good data quality")

    return limitations


def _generate_methodology_summary(
    analyzed_kpis: list[dict], missing_kpis: list[str], analysis_approach: str
) -> str:
    """Generate a concise summary of the KPI analysis methodology."""
    total_kpis = len(analyzed_kpis) + len(missing_kpis)
    coverage_percentage = (
        (len(analyzed_kpis) / total_kpis * 100) if total_kpis > 0 else 0
    )

    summary_parts = [
        f"Analyzed {len(analyzed_kpis)} KPIs ({coverage_percentage:.0f}% coverage) using {analysis_approach.lower()}",
        "Industry benchmarking applied with percentile ranking methodology",
        "Performance assessment based on current values vs. industry standards",
    ]

    if missing_kpis:
        summary_parts.append(
            f"Note: {len(missing_kpis)} critical KPIs were not available for analysis"
        )

    return ". ".join(summary_parts) + "."

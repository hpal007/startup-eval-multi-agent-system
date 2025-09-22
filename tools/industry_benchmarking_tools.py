"""Tools for industry benchmarking and statistical analysis."""

from typing import Any


def calculate_percentile_ranking(
    kpi_value: float,
    benchmark_data: dict[str, float],
    kpi_name: str
) -> dict[str, Any]:
    """
    Calculate percentile ranking for a KPI value against industry benchmarks.

    Args:
        kpi_value: The startup's KPI value
        benchmark_data: Dictionary with percentile benchmarks (p25, p50, p75, etc.)
        kpi_name: Name of the KPI being analyzed

    Returns:
        Dictionary with percentile ranking and performance assessment
    """
    if not benchmark_data:
        return {
            "percentile": None,
            "performance_level": "Unknown",
            "benchmark_comparison": "No benchmark data available",
            "improvement_potential": "Cannot assess without benchmarks"
        }

    # Extract percentile values
    p25 = benchmark_data.get("p25", 0)
    p50 = benchmark_data.get("p50", 0)
    p75 = benchmark_data.get("p75", 0)
    p90 = benchmark_data.get("p90", p75 * 1.2)  # Estimate if not provided

    # Determine if higher values are better (most KPIs) or worse (costs, churn)
    lower_is_better_kpis = [
        "churn", "burn", "cost", "cac", "customer acquisition cost",
        "attrition", "turnover", "cycle time", "response time"
    ]

    is_lower_better = any(keyword in kpi_name.lower() for keyword in lower_is_better_kpis)

    # Calculate percentile ranking
    if is_lower_better:
        # For metrics where lower is better (costs, churn, etc.)
        if kpi_value <= p25:
            percentile = 75 + (p25 - kpi_value) / p25 * 25  # 75-100th percentile
            performance_level = "Excellent"
        elif kpi_value <= p50:
            percentile = 50 + (p50 - kpi_value) / (p50 - p25) * 25  # 50-75th percentile
            performance_level = "Good"
        elif kpi_value <= p75:
            percentile = 25 + (p75 - kpi_value) / (p75 - p50) * 25  # 25-50th percentile
            performance_level = "Below Average"
        else:
            percentile = max(0, 25 - (kpi_value - p75) / p75 * 25)  # 0-25th percentile
            performance_level = "Poor"
    else:
        # For metrics where higher is better (revenue, retention, etc.)
        if kpi_value >= p90:
            percentile = 90 + min(10, (kpi_value - p90) / p90 * 10)  # 90-100th percentile
            performance_level = "Excellent"
        elif kpi_value >= p75:
            percentile = 75 + (kpi_value - p75) / (p90 - p75) * 15  # 75-90th percentile
            performance_level = "Good"
        elif kpi_value >= p50:
            percentile = 50 + (kpi_value - p50) / (p75 - p50) * 25  # 50-75th percentile
            performance_level = "Average"
        elif kpi_value >= p25:
            percentile = 25 + (kpi_value - p25) / (p50 - p25) * 25  # 25-50th percentile
            performance_level = "Below Average"
        else:
            percentile = max(0, (kpi_value / p25) * 25)  # 0-25th percentile
            performance_level = "Poor"

    # Generate benchmark comparison text
    benchmark_comparison = _generate_benchmark_comparison(
        kpi_value, p25, p50, p75, kpi_name, is_lower_better
    )

    # Generate improvement potential assessment
    improvement_potential = _assess_improvement_potential(
        percentile, performance_level, kpi_name, is_lower_better
    )

    return {
        "percentile": round(percentile, 1),
        "performance_level": performance_level,
        "benchmark_comparison": benchmark_comparison,
        "improvement_potential": improvement_potential,
        "benchmark_data_used": {
            "p25": p25,
            "p50": p50,
            "p75": p75,
            "p90": p90
        }
    }


def analyze_performance_gaps(
    startup_kpis: dict[str, float],
    kpi_framework: dict[str, Any],
    growth_stage: str
) -> dict[str, Any]:
    """
    Analyze performance gaps across multiple KPIs.

    Args:
        startup_kpis: Dictionary of startup's KPI values
        kpi_framework: KPI framework with benchmark data
        growth_stage: Current growth stage for appropriate benchmarks

    Returns:
        Comprehensive performance gap analysis
    """
    performance_analysis = {
        "overall_score": 0.0,
        "kpi_performances": [],
        "strengths": [],
        "improvement_areas": [],
        "critical_gaps": [],
        "competitive_advantages": []
    }

    total_weighted_score = 0.0
    total_weight = 0.0

    # Analyze each primary KPI
    for kpi_data in kpi_framework.get("primary_kpis", []):
        kpi_name = kpi_data["name"]
        importance_weight = kpi_data.get("importance_weight", 0.1)

        # Find matching startup KPI (exact or partial match)
        startup_value = _find_matching_kpi_value(startup_kpis, kpi_name)

        if startup_value is not None:
            # Get appropriate benchmark data for growth stage
            benchmark_ranges = kpi_data.get("benchmark_ranges", {})
            stage_benchmarks = benchmark_ranges.get(growth_stage, {})

            if stage_benchmarks:
                # Calculate percentile ranking
                percentile_result = calculate_percentile_ranking(
                    startup_value, stage_benchmarks, kpi_name
                )

                # Create KPI performance record
                kpi_performance = {
                    "kpi_name": kpi_name,
                    "current_value": startup_value,
                    "percentile": percentile_result["percentile"],
                    "performance_level": percentile_result["performance_level"],
                    "benchmark_comparison": percentile_result["benchmark_comparison"],
                    "importance_weight": importance_weight,
                    "weighted_score": (percentile_result["percentile"] or 0) * importance_weight
                }

                performance_analysis["kpi_performances"].append(kpi_performance)

                # Add to overall score calculation
                if percentile_result["percentile"] is not None:
                    total_weighted_score += kpi_performance["weighted_score"]
                    total_weight += importance_weight

                # Categorize performance
                percentile = percentile_result["percentile"] or 0
                if percentile >= 90:
                    performance_analysis["competitive_advantages"].append({
                        "kpi": kpi_name,
                        "percentile": percentile,
                        "description": f"Exceptional performance in {kpi_name}"
                    })
                elif percentile >= 75:
                    performance_analysis["strengths"].append({
                        "kpi": kpi_name,
                        "percentile": percentile,
                        "description": f"Strong performance in {kpi_name}"
                    })
                elif percentile <= 25:
                    performance_analysis["critical_gaps"].append({
                        "kpi": kpi_name,
                        "percentile": percentile,
                        "description": f"Critical improvement needed in {kpi_name}",
                        "priority": "High" if importance_weight > 0.15 else "Medium"
                    })
                elif percentile <= 50:
                    performance_analysis["improvement_areas"].append({
                        "kpi": kpi_name,
                        "percentile": percentile,
                        "description": f"Below average performance in {kpi_name}",
                        "priority": "Medium" if importance_weight > 0.10 else "Low"
                    })

    # Calculate overall performance score
    if total_weight > 0:
        performance_analysis["overall_score"] = total_weighted_score / total_weight

    # Generate performance summary
    performance_analysis["performance_summary"] = _generate_performance_summary(
        performance_analysis["overall_score"],
        len(performance_analysis["strengths"]),
        len(performance_analysis["improvement_areas"]),
        len(performance_analysis["critical_gaps"])
    )

    return performance_analysis

def generate_improvement_recommendations(
    performance_gaps: dict[str, Any],
    industry: str,
    growth_stage: str
) -> list[dict[str, Any]]:
    """
    Generate specific improvement recommendations based on performance gaps.

    Args:
        performance_gaps: Performance gap analysis results
        industry: Industry classification
        growth_stage: Current growth stage

    Returns:
        List of prioritized improvement recommendations
    """
    recommendations = []

    # Process critical gaps first (highest priority)
    for gap in performance_gaps.get("critical_gaps", []):
        kpi_name = gap["kpi"]
        recommendations.extend(_get_kpi_specific_recommendations(
            kpi_name, "Critical", industry, growth_stage
        ))

    # Process improvement areas (medium priority)
    for area in performance_gaps.get("improvement_areas", []):
        kpi_name = area["kpi"]
        priority = area.get("priority", "Medium")
        recommendations.extend(_get_kpi_specific_recommendations(
            kpi_name, priority, industry, growth_stage
        ))

    # Add growth stage specific recommendations
    recommendations.extend(_get_growth_stage_recommendations(
        growth_stage, performance_gaps["overall_score"]
    ))

    # Sort by priority and impact
    recommendations.sort(key=lambda x: (
        {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}[x["priority"]],
        -x.get("impact_score", 0)
    ))

    return recommendations[:10]  # Return top 10 recommendations


def calculate_industry_position(
    overall_score: float,
    kpi_performances: list[dict[str, Any]],
    industry: str
) -> dict[str, Any]:
    """
    Calculate startup's position within the industry.

    Args:
        overall_score: Overall performance score (0-100)
        kpi_performances: List of individual KPI performances
        industry: Industry classification

    Returns:
        Industry position analysis
    """
    # Determine overall industry position
    if overall_score >= 80:
        position = "Top Performer"
        position_description = "Among the top 20% of companies in the industry"
    elif overall_score >= 60:
        position = "Above Average"
        position_description = "Performing better than most industry peers"
    elif overall_score >= 40:
        position = "Average"
        position_description = "Performing at industry average levels"
    elif overall_score >= 20:
        position = "Below Average"
        position_description = "Underperforming compared to industry peers"
    else:
        position = "Needs Improvement"
        position_description = "Significant performance gaps compared to industry standards"

    # Calculate performance distribution
    excellent_count = sum(1 for kpi in kpi_performances if kpi.get("percentile", 0) >= 90)
    good_count = sum(1 for kpi in kpi_performances if 75 <= kpi.get("percentile", 0) < 90)
    average_count = sum(1 for kpi in kpi_performances if 50 <= kpi.get("percentile", 0) < 75)
    poor_count = sum(1 for kpi in kpi_performances if kpi.get("percentile", 0) < 50)

    total_kpis = len(kpi_performances)

    return {
        "industry_position": position,
        "position_description": position_description,
        "overall_percentile": overall_score,
        "performance_distribution": {
            "excellent": {"count": excellent_count, "percentage": excellent_count / total_kpis * 100 if total_kpis > 0 else 0},
            "good": {"count": good_count, "percentage": good_count / total_kpis * 100 if total_kpis > 0 else 0},
            "average": {"count": average_count, "percentage": average_count / total_kpis * 100 if total_kpis > 0 else 0},
            "poor": {"count": poor_count, "percentage": poor_count / total_kpis * 100 if total_kpis > 0 else 0}
        },
        "industry_context": _get_industry_context(industry, position),
        "peer_comparison": _generate_peer_comparison(overall_score, industry)
    }


def _find_matching_kpi_value(startup_kpis: dict[str, float], target_kpi: str) -> float | None:
    """Find matching KPI value from startup data."""
    # Try exact match first
    if target_kpi in startup_kpis:
        return startup_kpis[target_kpi]

    # Try case-insensitive match
    target_lower = target_kpi.lower()
    for kpi_name, value in startup_kpis.items():
        if kpi_name.lower() == target_lower:
            return value

    # Try partial matches
    for kpi_name, value in startup_kpis.items():
        if (target_lower in kpi_name.lower() or
            kpi_name.lower() in target_lower):
            return value

    return None


def _generate_benchmark_comparison(
    value: float, p25: float, p50: float, p75: float,
    kpi_name: str, is_lower_better: bool
) -> str:
    """Generate human-readable benchmark comparison."""
    if is_lower_better:
        if value <= p25:
            return f"Excellent - significantly better than industry median ({p50})"
        elif value <= p50:
            return f"Good - better than industry median ({p50})"
        elif value <= p75:
            return f"Below average - higher than industry median ({p50})"
        else:
            return f"Poor - significantly higher than industry median ({p50})"
    else:
        if value >= p75:
            return f"Good - above 75th percentile (industry median: {p50})"
        elif value >= p50:
            return f"Average - above industry median ({p50})"
        elif value >= p25:
            return f"Below average - below industry median ({p50})"
        else:
            return f"Poor - significantly below industry median ({p50})"


def _assess_improvement_potential(
    percentile: float, performance_level: str, kpi_name: str, is_lower_better: bool
) -> str:
    """Assess improvement potential for a KPI."""
    if percentile >= 90:
        return "Limited improvement potential - already at top performance levels"
    elif percentile >= 75:
        return "Moderate improvement potential - can reach top-tier performance"
    elif percentile >= 50:
        return "Good improvement potential - can reach above-average performance"
    elif percentile >= 25:
        return "High improvement potential - significant room for growth"
    else:
        return "Critical improvement needed - substantial performance gaps to address"


def _get_kpi_specific_recommendations(
    kpi_name: str, priority: str, industry: str, growth_stage: str
) -> list[dict[str, Any]]:
    """Get specific recommendations for improving a KPI."""
    recommendations = []
    kpi_lower = kpi_name.lower()

    # Revenue and growth KPIs
    if any(keyword in kpi_lower for keyword in ["revenue", "growth", "arr", "mrr"]):
        recommendations.append({
            "category": "Revenue Growth",
            "recommendation": "Focus on customer acquisition and expansion revenue",
            "specific_actions": [
                "Implement customer success programs to drive expansion",
                "Optimize pricing strategy and packaging",
                "Invest in sales and marketing efficiency"
            ],
            "priority": priority,
            "impact_score": 9,
            "timeframe": "3-6 months"
        })

    # Customer acquisition and retention
    elif any(keyword in kpi_lower for keyword in ["cac", "acquisition", "cost"]):
        recommendations.append({
            "category": "Customer Acquisition",
            "recommendation": "Optimize customer acquisition channels and reduce CAC",
            "specific_actions": [
                "Analyze channel performance and reallocate budget",
                "Improve conversion rates through A/B testing",
                "Implement referral and viral growth programs"
            ],
            "priority": priority,
            "impact_score": 8,
            "timeframe": "2-4 months"
        })

    elif any(keyword in kpi_lower for keyword in ["churn", "retention", "ltv"]):
        recommendations.append({
            "category": "Customer Retention",
            "recommendation": "Improve customer retention and lifetime value",
            "specific_actions": [
                "Implement proactive customer success management",
                "Develop onboarding and engagement programs",
                "Create loyalty and retention incentives"
            ],
            "priority": priority,
            "impact_score": 9,
            "timeframe": "2-3 months"
        })

    # Operational efficiency
    elif any(keyword in kpi_lower for keyword in ["margin", "efficiency", "productivity"]):
        recommendations.append({
            "category": "Operational Efficiency",
            "recommendation": "Improve operational efficiency and margins",
            "specific_actions": [
                "Automate manual processes and workflows",
                "Optimize cost structure and vendor relationships",
                "Implement performance monitoring and optimization"
            ],
            "priority": priority,
            "impact_score": 7,
            "timeframe": "3-6 months"
        })

    # Financial management
    elif any(keyword in kpi_lower for keyword in ["burn", "runway", "cash"]):
        recommendations.append({
            "category": "Financial Management",
            "recommendation": "Optimize cash management and extend runway",
            "specific_actions": [
                "Review and optimize operating expenses",
                "Improve cash flow forecasting and management",
                "Consider revenue-based financing options"
            ],
            "priority": "Critical",  # Always critical for cash-related KPIs
            "impact_score": 10,
            "timeframe": "1-2 months"
        })

    return recommendations


def _get_growth_stage_recommendations(growth_stage: str, overall_score: float) -> list[dict[str, Any]]:
    """Get growth stage specific recommendations."""
    recommendations = []

    if growth_stage == "seed":
        recommendations.append({
            "category": "Product-Market Fit",
            "recommendation": "Focus on achieving strong product-market fit",
            "specific_actions": [
                "Conduct regular customer interviews and feedback sessions",
                "Iterate on product based on user behavior data",
                "Establish clear value proposition and messaging"
            ],
            "priority": "High",
            "impact_score": 9,
            "timeframe": "2-4 months"
        })

    elif growth_stage == "early":
        recommendations.append({
            "category": "Scalable Growth",
            "recommendation": "Build scalable growth and operational systems",
            "specific_actions": [
                "Implement scalable customer acquisition channels",
                "Build operational processes and systems",
                "Establish key performance metrics and tracking"
            ],
            "priority": "High",
            "impact_score": 8,
            "timeframe": "3-6 months"
        })

    elif growth_stage == "growth":
        recommendations.append({
            "category": "Market Expansion",
            "recommendation": "Focus on market expansion and efficiency",
            "specific_actions": [
                "Expand to new market segments or geographies",
                "Optimize unit economics and operational efficiency",
                "Build competitive moats and differentiation"
            ],
            "priority": "Medium",
            "impact_score": 7,
            "timeframe": "6-12 months"
        })

    return recommendations


def _generate_performance_summary(
    overall_score: float, strengths_count: int,
    improvement_areas_count: int, critical_gaps_count: int
) -> str:
    """Generate overall performance summary."""
    if overall_score >= 80:
        return f"Strong overall performance with {strengths_count} key strengths. Minor optimization opportunities in {improvement_areas_count} areas."
    elif overall_score >= 60:
        return f"Above-average performance with {strengths_count} strengths. Focus needed on {improvement_areas_count + critical_gaps_count} improvement areas."
    elif overall_score >= 40:
        return f"Average industry performance. Balanced focus needed across {improvement_areas_count} improvement areas and {critical_gaps_count} critical gaps."
    else:
        return f"Below-average performance requiring immediate attention. {critical_gaps_count} critical gaps and {improvement_areas_count} improvement areas identified."


def _get_industry_context(industry: str, position: str) -> str:
    """Get industry-specific context for performance position."""
    industry_contexts = {
        "saas": "SaaS companies typically focus on recurring revenue growth and customer retention metrics",
        "ecommerce": "E-commerce businesses prioritize conversion rates, customer acquisition costs, and lifetime value",
        "fintech": "Fintech companies emphasize regulatory compliance, transaction volumes, and user trust metrics",
        "healthcare": "Healthcare startups focus on clinical outcomes, regulatory approvals, and patient satisfaction",
        "marketplace": "Marketplace platforms prioritize network effects, transaction volume, and take rates"
    }

    base_context = industry_contexts.get(industry.lower(), "Industry-specific performance benchmarks vary significantly")
    return f"{base_context}. Current position as '{position}' indicates {'strong competitive standing' if position in ['Top Performer', 'Above Average'] else 'opportunities for improvement'}."


def _generate_peer_comparison(overall_score: float, industry: str) -> str:
    """Generate peer comparison description."""
    if overall_score >= 80:
        return f"Outperforming 80%+ of {industry} companies at similar stage"
    elif overall_score >= 60:
        return f"Performing better than 60%+ of {industry} peers"
    elif overall_score >= 40:
        return f"Performing at median levels for {industry} companies"
    else:
        return f"Underperforming compared to most {industry} peers - significant improvement opportunities"

def validate_exceptional_performance(
    kpi_name: str,
    kpi_value: float,
    benchmark_data: dict[str, float],
    industry: str,
    growth_stage: str
) -> dict[str, Any]:
    """
    Validate exceptional performance claims and identify potential competitive advantages.

    Args:
        kpi_name: Name of the KPI being validated
        kpi_value: The startup's KPI value
        benchmark_data: Industry benchmark data
        industry: Industry classification
        growth_stage: Current growth stage

    Returns:
        Validation results for exceptional performance
    """
    if not benchmark_data:
        return {
            "is_exceptional": False,
            "validation_status": "Cannot validate - no benchmark data",
            "competitive_advantage": False,
            "validation_confidence": 0.0
        }

    # Calculate percentile to determine if performance is exceptional
    percentile_result = calculate_percentile_ranking(kpi_value, benchmark_data, kpi_name)
    percentile = percentile_result.get("percentile", 0)

    # Define exceptional performance threshold (90th+ percentile)
    is_exceptional = percentile >= 90

    # Validate the claim based on industry context
    validation_confidence = _calculate_validation_confidence(
        kpi_name, kpi_value, benchmark_data, industry, growth_stage
    )

    # Determine if this represents a competitive advantage
    competitive_advantage = _assess_competitive_advantage(
        kpi_name, percentile, industry, growth_stage
    )

    # Generate validation explanation
    validation_explanation = _generate_validation_explanation(
        kpi_name, kpi_value, percentile, is_exceptional, competitive_advantage
    )

    return {
        "is_exceptional": is_exceptional,
        "percentile": percentile,
        "validation_status": "Validated" if validation_confidence > 0.7 else "Needs verification",
        "competitive_advantage": competitive_advantage,
        "validation_confidence": validation_confidence,
        "explanation": validation_explanation,
        "benchmark_context": {
            "industry_median": benchmark_data.get("p50", 0),
            "top_quartile": benchmark_data.get("p75", 0),
            "top_decile": benchmark_data.get("p90", benchmark_data.get("p75", 0) * 1.2)
        }
    }


def correlate_market_trends(
    startup_kpis: dict[str, float],
    industry: str,
    market_trends: list[str],
    growth_stage: str
) -> dict[str, Any]:
    """
    Correlate startup KPI performance with identified market trends.

    Args:
        startup_kpis: Dictionary of startup's KPI values
        industry: Industry classification
        market_trends: List of identified market trends
        growth_stage: Current growth stage

    Returns:
        Correlation analysis between KPIs and market trends
    """
    correlations = {
        "trend_alignment": [],
        "trend_misalignment": [],
        "opportunity_indicators": [],
        "risk_indicators": [],
        "strategic_implications": []
    }

    # Analyze each trend for KPI correlation
    for trend in market_trends:
        trend_lower = trend.lower()

        # Growth trends
        if any(keyword in trend_lower for keyword in ["growth", "expansion", "increasing", "rising"]):
            growth_kpis = _find_growth_related_kpis(startup_kpis)
            for kpi_name, kpi_value in growth_kpis.items():
                correlation = _assess_trend_kpi_correlation(kpi_name, kpi_value, trend, "positive")
                if correlation["strength"] > 0.5:
                    correlations["trend_alignment"].append(correlation)

        # Efficiency trends
        elif any(keyword in trend_lower for keyword in ["efficiency", "optimization", "automation"]):
            efficiency_kpis = _find_efficiency_related_kpis(startup_kpis)
            for kpi_name, kpi_value in efficiency_kpis.items():
                correlation = _assess_trend_kpi_correlation(kpi_name, kpi_value, trend, "efficiency")
                if correlation["strength"] > 0.5:
                    correlations["trend_alignment"].append(correlation)

        # Market consolidation trends
        elif any(keyword in trend_lower for keyword in ["consolidation", "competition", "saturation"]):
            competitive_kpis = _find_competitive_related_kpis(startup_kpis)
            for kpi_name, kpi_value in competitive_kpis.items():
                correlation = _assess_trend_kpi_correlation(kpi_name, kpi_value, trend, "competitive")
                correlations["risk_indicators"].append(correlation)

    # Generate strategic implications
    correlations["strategic_implications"] = _generate_strategic_implications(
        correlations, industry, growth_stage
    )

    return correlations

def generate_typical_ranges_context(
    kpi_name: str,
    industry: str,
    growth_stage: str,
    benchmark_data: dict[str, float]
) -> dict[str, Any]:
    """
    Generate context on typical ranges and performance expectations for a KPI.

    Args:
        kpi_name: Name of the KPI
        industry: Industry classification
        growth_stage: Current growth stage
        benchmark_data: Industry benchmark data

    Returns:
        Comprehensive context on typical ranges and expectations
    """
    if not benchmark_data:
        return {
            "typical_ranges": "No benchmark data available",
            "performance_expectations": "Cannot provide expectations without benchmarks",
            "context": "Benchmark data needed for meaningful comparison"
        }

    # Extract percentile ranges
    p25 = benchmark_data.get("p25", 0)
    p50 = benchmark_data.get("p50", 0)
    p75 = benchmark_data.get("p75", 0)
    p90 = benchmark_data.get("p90", p75 * 1.2)

    # Generate typical ranges description
    typical_ranges = {
        "poor_performance": f"Below {p25} (bottom 25%)",
        "below_average": f"{p25} - {p50} (25th-50th percentile)",
        "average_performance": f"{p50} - {p75} (50th-75th percentile)",
        "good_performance": f"{p75} - {p90} (75th-90th percentile)",
        "exceptional_performance": f"Above {p90} (top 10%)"
    }

    # Generate performance expectations based on growth stage
    performance_expectations = _generate_stage_specific_expectations(
        kpi_name, industry, growth_stage, benchmark_data
    )

    # Generate industry-specific context
    industry_context = _generate_industry_specific_context(
        kpi_name, industry, benchmark_data
    )

    return {
        "typical_ranges": typical_ranges,
        "performance_expectations": performance_expectations,
        "industry_context": industry_context,
        "benchmark_interpretation": _generate_benchmark_interpretation(kpi_name),
        "improvement_trajectory": _generate_improvement_trajectory(kpi_name, growth_stage)
    }


def _calculate_validation_confidence(
    kpi_name: str, kpi_value: float, benchmark_data: dict[str, float],
    industry: str, growth_stage: str
) -> float:
    """Calculate confidence level for exceptional performance validation."""
    confidence_factors = []

    # Data quality factor
    if len(benchmark_data) >= 3:  # Has p25, p50, p75
        confidence_factors.append(0.8)
    else:
        confidence_factors.append(0.5)

    # Industry specificity factor
    industry_specific_industries = ["saas", "ecommerce", "fintech", "healthcare"]
    if any(ind in industry.lower() for ind in industry_specific_industries):
        confidence_factors.append(0.9)
    else:
        confidence_factors.append(0.6)

    # KPI importance factor
    critical_kpis = ["revenue", "growth", "retention", "margin", "cac", "ltv"]
    if any(kpi in kpi_name.lower() for kpi in critical_kpis):
        confidence_factors.append(0.9)
    else:
        confidence_factors.append(0.7)

    # Calculate weighted average confidence
    return sum(confidence_factors) / len(confidence_factors)


def _assess_competitive_advantage(
    kpi_name: str, percentile: float, industry: str, growth_stage: str
) -> bool:
    """Assess if exceptional performance represents a competitive advantage."""
    # Must be in top 10% to be considered competitive advantage
    if percentile < 90:
        return False

    # Strategic KPIs that provide competitive advantages
    strategic_kpis = [
        "customer retention", "nps", "net promoter score", "customer satisfaction",
        "gross margin", "unit economics", "ltv/cac", "market share",
        "brand recognition", "customer acquisition cost", "viral coefficient"
    ]

    return any(strategic_kpi in kpi_name.lower() for strategic_kpi in strategic_kpis)


def _generate_validation_explanation(
    kpi_name: str, kpi_value: float, percentile: float,
    is_exceptional: bool, competitive_advantage: bool
) -> str:
    """Generate explanation for performance validation."""
    if is_exceptional:
        if competitive_advantage:
            return f"{kpi_name} performance at {kpi_value} represents a significant competitive advantage, ranking in the {percentile:.1f}th percentile of industry peers."
        else:
            return f"{kpi_name} shows exceptional performance at {kpi_value} ({percentile:.1f}th percentile), though may not constitute a sustainable competitive advantage."
    else:
        return f"{kpi_name} performance at {kpi_value} is within normal industry ranges ({percentile:.1f}th percentile)."


def _find_growth_related_kpis(startup_kpis: dict[str, float]) -> dict[str, float]:
    """Find KPIs related to growth metrics."""
    growth_keywords = ["growth", "revenue", "user", "customer", "arr", "mrr", "expansion"]
    return {
        kpi_name: value for kpi_name, value in startup_kpis.items()
        if any(keyword in kpi_name.lower() for keyword in growth_keywords)
    }


def _find_efficiency_related_kpis(startup_kpis: dict[str, float]) -> dict[str, float]:
    """Find KPIs related to efficiency metrics."""
    efficiency_keywords = ["margin", "productivity", "efficiency", "cost", "cac", "ltv", "automation"]
    return {
        kpi_name: value for kpi_name, value in startup_kpis.items()
        if any(keyword in kpi_name.lower() for keyword in efficiency_keywords)
    }


def _find_competitive_related_kpis(startup_kpis: dict[str, float]) -> dict[str, float]:
    """Find KPIs related to competitive positioning."""
    competitive_keywords = ["market share", "retention", "nps", "satisfaction", "churn", "competitive"]
    return {
        kpi_name: value for kpi_name, value in startup_kpis.items()
        if any(keyword in kpi_name.lower() for keyword in competitive_keywords)
    }


def _assess_trend_kpi_correlation(
    kpi_name: str, kpi_value: float, trend: str, trend_type: str
) -> dict[str, Any]:
    """Assess correlation between a KPI and market trend."""
    # Simplified correlation assessment
    correlation_strength = 0.7  # Default moderate correlation

    # Adjust based on trend type and KPI relevance
    if trend_type == "positive" and "growth" in kpi_name.lower():
        correlation_strength = 0.9
    elif (trend_type == "efficiency" and any(keyword in kpi_name.lower() for keyword in ["margin", "cost", "efficiency"])) or (trend_type == "competitive" and any(keyword in kpi_name.lower() for keyword in ["retention", "share", "nps"])):
        correlation_strength = 0.8

    return {
        "kpi_name": kpi_name,
        "kpi_value": kpi_value,
        "trend": trend,
        "strength": correlation_strength,
        "correlation_type": trend_type
    }


def _generate_strategic_implications(
    correlations: dict[str, Any], industry: str, growth_stage: str
) -> list[str]:
    """Generate strategic implications from trend correlations."""
    implications = []

    # Positive trend alignments
    if correlations["trend_alignment"]:
        implications.append(
            f"Strong alignment with {len(correlations['trend_alignment'])} market trends suggests good strategic positioning"
        )

    # Risk indicators
    if correlations["risk_indicators"]:
        implications.append(
            f"Identified {len(correlations['risk_indicators'])} potential risk areas requiring strategic attention"
        )

    # Growth stage specific implications
    if growth_stage == "seed":
        implications.append("Focus on validating product-market fit while monitoring emerging trends")
    elif growth_stage == "growth":
        implications.append("Leverage trend alignment to accelerate market expansion")

    return implications


def _generate_stage_specific_expectations(
    kpi_name: str, industry: str, growth_stage: str, benchmark_data: dict[str, float]
) -> str:
    """Generate growth stage specific performance expectations."""
    p50 = benchmark_data.get("p50", 0)
    p75 = benchmark_data.get("p75", 0)

    stage_expectations = {
        "seed": f"Seed stage companies typically target {p50} as baseline, with {p75} representing strong performance",
        "early": f"Early stage companies should aim for {p75} or higher to demonstrate scalability",
        "growth": f"Growth stage companies need consistent performance above {p75} to maintain momentum",
        "mature": f"Mature companies should sustain performance at or above {p75} while optimizing efficiency"
    }

    return stage_expectations.get(growth_stage, f"Target performance above industry median ({p50})")


def _generate_industry_specific_context(
    kpi_name: str, industry: str, benchmark_data: dict[str, float]
) -> str:
    """Generate industry-specific context for KPI interpretation."""
    industry_contexts = {
        "saas": "SaaS companies typically show higher retention rates and recurring revenue metrics",
        "ecommerce": "E-commerce businesses focus on conversion rates and customer lifetime value",
        "fintech": "Fintech companies emphasize regulatory compliance and transaction volume growth",
        "healthcare": "Healthcare startups prioritize clinical outcomes and regulatory milestone achievement"
    }

    base_context = industry_contexts.get(industry.lower(), "Industry-specific benchmarks vary significantly")
    return f"{base_context}. Current benchmark median of {benchmark_data.get('p50', 'N/A')} reflects typical industry performance."


def _generate_benchmark_interpretation(kpi_name: str) -> str:
    """Generate interpretation guidance for benchmark data."""
    kpi_lower = kpi_name.lower()

    if any(keyword in kpi_lower for keyword in ["cost", "churn", "burn"]):
        return "Lower values indicate better performance for this metric"
    elif any(keyword in kpi_lower for keyword in ["revenue", "growth", "retention", "margin"]):
        return "Higher values indicate better performance for this metric"
    else:
        return "Benchmark interpretation depends on specific business context"


def _generate_improvement_trajectory(kpi_name: str, growth_stage: str) -> str:
    """Generate expected improvement trajectory for KPI."""
    trajectories = {
        "seed": "Focus on establishing baseline performance and identifying improvement levers",
        "early": "Target steady improvement with 10-20% quarterly gains where possible",
        "growth": "Maintain consistent performance while scaling operations efficiently",
        "mature": "Optimize for sustainable performance with incremental improvements"
    }

    return trajectories.get(growth_stage, "Establish consistent measurement and improvement processes")

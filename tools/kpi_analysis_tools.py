"""Tools for KPI analysis including time series analysis and performance scoring."""

import statistics
from typing import Any


def analyze_kpi_trends(historical_data: dict[str, list[dict]], industry_benchmarks: dict[str, Any]) -> dict[str, Any]:
    """
    Analyze trends in KPI historical data.
    
    Args:
        historical_data: Dictionary with KPI names as keys and list of {date, value} dicts as values
        industry_benchmarks: Industry benchmark data for comparison
        
    Returns:
        Dictionary containing trend analysis results
    """
    trend_results = {}

    for kpi_name, data_points in historical_data.items():
        if len(data_points) < 2:
            trend_results[kpi_name] = {
                "trend": "insufficient_data",
                "growth_rate": None,
                "volatility": None,
                "direction": "unknown"
            }
            continue

        # Sort data points by date
        sorted_data = sorted(data_points, key=lambda x: x['date'])
        values = [point['value'] for point in sorted_data]

        # Calculate growth rate
        if len(values) >= 2:
            first_value = values[0]
            last_value = values[-1]
            if first_value != 0:
                growth_rate = ((last_value - first_value) / first_value) * 100
            else:
                growth_rate = 0
        else:
            growth_rate = 0

        # Calculate volatility (standard deviation)
        volatility = statistics.stdev(values) if len(values) > 1 else 0

        # Determine trend direction
        if growth_rate > 5:
            direction = "increasing"
        elif growth_rate < -5:
            direction = "decreasing"
        else:
            direction = "stable"

        # Compare with industry benchmarks
        industry_growth = industry_benchmarks.get(kpi_name, {}).get('typical_growth_rate', 0)
        relative_performance = "above_industry" if growth_rate > industry_growth else "below_industry"

        trend_results[kpi_name] = {
            "trend": direction,
            "growth_rate": round(growth_rate, 2),
            "volatility": round(volatility, 2),
            "direction": direction,
            "relative_performance": relative_performance,
            "data_points": len(values),
            "latest_value": last_value
        }

    return trend_results


def calculate_performance_scores(current_kpis: dict[str, Any], industry_benchmarks: dict[str, Any],
                               kpi_weights: dict[str, float] | None = None) -> dict[str, Any]:
    """
    Calculate performance scores for KPIs against industry benchmarks.
    
    Args:
        current_kpis: Current KPI values
        industry_benchmarks: Industry benchmark data with percentiles
        kpi_weights: Optional weights for different KPIs
        
    Returns:
        Dictionary containing performance scores and analysis
    """
    if kpi_weights is None:
        kpi_weights = {}

    performance_results = {}
    total_weighted_score = 0
    total_weight = 0

    for kpi_name, current_value in current_kpis.items():
        if kpi_name not in industry_benchmarks:
            performance_results[kpi_name] = {
                "score": None,
                "percentile": None,
                "status": "no_benchmark_data"
            }
            continue

        benchmarks = industry_benchmarks[kpi_name]
        weight = kpi_weights.get(kpi_name, 1.0)

        # Calculate percentile ranking
        percentile = calculate_percentile_ranking(current_value, benchmarks)

        # Convert percentile to performance score (0-100)
        performance_score = percentile

        # Determine performance status
        if percentile >= 75:
            status = "excellent"
        elif percentile >= 50:
            status = "good"
        elif percentile >= 25:
            status = "below_average"
        else:
            status = "poor"

        performance_results[kpi_name] = {
            "current_value": current_value,
            "score": round(performance_score, 1),
            "percentile": round(percentile, 1),
            "status": status,
            "weight": weight,
            "benchmark_p25": benchmarks.get('p25'),
            "benchmark_p50": benchmarks.get('p50'),
            "benchmark_p75": benchmarks.get('p75'),
            "benchmark_p90": benchmarks.get('p90')
        }

        # Add to weighted total
        total_weighted_score += performance_score * weight
        total_weight += weight

    # Calculate overall performance score
    overall_score = total_weighted_score / total_weight if total_weight > 0 else 0

    return {
        "individual_scores": performance_results,
        "overall_score": round(overall_score, 1),
        "total_kpis_analyzed": len([k for k in performance_results.values() if k["score"] is not None])
    }


def calculate_percentile_ranking(value: float, benchmarks: dict[str, float]) -> float:
    """
    Calculate percentile ranking of a value against industry benchmarks.
    
    Args:
        value: The value to rank
        benchmarks: Dictionary with percentile benchmarks (p25, p50, p75, p90)
        
    Returns:
        Percentile ranking (0-100)
    """
    p25 = benchmarks.get('p25', 0)
    p50 = benchmarks.get('p50', 0)
    p75 = benchmarks.get('p75', 0)
    p90 = benchmarks.get('p90', 0)

    if value >= p90:
        return 90 + (10 * min((value - p90) / (p90 * 0.1), 1))  # Cap at 100
    elif value >= p75:
        return 75 + (15 * (value - p75) / (p90 - p75))
    elif value >= p50:
        return 50 + (25 * (value - p50) / (p75 - p50))
    elif value >= p25:
        return 25 + (25 * (value - p25) / (p50 - p25))
    else:
        return max(0, 25 * (value / p25))  # Don't go below 0


def generate_improvement_recommendations(performance_results: dict[str, Any],
                                       industry_best_practices: dict[str, list[str]],
                                       growth_stage: str) -> list[dict[str, Any]]:
    """
    Generate specific improvement recommendations based on performance analysis.
    
    Args:
        performance_results: Results from performance scoring
        industry_best_practices: Industry-specific best practices
        growth_stage: Current growth stage of the startup
        
    Returns:
        List of prioritized recommendations
    """
    recommendations = []

    # Analyze individual KPI performance
    individual_scores = performance_results.get("individual_scores", {})

    for kpi_name, kpi_data in individual_scores.items():
        if kpi_data["score"] is None:
            continue

        score = kpi_data["score"]
        status = kpi_data["status"]

        # Generate recommendations based on performance
        if status in ["poor", "below_average"]:
            priority = "high" if status == "poor" else "medium"

            # Get industry-specific recommendations
            best_practices = industry_best_practices.get(kpi_name, [])

            recommendation = {
                "kpi": kpi_name,
                "priority": priority,
                "current_performance": f"{score}th percentile",
                "issue": f"Performance below industry standards ({status})",
                "recommendations": best_practices[:3] if best_practices else [
                    f"Focus on improving {kpi_name} through targeted initiatives",
                    "Benchmark against top performers in your industry",
                    f"Implement measurement and tracking systems for {kpi_name}"
                ],
                "expected_impact": "Significant improvement in overall performance",
                "timeline": "3-6 months" if priority == "high" else "6-12 months"
            }
            recommendations.append(recommendation)

    # Add growth stage specific recommendations
    if growth_stage == "seed":
        recommendations.append({
            "kpi": "overall",
            "priority": "high",
            "issue": "Early stage focus areas",
            "recommendations": [
                "Establish baseline KPI tracking systems",
                "Focus on product-market fit indicators",
                "Implement customer feedback loops"
            ],
            "expected_impact": "Foundation for future growth",
            "timeline": "1-3 months"
        })
    elif growth_stage == "growth":
        recommendations.append({
            "kpi": "overall",
            "priority": "medium",
            "issue": "Scaling optimization",
            "recommendations": [
                "Optimize unit economics and efficiency metrics",
                "Implement advanced analytics and reporting",
                "Focus on sustainable growth strategies"
            ],
            "expected_impact": "Improved scalability and efficiency",
            "timeline": "3-6 months"
        })

    # Sort by priority
    priority_order = {"high": 3, "medium": 2, "low": 1}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 0), reverse=True)

    return recommendations


def identify_competitive_advantages(performance_results: dict[str, Any],
                                  industry_context: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Identify potential competitive advantages based on exceptional KPI performance.
    
    Args:
        performance_results: Results from performance scoring
        industry_context: Industry context and competitive landscape
        
    Returns:
        List of identified competitive advantages
    """
    advantages = []
    individual_scores = performance_results.get("individual_scores", {})

    for kpi_name, kpi_data in individual_scores.items():
        if kpi_data["score"] is None:
            continue

        score = kpi_data["score"]
        percentile = kpi_data["percentile"]

        # Identify exceptional performance (top 10%)
        if percentile >= 90:
            advantage = {
                "kpi": kpi_name,
                "performance_level": "exceptional",
                "percentile": percentile,
                "competitive_advantage": f"Top 10% performance in {kpi_name}",
                "sustainability": assess_advantage_sustainability(kpi_name, kpi_data, industry_context),
                "strategic_value": assess_strategic_value(kpi_name, industry_context),
                "recommendations": [
                    f"Leverage {kpi_name} strength in marketing and positioning",
                    f"Use {kpi_name} performance as competitive differentiator",
                    f"Maintain and expand {kpi_name} advantage through continued investment"
                ]
            }
            advantages.append(advantage)
        elif percentile >= 75:
            advantage = {
                "kpi": kpi_name,
                "performance_level": "strong",
                "percentile": percentile,
                "competitive_advantage": f"Above-average performance in {kpi_name}",
                "sustainability": assess_advantage_sustainability(kpi_name, kpi_data, industry_context),
                "strategic_value": assess_strategic_value(kpi_name, industry_context),
                "recommendations": [
                    f"Build on {kpi_name} strength to reach top-tier performance",
                    f"Use {kpi_name} as foundation for competitive positioning"
                ]
            }
            advantages.append(advantage)

    return advantages


def assess_advantage_sustainability(kpi_name: str, kpi_data: dict[str, Any],
                                  industry_context: dict[str, Any]) -> str:
    """Assess the sustainability of a competitive advantage."""
    # This is a simplified assessment - in practice, this would be more sophisticated
    strategic_kpis = ["customer_retention", "nps", "ltv_cac_ratio", "gross_margin"]

    if kpi_name.lower() in strategic_kpis:
        return "high"
    elif kpi_data["percentile"] >= 95:
        return "medium"
    else:
        return "low"


def assess_strategic_value(kpi_name: str, industry_context: dict[str, Any]) -> str:
    """Assess the strategic value of a KPI advantage."""
    # This is a simplified assessment - in practice, this would be more sophisticated
    high_value_kpis = ["revenue_growth", "customer_acquisition_cost", "lifetime_value", "churn_rate"]

    if kpi_name.lower() in high_value_kpis:
        return "high"
    else:
        return "medium"


def validate_exceptional_claims(kpi_data: dict[str, Any], industry_benchmarks: dict[str, Any]) -> dict[str, Any]:
    """
    Validate exceptional performance claims against industry data.
    
    Args:
        kpi_data: KPI performance data
        industry_benchmarks: Industry benchmark data
        
    Returns:
        Validation results with confidence scores
    """
    validation_results = {}

    for kpi_name, performance in kpi_data.items():
        if performance.get("percentile", 0) >= 90:
            # This is an exceptional claim that needs validation
            benchmark_data = industry_benchmarks.get(kpi_name, {})

            validation = {
                "claim": f"Top 10% performance in {kpi_name}",
                "validation_status": "requires_verification",
                "confidence_score": calculate_validation_confidence(performance, benchmark_data),
                "supporting_evidence_needed": [
                    "Historical performance data",
                    "Methodology verification",
                    "Third-party validation"
                ],
                "red_flags": identify_performance_red_flags(performance, benchmark_data)
            }

            validation_results[kpi_name] = validation

    return validation_results


def calculate_validation_confidence(performance: dict[str, Any], benchmark_data: dict[str, Any]) -> float:
    """Calculate confidence score for performance validation."""
    confidence = 0.5  # Base confidence

    # Increase confidence based on data quality
    if benchmark_data.get('sample_size', 0) > 100:
        confidence += 0.2
    if benchmark_data.get('data_recency', 'old') == 'recent':
        confidence += 0.2
    if performance.get('data_points', 0) > 6:
        confidence += 0.1

    return min(confidence, 1.0)


def identify_performance_red_flags(performance: dict[str, Any], benchmark_data: dict[str, Any]) -> list[str]:
    """Identify potential red flags in exceptional performance claims."""
    red_flags = []

    percentile = performance.get("percentile", 0)

    if percentile > 99:
        red_flags.append("Performance appears too good to be true - requires verification")

    if performance.get("data_points", 0) < 3:
        red_flags.append("Insufficient historical data to validate performance")

    if not benchmark_data:
        red_flags.append("No industry benchmark data available for validation")

    return red_flags


def analyze_individual_kpi_performance(kpi_name: str, current_value: float,
                                     historical_data: list[dict],
                                     industry_benchmarks: dict[str, Any],
                                     industry_context: dict[str, Any]) -> dict[str, Any]:
    """
    Perform detailed analysis of individual KPI performance.
    
    Args:
        kpi_name: Name of the KPI to analyze
        current_value: Current value of the KPI
        historical_data: Historical data points for the KPI
        industry_benchmarks: Industry benchmark data
        industry_context: Industry and business context
        
    Returns:
        Comprehensive individual KPI analysis
    """
    # Calculate percentile ranking
    benchmarks = industry_benchmarks.get(kpi_name, {})
    percentile = calculate_percentile_ranking(current_value, benchmarks) if benchmarks else None

    # Analyze historical trends
    trend_analysis = {}
    if historical_data and len(historical_data) > 1:
        trend_data = {kpi_name: historical_data}
        trend_results = analyze_kpi_trends(trend_data, {kpi_name: benchmarks})
        trend_analysis = trend_results.get(kpi_name, {})

    # Determine performance status
    performance_status = "unknown"
    if percentile is not None:
        if percentile >= 90:
            performance_status = "exceptional"
        elif percentile >= 75:
            performance_status = "excellent"
        elif percentile >= 50:
            performance_status = "good"
        elif percentile >= 25:
            performance_status = "below_average"
        else:
            performance_status = "poor"

    # Generate specific recommendations
    recommendations = generate_kpi_specific_recommendations(
        kpi_name, current_value, percentile, trend_analysis, industry_context
    )

    # Identify potential competitive advantages
    competitive_advantage = None
    if percentile and percentile >= 75:
        competitive_advantage = {
            "level": "exceptional" if percentile >= 90 else "strong",
            "description": f"Performance in top {100-percentile:.0f}% of industry",
            "sustainability": assess_advantage_sustainability(kpi_name, {"percentile": percentile}, industry_context),
            "strategic_value": assess_strategic_value(kpi_name, industry_context)
        }

    # Calculate improvement potential
    improvement_potential = calculate_improvement_potential(
        current_value, percentile, benchmarks, trend_analysis
    )

    analysis = {
        "kpi_name": kpi_name,
        "current_value": current_value,
        "percentile_ranking": percentile,
        "performance_status": performance_status,
        "benchmark_comparison": {
            "p25": benchmarks.get('p25'),
            "p50": benchmarks.get('p50'),
            "p75": benchmarks.get('p75'),
            "p90": benchmarks.get('p90'),
            "current_vs_median": ((current_value - benchmarks.get('p50', 0)) / benchmarks.get('p50', 1)) * 100 if benchmarks.get('p50') else None
        },
        "trend_analysis": trend_analysis,
        "competitive_advantage": competitive_advantage,
        "improvement_potential": improvement_potential,
        "recommendations": recommendations,
        "risk_factors": identify_kpi_risk_factors(kpi_name, current_value, trend_analysis, benchmarks),
        "confidence_score": calculate_analysis_confidence(historical_data, benchmarks, industry_context)
    }

    return analysis

def generate_kpi_specific_recommendations(kpi_name: str, current_value: float,
                                        percentile: float | None, trend_analysis: dict[str, Any],
                                        industry_context: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Generate specific recommendations for individual KPI improvement.
    
    Args:
        kpi_name: Name of the KPI
        current_value: Current KPI value
        percentile: Percentile ranking
        trend_analysis: Trend analysis results
        industry_context: Industry context
        
    Returns:
        List of specific recommendations
    """
    recommendations = []
    industry = industry_context.get('industry', 'general')
    growth_stage = industry_context.get('growth_stage', 'unknown')

    # Performance-based recommendations
    if percentile is not None:
        if percentile < 25:
            recommendations.append({
                "priority": "high",
                "category": "performance_improvement",
                "action": f"Urgent improvement needed for {kpi_name}",
                "specific_steps": get_industry_specific_improvement_steps(kpi_name, industry, growth_stage),
                "expected_impact": "Significant performance improvement",
                "timeline": "1-3 months",
                "success_metrics": [f"Achieve {kpi_name} above 25th percentile", f"Improve {kpi_name} by 20-30%"]
            })
        elif percentile < 50:
            recommendations.append({
                "priority": "medium",
                "category": "performance_optimization",
                "action": f"Optimize {kpi_name} to reach industry median",
                "specific_steps": get_industry_specific_improvement_steps(kpi_name, industry, growth_stage),
                "expected_impact": "Moderate performance improvement",
                "timeline": "3-6 months",
                "success_metrics": [f"Achieve {kpi_name} above 50th percentile"]
            })

    # Trend-based recommendations
    growth_rate = trend_analysis.get('growth_rate', 0)
    if growth_rate < -10:
        recommendations.append({
            "priority": "high",
            "category": "trend_reversal",
            "action": f"Address declining trend in {kpi_name}",
            "specific_steps": [
                f"Investigate root causes of {kpi_name} decline",
                f"Implement corrective measures for {kpi_name}",
                f"Monitor {kpi_name} weekly until trend reverses"
            ],
            "expected_impact": "Trend stabilization and improvement",
            "timeline": "1-2 months",
            "success_metrics": [f"Achieve positive {kpi_name} growth rate"]
        })
    elif growth_rate > 20 and percentile and percentile > 75:
        recommendations.append({
            "priority": "medium",
            "category": "advantage_leverage",
            "action": f"Leverage strong {kpi_name} performance",
            "specific_steps": [
                f"Use {kpi_name} strength in competitive positioning",
                f"Scale successful {kpi_name} strategies",
                f"Share {kpi_name} best practices across organization"
            ],
            "expected_impact": "Competitive advantage reinforcement",
            "timeline": "Ongoing",
            "success_metrics": [f"Maintain {kpi_name} growth trajectory"]
        })

    return recommendations


def get_industry_specific_improvement_steps(kpi_name: str, industry: str, growth_stage: str) -> list[str]:
    """
    Get industry-specific improvement steps for a KPI.
    
    Args:
        kpi_name: Name of the KPI
        industry: Industry sector
        growth_stage: Growth stage of the company
        
    Returns:
        List of specific improvement steps
    """
    # Industry-specific KPI improvement strategies
    improvement_strategies = {
        "saas": {
            "churn_rate": [
                "Implement customer success programs",
                "Improve onboarding experience",
                "Develop customer health scoring",
                "Create proactive retention campaigns"
            ],
            "customer_acquisition_cost": [
                "Optimize marketing channel mix",
                "Improve conversion funnel",
                "Implement referral programs",
                "Focus on organic growth strategies"
            ],
            "monthly_recurring_revenue": [
                "Expand existing customer accounts",
                "Improve pricing strategy",
                "Reduce churn rate",
                "Accelerate new customer acquisition"
            ]
        },
        "ecommerce": {
            "conversion_rate": [
                "Optimize website user experience",
                "Improve product page design",
                "Implement A/B testing",
                "Enhance checkout process"
            ],
            "average_order_value": [
                "Implement upselling strategies",
                "Create product bundles",
                "Offer volume discounts",
                "Improve product recommendations"
            ],
            "customer_lifetime_value": [
                "Develop loyalty programs",
                "Improve customer retention",
                "Increase purchase frequency",
                "Expand product catalog"
            ]
        },
        "fintech": {
            "transaction_volume": [
                "Expand user base",
                "Increase transaction frequency",
                "Add new payment methods",
                "Improve user engagement"
            ],
            "user_acquisition_cost": [
                "Optimize digital marketing",
                "Implement referral programs",
                "Focus on organic growth",
                "Improve conversion rates"
            ]
        }
    }

    # Get industry-specific steps or default generic steps
    industry_strategies = improvement_strategies.get(industry.lower(), {})
    kpi_steps = industry_strategies.get(kpi_name.lower(), [
        f"Benchmark {kpi_name} against top performers",
        f"Identify key drivers of {kpi_name}",
        "Implement targeted improvement initiatives",
        f"Monitor {kpi_name} progress regularly"
    ])

    # Add growth stage specific considerations
    if growth_stage == "seed":
        kpi_steps.append(f"Focus on establishing baseline {kpi_name} measurement")
    elif growth_stage == "growth":
        kpi_steps.append(f"Scale successful {kpi_name} improvement strategies")

    return kpi_steps


def calculate_improvement_potential(current_value: float, percentile: float | None,
                                  benchmarks: dict[str, Any], trend_analysis: dict[str, Any]) -> dict[str, Any]:
    """
    Calculate the improvement potential for a KPI.
    
    Args:
        current_value: Current KPI value
        percentile: Current percentile ranking
        benchmarks: Industry benchmarks
        trend_analysis: Trend analysis results
        
    Returns:
        Improvement potential analysis
    """
    if not benchmarks or percentile is None:
        return {"potential": "unknown", "reason": "insufficient_benchmark_data"}

    p50 = benchmarks.get('p50', current_value)
    p75 = benchmarks.get('p75', current_value)
    p90 = benchmarks.get('p90', current_value)

    # Calculate potential improvements
    potential_to_median = ((p50 - current_value) / current_value) * 100 if current_value > 0 else 0
    potential_to_75th = ((p75 - current_value) / current_value) * 100 if current_value > 0 else 0
    potential_to_90th = ((p90 - current_value) / current_value) * 100 if current_value > 0 else 0

    # Determine realistic improvement potential
    if percentile < 25:
        realistic_target = "median"
        realistic_improvement = potential_to_median
        timeline = "6-12 months"
    elif percentile < 50:
        realistic_target = "75th percentile"
        realistic_improvement = potential_to_75th
        timeline = "3-6 months"
    elif percentile < 75:
        realistic_target = "90th percentile"
        realistic_improvement = potential_to_90th
        timeline = "6-12 months"
    else:
        realistic_target = "maintain excellence"
        realistic_improvement = 0
        timeline = "ongoing"

    # Consider trend momentum
    growth_rate = trend_analysis.get('growth_rate', 0)
    if growth_rate > 10:
        timeline = "3-6 months"  # Faster improvement with positive momentum
    elif growth_rate < -10:
        timeline = "9-18 months"  # Slower improvement with negative momentum

    return {
        "realistic_target": realistic_target,
        "realistic_improvement_percent": round(realistic_improvement, 1),
        "timeline": timeline,
        "potential_to_median": round(potential_to_median, 1),
        "potential_to_75th": round(potential_to_75th, 1),
        "potential_to_90th": round(potential_to_90th, 1),
        "current_momentum": "positive" if growth_rate > 5 else "negative" if growth_rate < -5 else "stable"
    }


def identify_kpi_risk_factors(kpi_name: str, current_value: float,
                            trend_analysis: dict[str, Any], benchmarks: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Identify risk factors associated with KPI performance.
    
    Args:
        kpi_name: Name of the KPI
        current_value: Current KPI value
        trend_analysis: Trend analysis results
        benchmarks: Industry benchmarks
        
    Returns:
        List of identified risk factors
    """
    risk_factors = []

    # Performance-based risks
    percentile = calculate_percentile_ranking(current_value, benchmarks) if benchmarks else None
    if percentile is not None and percentile < 10:
        risk_factors.append({
            "type": "performance_risk",
            "severity": "high",
            "description": f"{kpi_name} performance in bottom 10% of industry",
            "impact": "Significant competitive disadvantage",
            "mitigation": f"Urgent improvement initiatives for {kpi_name}"
        })

    # Trend-based risks
    growth_rate = trend_analysis.get('growth_rate', 0)
    volatility = trend_analysis.get('volatility', 0)

    if growth_rate < -20:
        risk_factors.append({
            "type": "trend_risk",
            "severity": "high",
            "description": f"{kpi_name} showing steep decline ({growth_rate:.1f}%)",
            "impact": "Potential business model issues",
            "mitigation": f"Investigate and address root causes of {kpi_name} decline"
        })

    if volatility > current_value * 0.3:  # High volatility relative to value
        risk_factors.append({
            "type": "volatility_risk",
            "severity": "medium",
            "description": f"{kpi_name} showing high volatility",
            "impact": "Unpredictable performance and planning difficulties",
            "mitigation": f"Implement more consistent {kpi_name} management processes"
        })

    # Data quality risks
    data_points = trend_analysis.get('data_points', 0)
    if data_points < 3:
        risk_factors.append({
            "type": "data_risk",
            "severity": "medium",
            "description": f"Insufficient historical data for {kpi_name}",
            "impact": "Limited ability to validate performance trends",
            "mitigation": f"Implement consistent {kpi_name} tracking and reporting"
        })

    return risk_factors


def calculate_analysis_confidence(historical_data: list[dict], benchmarks: dict[str, Any],
                                industry_context: dict[str, Any]) -> float:
    """
    Calculate confidence score for the KPI analysis.
    
    Args:
        historical_data: Historical data points
        benchmarks: Industry benchmark data
        industry_context: Industry context
        
    Returns:
        Confidence score (0.0 to 1.0)
    """
    confidence = 0.0

    # Data quality factors
    if historical_data and len(historical_data) >= 6:
        confidence += 0.3  # Good historical data
    elif historical_data and len(historical_data) >= 3:
        confidence += 0.2  # Adequate historical data
    elif historical_data:
        confidence += 0.1  # Some historical data

    # Benchmark quality factors
    if benchmarks:
        confidence += 0.3  # Benchmark data available
        if benchmarks.get('sample_size', 0) > 100:
            confidence += 0.1  # Large sample size
        if benchmarks.get('data_recency') == 'recent':
            confidence += 0.1  # Recent benchmark data

    # Industry context factors
    if industry_context.get('industry') != 'unknown':
        confidence += 0.2  # Known industry

    return min(confidence, 1.0)

"""
Market research integration tools for Business KPIs Orchestrator.
Adapts existing search tools with rate limiting, caching, and industry-specific capabilities.
"""

import time
import logging
from typing import Dict, List

from tools.search_tool import concise_google_search, search_indian_news

logger = logging.getLogger(__name__)


def market_size_validation_search(market_segment: str, market_size_type: str = "TAM") -> str:
    """
    Search for market size validation data from authoritative sources.
    
    Args:
        market_segment: The market segment to validate (e.g., "fintech", "edtech")
        market_size_type: Type of market size ("TAM", "SAM", "SOM")
        
    Returns:
        Market size validation data from authoritative sources
    """
    # Simple rate limiting
    time.sleep(0.5)
    
    # Generate market size validation queries
    validation_queries = [
        f"{market_segment} market size {market_size_type} 2024 Gartner",
        f"{market_segment} market research Forrester McKinsey",
        f"{market_segment} industry report market value"
    ]
    
    results = []
    for query in validation_queries:
        try:
            result = concise_google_search(query)
            if result and "fallback" not in result.lower():
                results.append(f"**Query: {query}**\n{result}")
        except Exception as e:
            logger.warning(f"Failed search '{query}': {e}")
            continue
    
    return "\n\n".join(results) if results else f"No market size validation data found for {market_segment} {market_size_type}"


def industry_benchmark_search(industry: str, kpi_name: str) -> str:
    """
    Search for industry benchmark data for specific KPIs.
    
    Args:
        industry: Industry sector (e.g., "SaaS", "e-commerce", "fintech")
        kpi_name: Name of the KPI to benchmark (e.g., "CAC", "churn rate", "conversion rate")
        
    Returns:
        Industry benchmark data for the specified KPI
    """
    # Simple rate limiting
    time.sleep(0.5)
    
    # Generate industry benchmark queries
    benchmark_queries = [
        f"{industry} {kpi_name} industry benchmark average",
        f"{industry} {kpi_name} industry standard typical range",
        f"{industry} companies {kpi_name} benchmark report"
    ]
    
    results = []
    for query in benchmark_queries:
        try:
            result = concise_google_search(query)
            if result and "fallback" not in result.lower():
                results.append(f"**Query: {query}**\n{result}")
        except Exception as e:
            logger.warning(f"Failed search '{query}': {e}")
            continue
    
    return "\n\n".join(results) if results else f"No benchmark data found for {kpi_name} in {industry} industry"


def industry_report_search(industry: str, report_type: str = "market_analysis") -> str:
    """
    Search for comprehensive industry reports and market intelligence.
    
    Args:
        industry: Industry sector to research
        report_type: Type of report ("market_analysis", "trends", "regulatory", "competitive")
        
    Returns:
        Industry report findings and market intelligence
    """
    # Simple rate limiting
    time.sleep(0.5)
    
    # Generate industry report queries based on type
    if report_type == "trends":
        report_queries = [
            f"{industry} industry trends 2024 emerging",
            f"{industry} market trends technology innovation"
        ]
    elif report_type == "regulatory":
        report_queries = [
            f"{industry} regulatory changes compliance 2024",
            f"{industry} industry regulations policy impact"
        ]
    elif report_type == "competitive":
        report_queries = [
            f"{industry} competitive landscape analysis",
            f"{industry} market competition report"
        ]
    else:  # market_analysis
        report_queries = [
            f"{industry} market analysis report 2024",
            f"{industry} industry overview market research"
        ]
    
    results = []
    for query in report_queries:
        try:
            result = concise_google_search(query)
            if result and "fallback" not in result.lower():
                results.append(f"**Query: {query}**\n{result}")
        except Exception as e:
            logger.warning(f"Failed search '{query}': {e}")
            continue
    
    return "\n\n".join(results) if results else f"No industry reports found for {industry} ({report_type})"


def kpi_validation_search(company_name: str, kpi_name: str, claimed_value: str) -> str:
    """
    Search to validate specific KPI claims against industry data.
    
    Args:
        company_name: Name of the company making the claim
        kpi_name: Name of the KPI being validated
        claimed_value: The claimed KPI value
        
    Returns:
        Validation data for the KPI claim
    """
    # Simple rate limiting
    time.sleep(0.5)
    
    # Generate KPI validation queries
    validation_queries = [
        f"{company_name} {kpi_name} performance metrics",
        f"{kpi_name} {claimed_value} industry comparison",
        f"{company_name} financial metrics {kpi_name}"
    ]
    
    results = []
    for query in validation_queries:
        try:
            result = concise_google_search(query)
            if result and "fallback" not in result.lower():
                results.append(f"**Query: {query}**\n{result}")
        except Exception as e:
            logger.warning(f"Failed search '{query}': {e}")
            continue
    
    # Also search Indian news for any mentions
    try:
        news_result = search_indian_news(f"{company_name} {kpi_name}")
        if news_result and "unavailable" not in news_result.lower():
            results.append(f"**News Coverage**: {news_result}")
    except Exception as e:
        logger.warning(f"Failed news search: {e}")
    
    return "\n\n".join(results) if results else f"No validation data found for {company_name}'s {kpi_name} claim of {claimed_value}"


def funding_validation_search(company_name: str, claimed_funding: str) -> str:
    """
    Search to validate funding claims and financial status.
    
    Args:
        company_name: Name of the company
        claimed_funding: Claimed funding amount or status
        
    Returns:
        Funding validation data from various sources
    """
    # Simple rate limiting
    time.sleep(0.5)
    
    # Generate funding validation queries
    funding_queries = [
        f"{company_name} funding {claimed_funding} series round",
        f"{company_name} investment valuation {claimed_funding}",
        f"{company_name} funding announcement {claimed_funding}"
    ]
    
    results = []
    for query in funding_queries:
        try:
            result = concise_google_search(query)
            if result and "fallback" not in result.lower():
                results.append(f"**Query: {query}**\n{result}")
        except Exception as e:
            logger.warning(f"Failed search '{query}': {e}")
            continue
    
    # Search Indian news for funding announcements
    try:
        news_result = search_indian_news(f"{company_name} funding {claimed_funding}")
        if news_result and "unavailable" not in news_result.lower():
            results.append(f"**News Coverage**: {news_result}")
    except Exception as e:
        logger.warning(f"Failed news search: {e}")
    
    return "\n\n".join(results) if results else f"No funding validation data found for {company_name}'s claim of {claimed_funding}"


def comprehensive_market_research(market_segment: str, research_focus: str = "comprehensive") -> str:
    """
    Perform comprehensive market research combining multiple search strategies.
    
    Args:
        market_segment: Market segment to research
        research_focus: Focus area ("comprehensive", "size", "trends", "competition")
        
    Returns:
        Comprehensive market research findings
    """
    results = {}
    
    try:
        # Market size validation
        if research_focus in ["comprehensive", "size"]:
            tam_result = market_size_validation_search(market_segment, "TAM")
            results["market_size"] = tam_result
        
        # Industry reports
        if research_focus in ["comprehensive", "trends"]:
            trends_result = industry_report_search(market_segment, "trends")
            results["industry_trends"] = trends_result
        
        # Competitive landscape
        if research_focus in ["comprehensive", "competition"]:
            competitive_result = industry_report_search(market_segment, "competitive")
            results["competitive_landscape"] = competitive_result
    
    except Exception as e:
        logger.error(f"Error in comprehensive market research: {e}")
        return f"Comprehensive market research failed for {market_segment}: {str(e)}"
    
    # Format consolidated results
    formatted_results = []
    for area, result in results.items():
        if result:
            formatted_results.append(f"## {area.replace('_', ' ').title()}\n\n{result}")
    
    return "\n\n---\n\n".join(formatted_results) if formatted_results else f"No comprehensive market research data found for {market_segment}"


# Export the market research tools
__all__ = [
    'market_size_validation_search',
    'industry_benchmark_search',
    'industry_report_search',
    'kpi_validation_search',
    'funding_validation_search',
    'comprehensive_market_research'
]


# Industry-specific research capabilities

# Industry sector mappings and specialized search strategies
INDUSTRY_SEARCH_STRATEGIES = {
    "fintech": {
        "keywords": ["financial technology", "digital payments", "blockchain", "cryptocurrency", "neobank", "regtech"],
        "regulatory_terms": ["PCI DSS", "KYC", "AML", "GDPR", "PSD2", "Basel III"],
        "sources": ["fintech news", "banking technology", "payments journal"],
        "kpi_focus": ["transaction volume", "user acquisition cost", "regulatory compliance cost"]
    },
    "healthtech": {
        "keywords": ["digital health", "telemedicine", "health informatics", "medical devices", "pharma tech"],
        "regulatory_terms": ["HIPAA", "FDA approval", "clinical trials", "medical device regulation", "health data privacy"],
        "sources": ["healthcare IT news", "medical device network", "digital health"],
        "kpi_focus": ["patient outcomes", "clinical efficacy", "regulatory approval time"]
    },
    "edtech": {
        "keywords": ["educational technology", "e-learning", "online education", "learning management", "educational software"],
        "regulatory_terms": ["FERPA", "COPPA", "accessibility compliance", "educational standards"],
        "sources": ["education technology", "elearning industry", "educational research"],
        "kpi_focus": ["student engagement", "learning outcomes", "teacher adoption rate"]
    },
    "saas": {
        "keywords": ["software as a service", "cloud computing", "enterprise software", "business applications"],
        "regulatory_terms": ["SOC 2", "ISO 27001", "data protection", "cloud security"],
        "sources": ["software industry", "cloud computing news", "enterprise tech"],
        "kpi_focus": ["monthly recurring revenue", "churn rate", "customer acquisition cost", "net revenue retention"]
    },
    "ecommerce": {
        "keywords": ["online retail", "digital commerce", "marketplace", "retail technology"],
        "regulatory_terms": ["consumer protection", "data privacy", "payment regulations", "tax compliance"],
        "sources": ["retail technology", "ecommerce news", "digital commerce"],
        "kpi_focus": ["conversion rate", "average order value", "customer lifetime value", "cart abandonment rate"]
    },
    "mobility": {
        "keywords": ["transportation technology", "ride sharing", "autonomous vehicles", "logistics tech"],
        "regulatory_terms": ["transportation regulations", "vehicle safety", "driver regulations", "emissions standards"],
        "sources": ["transportation technology", "mobility news", "automotive tech"],
        "kpi_focus": ["ride completion rate", "driver utilization", "safety metrics", "operational efficiency"]
    }
}

# Source credibility weights for different types of sources
SOURCE_CREDIBILITY_WEIGHTS = {
    "tier1_research": 1.0,  # Gartner, Forrester, McKinsey, BCG
    "tier2_research": 0.8,  # Industry-specific research firms
    "government": 0.9,      # Government reports and statistics
    "industry_association": 0.7,  # Industry association reports
    "major_news": 0.6,      # Major business news outlets
    "trade_publication": 0.5,  # Industry trade publications
    "company_reports": 0.4,  # Company annual reports, press releases
    "blog_opinion": 0.2,    # Blog posts, opinion pieces
    "unknown": 0.3          # Unknown or unverified sources
}

# Tier 1 research firms and authoritative sources
TIER1_SOURCES = [
    "gartner", "forrester", "mckinsey", "bcg", "bain", "deloitte", "pwc", "kpmg", "ey",
    "idc", "frost & sullivan", "ovum", "451 research"
]

GOVERNMENT_SOURCES = [
    "sec.gov", "treasury.gov", "federalreserve.gov", "census.gov", "bls.gov", "sba.gov",
    "europa.eu", "gov.uk", "rbi.org.in", "sebi.gov.in"
]

MAJOR_NEWS_SOURCES = [
    "reuters", "bloomberg", "wsj", "ft.com", "economist", "forbes", "techcrunch",
    "venturebeat", "crunchbase", "pitchbook"
]


def industry_specific_search(industry: str, search_type: str, query_context: str = "") -> str:
    """
    Perform industry-specific search using specialized strategies and keywords.
    
    Args:
        industry: Industry sector (e.g., "fintech", "healthtech", "edtech")
        search_type: Type of search ("market_analysis", "regulatory", "competitive", "trends")
        query_context: Additional context for the search query
        
    Returns:
        Industry-specific search results with enhanced relevance
    """
    industry_lower = industry.lower()
    
    # Get industry-specific configuration
    if industry_lower not in INDUSTRY_SEARCH_STRATEGIES:
        # Fallback to generic search
        return industry_report_search(industry, search_type)
    
    industry_config = INDUSTRY_SEARCH_STRATEGIES[industry_lower]
    
    # Build specialized queries based on industry and search type
    specialized_queries = []
    
    if search_type == "regulatory":
        for reg_term in industry_config["regulatory_terms"][:3]:
            specialized_queries.append(f"{industry} {reg_term} compliance requirements 2024")
            specialized_queries.append(f"{reg_term} impact {industry} industry")
    
    elif search_type == "competitive":
        for keyword in industry_config["keywords"][:2]:
            specialized_queries.append(f"{keyword} competitive landscape analysis")
            specialized_queries.append(f"{keyword} market leaders companies")
    
    elif search_type == "trends":
        for keyword in industry_config["keywords"][:2]:
            specialized_queries.append(f"{keyword} trends 2024 emerging technologies")
            specialized_queries.append(f"{keyword} future outlook predictions")
    
    else:  # market_analysis
        for keyword in industry_config["keywords"][:2]:
            specialized_queries.append(f"{keyword} market size analysis report")
            specialized_queries.append(f"{keyword} industry growth forecast")
    
    # Add query context if provided
    if query_context:
        specialized_queries = [f"{query} {query_context}" for query in specialized_queries]
    
    # Execute specialized searches
    results = []
    for query in specialized_queries[:4]:  # Limit to 4 queries for performance
        try:
            result = concise_google_search(query)
            if result and "fallback" not in result.lower():
                # Weight the result based on source credibility
                weighted_result = _apply_source_credibility_weighting(result, query)
                results.append(f"**Specialized Query: {query}**\n{weighted_result}")
        except Exception as e:
            logger.warning(f"Failed specialized search '{query}': {e}")
            continue
    
    return "\n\n".join(results) if results else f"No specialized search results found for {industry} {search_type}"


def regulatory_change_detection(industry: str, time_period: str = "2024") -> str:
    """
    Detect and analyze regulatory changes impacting specific industries.
    
    Args:
        industry: Industry sector to monitor for regulatory changes
        time_period: Time period to focus on (default: "2024")
        
    Returns:
        Analysis of regulatory changes and their potential impact
    """
    industry_lower = industry.lower()
    
    # Get industry-specific regulatory terms
    if industry_lower in INDUSTRY_SEARCH_STRATEGIES:
        regulatory_terms = INDUSTRY_SEARCH_STRATEGIES[industry_lower]["regulatory_terms"]
    else:
        regulatory_terms = ["regulation", "compliance", "policy changes"]
    
    # Build regulatory change detection queries
    regulatory_queries = []
    for reg_term in regulatory_terms[:3]:
        regulatory_queries.extend([
            f"{reg_term} changes {time_period} {industry}",
            f"new {reg_term} requirements {industry} {time_period}",
            f"{reg_term} updates impact {industry} companies"
        ])
    
    # Add general regulatory change queries
    regulatory_queries.extend([
        f"{industry} regulatory changes {time_period}",
        f"{industry} compliance requirements updates {time_period}",
        f"{industry} policy changes government {time_period}"
    ])
    
    results = []
    for query in regulatory_queries[:5]:  # Limit queries for performance
        try:
            result = concise_google_search(query)
            if result and "fallback" not in result.lower():
                # Apply higher credibility weighting for government sources
                weighted_result = _apply_source_credibility_weighting(result, query, boost_government=True)
                results.append(f"**Regulatory Query: {query}**\n{weighted_result}")
        except Exception as e:
            logger.warning(f"Failed regulatory search '{query}': {e}")
            continue
    
    if results:
        # Add impact assessment
        impact_assessment = _assess_regulatory_impact(industry, results)
        results.append(f"**Impact Assessment**\n{impact_assessment}")
        return "\n\n".join(results)
    else:
        return f"No regulatory changes detected for {industry} in {time_period}"


def source_credibility_analysis(search_results: str, query_context: str = "") -> str:
    """
    Analyze and weight search results based on source credibility.
    
    Args:
        search_results: Raw search results to analyze
        query_context: Context about the search query for better analysis
        
    Returns:
        Credibility analysis with weighted results and confidence scores
    """
    # Extract potential sources from search results
    sources_found = _extract_sources_from_results(search_results)
    
    # Calculate credibility scores
    credibility_analysis = []
    overall_credibility = 0.0
    source_count = 0
    
    for source, content in sources_found.items():
        credibility_score = _calculate_source_credibility(source)
        source_count += 1
        overall_credibility += credibility_score
        
        credibility_analysis.append(
            f"**Source: {source}**\n"
            f"Credibility Score: {credibility_score:.2f}\n"
            f"Content: {content[:200]}...\n"
        )
    
    # Calculate overall confidence
    if source_count > 0:
        avg_credibility = overall_credibility / source_count
        confidence_level = _determine_confidence_level(avg_credibility, source_count)
    else:
        avg_credibility = 0.0
        confidence_level = "Low"
    
    # Format analysis results
    analysis_summary = (
        f"**Source Credibility Analysis**\n"
        f"Sources Analyzed: {source_count}\n"
        f"Average Credibility Score: {avg_credibility:.2f}\n"
        f"Overall Confidence Level: {confidence_level}\n\n"
        f"**Individual Source Analysis:**\n"
    )
    
    return analysis_summary + "\n".join(credibility_analysis)


def _apply_source_credibility_weighting(search_result: str, query: str, boost_government: bool = False) -> str:
    """Apply credibility weighting to search results."""
    # Extract potential sources from the result
    result_lower = search_result.lower()
    
    # Check for high-credibility sources
    credibility_indicators = []
    
    # Check for Tier 1 research sources
    for source in TIER1_SOURCES:
        if source in result_lower:
            credibility_indicators.append(f"[HIGH CREDIBILITY: {source.upper()}]")
            break
    
    # Check for government sources
    for source in GOVERNMENT_SOURCES:
        if source in result_lower:
            weight = "[VERY HIGH CREDIBILITY: GOVERNMENT SOURCE]" if boost_government else "[HIGH CREDIBILITY: GOVERNMENT]"
            credibility_indicators.append(weight)
            break
    
    # Check for major news sources
    for source in MAJOR_NEWS_SOURCES:
        if source in result_lower:
            credibility_indicators.append(f"[MEDIUM CREDIBILITY: {source.upper()}]")
            break
    
    # Add credibility indicators to the result
    if credibility_indicators:
        return f"{' '.join(credibility_indicators)} {search_result}"
    else:
        return f"[CREDIBILITY: UNVERIFIED] {search_result}"


def _extract_sources_from_results(search_results: str) -> Dict[str, str]:
    """Extract potential sources and their content from search results."""
    sources = {}
    
    # Simple extraction based on common patterns
    lines = search_results.split('\n')
    current_source = "Unknown"
    current_content = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line contains a source indicator
        line_lower = line.lower()
        source_found = None
        
        for source in TIER1_SOURCES + [s.replace('.', '') for s in GOVERNMENT_SOURCES] + MAJOR_NEWS_SOURCES:
            if source in line_lower:
                source_found = source
                break
        
        if source_found:
            if current_content:
                sources[current_source] = current_content
            current_source = source_found
            current_content = line
        else:
            current_content += " " + line
    
    # Add the last source
    if current_content:
        sources[current_source] = current_content
    
    return sources


def _calculate_source_credibility(source: str) -> float:
    """Calculate credibility score for a source."""
    source_lower = source.lower()
    
    # Check against known high-credibility sources
    if any(tier1 in source_lower for tier1 in TIER1_SOURCES):
        return SOURCE_CREDIBILITY_WEIGHTS["tier1_research"]
    
    if any(gov in source_lower for gov in GOVERNMENT_SOURCES):
        return SOURCE_CREDIBILITY_WEIGHTS["government"]
    
    if any(news in source_lower for news in MAJOR_NEWS_SOURCES):
        return SOURCE_CREDIBILITY_WEIGHTS["major_news"]
    
    # Check for industry associations or trade publications
    if any(term in source_lower for term in ["association", "institute", "foundation"]):
        return SOURCE_CREDIBILITY_WEIGHTS["industry_association"]
    
    if any(term in source_lower for term in ["journal", "publication", "magazine"]):
        return SOURCE_CREDIBILITY_WEIGHTS["trade_publication"]
    
    # Default to unknown credibility
    return SOURCE_CREDIBILITY_WEIGHTS["unknown"]


def _determine_confidence_level(avg_credibility: float, source_count: int) -> str:
    """Determine overall confidence level based on credibility and source count."""
    if avg_credibility >= 0.8 and source_count >= 3:
        return "Very High"
    elif avg_credibility >= 0.6 and source_count >= 2:
        return "High"
    elif avg_credibility >= 0.4 or source_count >= 3:
        return "Medium"
    elif avg_credibility >= 0.2 or source_count >= 1:
        return "Low"
    else:
        return "Very Low"


def _assess_regulatory_impact(industry: str, regulatory_results: List[str]) -> str:
    """Assess the potential impact of regulatory changes on an industry."""
    # Simple impact assessment based on keyword analysis
    impact_keywords = {
        "high_impact": ["mandatory", "required", "compliance deadline", "penalty", "fine", "enforcement"],
        "medium_impact": ["recommended", "guidance", "best practice", "voluntary", "phased implementation"],
        "low_impact": ["proposed", "under review", "consultation", "draft", "preliminary"]
    }
    
    impact_scores = {"high": 0, "medium": 0, "low": 0}
    
    combined_text = " ".join(regulatory_results).lower()
    
    for impact_level, keywords in impact_keywords.items():
        for keyword in keywords:
            if keyword in combined_text:
                impact_level_key = impact_level.split("_")[0]
                impact_scores[impact_level_key] += 1
    
    # Determine overall impact level
    if impact_scores["high"] >= 2:
        overall_impact = "High"
        impact_description = "Significant regulatory changes requiring immediate attention and compliance measures."
    elif impact_scores["medium"] >= 2 or impact_scores["high"] >= 1:
        overall_impact = "Medium"
        impact_description = "Moderate regulatory changes that may require operational adjustments."
    else:
        overall_impact = "Low"
        impact_description = "Minor or proposed regulatory changes with limited immediate impact."
    
    return (
        f"Overall Impact Level: {overall_impact}\n"
        f"Assessment: {impact_description}\n"
        f"Impact Indicators - High: {impact_scores['high']}, Medium: {impact_scores['medium']}, Low: {impact_scores['low']}"
    )


# Update the __all__ export list
__all__ = [
    'market_size_validation_search',
    'industry_benchmark_search',
    'industry_report_search',
    'kpi_validation_search',
    'funding_validation_search',
    'comprehensive_market_research',
    'industry_specific_search',
    'regulatory_change_detection',
    'source_credibility_analysis'
]
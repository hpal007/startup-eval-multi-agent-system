"""
Competitor-specific search tools for competitive analysis.
Adapts existing search tools for competitor research patterns with rate limiting and error handling.
"""

import logging
import time
from functools import wraps

import requests

from tools.search_tool import (
    comprehensive_founder_search,
    concise_google_search,
    search_indian_news,
)

logger = logging.getLogger(__name__)


class CompetitorSearchError(Exception):
    """Custom exception for competitor search errors."""

    pass


class RateLimiter:
    """Simple rate limiter for search operations."""

    def __init__(self, max_requests_per_minute: int = 30):
        self.max_requests = max_requests_per_minute
        self.requests = []

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]

        if len(self.requests) >= self.max_requests:
            # Wait until the oldest request is more than 1 minute old
            sleep_time = 60 - (now - self.requests[0]) + 1
            if sleep_time > 0:
                logger.info(f"Rate limit reached. Waiting {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)

        self.requests.append(now)


# Global rate limiter instance
rate_limiter = RateLimiter(max_requests_per_minute=20)  # Conservative limit


def with_rate_limiting(func):
    """Decorator to add rate limiting to search functions."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        rate_limiter.wait_if_needed()
        return func(*args, **kwargs)

    return wrapper


def with_error_handling(func):
    """Decorator to add comprehensive error handling to search functions."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Search attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Search failed after {max_retries} attempts: {e}")
                    return f"Search failed after multiple attempts: {e!s}"
            except Exception as e:
                logger.error(f"Unexpected error in search: {e}")
                return f"Search failed due to unexpected error: {e!s}"

    return wrapper


@with_rate_limiting
@with_error_handling
def competitor_market_search(
    market_segment: str, competitor_type: str = "direct"
) -> str:
    """
    Search for competitors in a specific market segment.

    Args:
        market_segment: The market segment to search (e.g., "fintech", "edtech", "healthtech")
        competitor_type: Type of competitors to find ("direct", "indirect", "substitute")

    Returns:
        Formatted search results with competitor information
    """
    # Generate competitor-specific search queries
    search_queries = _generate_competitor_search_queries(
        market_segment, competitor_type
    )

    results = []
    for query in search_queries[:3]:  # Limit to top 3 queries to manage rate limits
        try:
            result = concise_google_search(query)
            if result and "fallback" not in result.lower():
                results.append(f"**Query: {query}**\n{result}")
        except Exception as e:
            logger.warning(f"Failed to execute query '{query}': {e}")
            continue

    if results:
        return "\n\n".join(results)
    else:
        return f"No competitor information found for {market_segment} market segment"


@with_rate_limiting
@with_error_handling
def competitor_intelligence_search(competitor_name: str) -> str:
    """
    Gather comprehensive intelligence on a specific competitor.

    Args:
        competitor_name: Name of the competitor company

    Returns:
        Formatted intelligence report with competitor details
    """
    intelligence_areas = [
        "funding latest round",
        "product features",
        "market positioning",
        "founders team",
        "partnerships news",
    ]

    results = {}

    for area in intelligence_areas:
        query = f"{competitor_name} {area}"
        try:
            result = concise_google_search(query)
            if result and "fallback" not in result.lower():
                results[area] = result
        except Exception as e:
            logger.warning(
                f"Failed intelligence search for {competitor_name} {area}: {e}"
            )
            results[area] = f"Search failed: {e!s}"

    # Also search for news coverage
    try:
        news_result = search_indian_news(competitor_name)
        if news_result:
            results["news_coverage"] = news_result
    except Exception as e:
        logger.warning(f"Failed news search for {competitor_name}: {e}")
        results["news_coverage"] = f"News search failed: {e!s}"

    # Format results
    formatted_results = []
    for area, result in results.items():
        formatted_results.append(f"**{area.replace('_', ' ').title()}**:\n{result}")

    return "\n\n".join(formatted_results)


@with_rate_limiting
@with_error_handling
def competitor_validation_search(competitor_name: str, claimed_advantage: str) -> str:
    """
    Search to validate specific competitive advantage claims.

    Args:
        competitor_name: Name of the competitor
        claimed_advantage: The competitive advantage claim to validate

    Returns:
        Search results that help validate or contradict the claim
    """
    # Generate validation-specific queries
    validation_queries = [
        f"{competitor_name} {claimed_advantage}",
        f"{competitor_name} vs competitors {claimed_advantage}",
        f"{competitor_name} customer reviews {claimed_advantage}",
        f"{competitor_name} disadvantages limitations",
    ]

    results = []
    for query in validation_queries:
        try:
            result = concise_google_search(query)
            if result and "fallback" not in result.lower():
                results.append(f"**Validation Query: {query}**\n{result}")
        except Exception as e:
            logger.warning(f"Failed validation search '{query}': {e}")
            continue

    if results:
        return "\n\n".join(results)
    else:
        return f"No validation information found for {competitor_name}'s claimed advantage: {claimed_advantage}"


@with_rate_limiting
@with_error_handling
def competitor_funding_search(competitor_name: str) -> str:
    """
    Search for competitor funding information and financial status.

    Args:
        competitor_name: Name of the competitor company

    Returns:
        Funding and financial information about the competitor
    """
    funding_queries = [
        f"{competitor_name} funding series latest 2024",
        f"{competitor_name} valuation investment",
        f"{competitor_name} revenue growth financial",
        f"{competitor_name} investors funding round",
    ]

    results = []
    for query in funding_queries:
        try:
            result = concise_google_search(query)
            if result and "fallback" not in result.lower():
                results.append(f"**{query}**: {result}")
        except Exception as e:
            logger.warning(f"Failed funding search '{query}': {e}")
            continue

    # Also search Indian news for funding announcements
    try:
        news_result = search_indian_news(f"{competitor_name} funding")
        if news_result and "unavailable" not in news_result.lower():
            results.append(f"**Indian News Coverage**: {news_result}")
    except Exception as e:
        logger.warning(f"Failed Indian news funding search for {competitor_name}: {e}")

    if results:
        return "\n\n".join(results)
    else:
        return f"No funding information found for {competitor_name}"


@with_rate_limiting
@with_error_handling
def competitor_leadership_search(competitor_name: str) -> str:
    """
    Search for competitor leadership team information.
    Adapts comprehensive_founder_search for competitor leadership research.

    Args:
        competitor_name: Name of the competitor company

    Returns:
        Information about competitor's leadership team
    """
    # First try to find founder names
    founder_search_queries = [
        f"{competitor_name} founder CEO",
        f"{competitor_name} founding team",
        f"{competitor_name} leadership team executives",
    ]

    leadership_info = []

    for query in founder_search_queries:
        try:
            result = concise_google_search(query)
            if result and "fallback" not in result.lower():
                leadership_info.append(f"**{query}**: {result}")
        except Exception as e:
            logger.warning(f"Failed leadership search '{query}': {e}")
            continue

    # Try to extract founder names and use comprehensive search
    # This is a simplified approach - in practice, you'd parse the results to extract names
    try:
        founder_result = comprehensive_founder_search(f"{competitor_name} founder")
        if founder_result:
            leadership_info.append(
                f"**Comprehensive Leadership Search**: {founder_result}"
            )
    except Exception as e:
        logger.warning(
            f"Failed comprehensive leadership search for {competitor_name}: {e}"
        )

    if leadership_info:
        return "\n\n".join(leadership_info)
    else:
        return f"No leadership information found for {competitor_name}"


def _generate_competitor_search_queries(
    market_segment: str, competitor_type: str
) -> list[str]:
    """
    Generate targeted search queries for competitor discovery.

    Args:
        market_segment: The market segment to search
        competitor_type: Type of competitors ("direct", "indirect", "substitute")

    Returns:
        List of search queries optimized for competitor discovery
    """
    base_queries = []

    if competitor_type == "direct":
        base_queries = [
            f"{market_segment} startups companies 2024",
            f"{market_segment} competitors market leaders",
            f"{market_segment} software platforms tools",
            f"{market_segment} solutions providers India",
            f"top {market_segment} companies funding",
        ]
    elif competitor_type == "indirect":
        base_queries = [
            f"alternative solutions {market_segment}",
            f"different approaches {market_segment} problem",
            f"{market_segment} adjacent markets",
            f"substitute products {market_segment}",
            f"competing technologies {market_segment}",
        ]
    elif competitor_type == "substitute":
        base_queries = [
            f"alternatives to {market_segment}",
            f"traditional solutions {market_segment}",
            f"manual processes {market_segment}",
            f"existing tools {market_segment} market",
            f"legacy systems {market_segment}",
        ]
    else:
        # Default to comprehensive search
        base_queries = [
            f"{market_segment} companies startups",
            f"{market_segment} market players",
            f"{market_segment} industry competitors",
        ]

    return base_queries


@with_rate_limiting
@with_error_handling
def batch_competitor_search(
    competitor_names: list[str], search_type: str = "basic"
) -> str:
    """
    Perform batch search for multiple competitors with rate limiting.

    Args:
        competitor_names: List of competitor names to search
        search_type: Type of search ("basic", "intelligence", "funding")

    Returns:
        Consolidated search results for all competitors
    """
    if len(competitor_names) > 10:
        logger.warning(
            f"Batch search limited to 10 competitors, received {len(competitor_names)}"
        )
        competitor_names = competitor_names[:10]

    results = {}

    for competitor in competitor_names:
        try:
            if search_type == "intelligence":
                result = competitor_intelligence_search(competitor)
            elif search_type == "funding":
                result = competitor_funding_search(competitor)
            else:  # basic
                result = concise_google_search(f"{competitor} company profile")

            results[competitor] = result

        except Exception as e:
            logger.error(f"Failed batch search for {competitor}: {e}")
            results[competitor] = f"Search failed: {e!s}"

    # Format consolidated results
    formatted_results = []
    for competitor, result in results.items():
        formatted_results.append(f"## {competitor}\n\n{result}")

    return "\n\n---\n\n".join(formatted_results)

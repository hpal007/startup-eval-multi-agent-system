"""
Search tool for founder profile verification.
Integrates with real search APIs for comprehensive founder verification.
"""

import logging

import requests

from utils.configs import config

logger = logging.getLogger(__name__)


class SearchAPIError(Exception):
    """Custom exception for search API errors."""

    pass


def concise_google_search(query: str) -> str:
    """
    Perform real Google search using Google Custom Search API.
    Falls back to simulated search if Google API is unavailable.

    Args:
        query: Search query string

    Returns:
        Search result text from Google API or fallback simulation
    """
    # Try Google Custom Search API first
    google_result = _google_custom_search(query)
    if google_result:
        return google_result

    # Fallback to DuckDuckGo (no API key required) for basic results
    duckduckgo_result = _duckduckgo_search(query)
    if duckduckgo_result:
        return duckduckgo_result

    # Final fallback to simulated search for development
    logger.warning(
        f"Google Search API unavailable for query: {query}. Using fallback simulation."
    )
    return _fallback_simulated_search(query)


def comprehensive_founder_search(founder_name: str) -> str:
    """
    Perform comprehensive search for founder using multiple sources.

    Args:
        founder_name: Full name of the founder

    Returns:
        Formatted string with search results from different sources
    """
    results = {}

    # Google search for general information
    results["google_search"] = concise_google_search(f"{founder_name} founder startup")

    # News search for media coverage
    results["news_coverage"] = search_indian_news(founder_name)

    # India-specific searches
    results["india_ecosystem"] = concise_google_search(
        f"{founder_name} startup india ecosystem"
    )
    results["education_background"] = concise_google_search(
        f"{founder_name} IIT IIM education"
    )
    results["professional_background"] = concise_google_search(
        f"{founder_name} linkedin professional"
    )

    # Format results for ADK agent consumption
    formatted_results = []
    for source, result in results.items():
        formatted_results.append(f"**{source.replace('_', ' ').title()}**: {result}")

    return "\n\n".join(formatted_results)


def _google_custom_search(query: str) -> str | None:
    """
    Search using Google Custom Search API.

    Requires:
    - GOOGLE_SEARCH_API_KEY environment variable
    - GOOGLE_SEARCH_ENGINE_ID environment variable

    Get these from: https://developers.google.com/custom-search/v1/introduction
    """

    api_key = config.get_config_value("GOOGLE_SEARCH_API_KEY")
    search_engine_id = config.get_config_value("GOOGLE_SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        logger.info(
            "Google Custom Search API credentials not found. Skipping Google search."
        )
        return None

    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": query,
            "num": 5,  # Number of results
            "safe": "active",
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Extract and format search results
        results = []
        if "items" in data:
            for item in data["items"][:3]:  # Top 3 results
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                results.append(f"{title}: {snippet}")

        if results:
            return " | ".join(results)
        else:
            return (
                f"Google search completed for '{query}' but no relevant results found."
            )

    except requests.RequestException as e:
        logger.error(f"Google Custom Search API error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in Google search: {e}")
        return None


def search_indian_news(founder_name: str) -> str:
    """
    Search Indian news sources for founder mentions using News API.

    Requires:
    - NEWS_API_KEY environment variable (free 500 requests/day)

    Get this from: https://newsapi.org/
    """

    api_key = config.get_config_value("NEWS_API_KEY")

    if not api_key or api_key == "your_news_api_key_here":
        logger.info("News API key not found. Skipping news search.")
        return f"News search unavailable for {founder_name} - API key not configured"

    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": f'"{founder_name}" AND (startup OR entrepreneur OR founder OR CEO)',
            "sources": "the-times-of-india,economic-times",
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": 5,
            "apiKey": api_key,
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Extract and format news results
        results = []
        if data.get("articles") and len(data["articles"]) > 0:
            for article in data["articles"][:3]:  # Top 3 articles
                title = article.get("title", "")
                description = article.get("description", "")
                source = article.get("source", {}).get("name", "")
                if title and description:
                    results.append(f"{source}: {title} - {description}")

        if results:
            return " | ".join(results)
        else:
            # Try broader search if no results
            params["q"] = f"{founder_name} startup india"
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get("articles") and len(data["articles"]) > 0:
                article = data["articles"][0]
                title = article.get("title", "")
                description = article.get("description", "")
                return f"Broader search: {title} - {description}"

            return f"No news coverage found for {founder_name} in major Indian publications"

    except requests.RequestException as e:
        logger.error(f"News API error: {e}")
        return f"News search failed for {founder_name} - API error"
    except Exception as e:
        logger.error(f"Unexpected error in news search: {e}")
        return f"News search failed for {founder_name} - unexpected error"


def _duckduckgo_search(query: str) -> str | None:
    """
    Search using DuckDuckGo Instant Answer API (no API key required).

    Note: This is limited but doesn't require API keys.
    """
    try:
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Extract relevant information
        results = []

        # Abstract (main answer)
        if data.get("Abstract"):
            results.append(f"Summary: {data['Abstract']}")

        # Related topics
        if data.get("RelatedTopics"):
            for topic in data["RelatedTopics"][:2]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append(f"Related: {topic['Text']}")

        if results:
            return " | ".join(results)
        else:
            return f"DuckDuckGo search completed for '{query}' but no structured results found."

    except requests.RequestException as e:
        logger.error(f"DuckDuckGo search error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in DuckDuckGo search: {e}")
        return None


def _fallback_simulated_search(query: str) -> str:
    """
    Fallback simulated search for development when APIs are unavailable.
    """
    query_lower = query.lower()

    # Simplified fallback responses
    fallback_responses = {
        "linkedin": "LinkedIn profiles found but require direct access for verification.",
        "patent": "Patent database search requires specialized access for detailed verification.",
        "professional": "Professional background information available through various sources.",
        "company": "Company registration and business information may be available through official databases.",
        "startup": "Startup information typically limited for early-stage companies.",
    }

    for keyword, response in fallback_responses.items():
        if keyword in query_lower:
            return f"Fallback search for '{query}': {response}"

    return f"Fallback search completed for '{query}'. Real API access recommended for comprehensive verification."


def search_linkedin_profile(name: str) -> str:
    """
    Search for LinkedIn profiles (requires LinkedIn API access).

    Note: LinkedIn API has strict access requirements.
    This is a placeholder for future implementation.
    """
    # LinkedIn API implementation would go here
    # Requires LinkedIn Developer Program access
    return (
        f"LinkedIn search for '{name}' requires LinkedIn API access (not implemented)."
    )


def search_patent_databases(inventor_name: str) -> str:
    """
    Search patent databases for inventor information.

    Could integrate with:
    - USPTO API
    - Google Patents API
    - WIPO Global Brand Database
    """
    # Patent database API implementation would go here
    return f"Patent search for '{inventor_name}' requires patent database API access (not implemented)."


def search_company_registrations(company_name: str) -> str:
    """
    Search company registration databases.

    Could integrate with:
    - OpenCorporates API
    - SEC EDGAR database
    - Local business registration APIs
    """
    # Company registration API implementation would go here
    return f"Company registration search for '{company_name}' requires business database API access (not implemented)."

"""
Market validation tools for TAM/SAM/SOM validation and source credibility assessment.
"""

import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class SourceCredibilityWeights:
    """Source credibility weighting system for market research validation."""

    TIER_1_SOURCES = {
        'gartner': 0.95,
        'forrester': 0.95,
        'mckinsey': 0.95,
        'bain': 0.90,
        'bcg': 0.90,
        'deloitte': 0.85,
        'pwc': 0.85,
        'kpmg': 0.85,
        'ey': 0.85,
        'idc': 0.90,
        'frost': 0.85,
        'grand view research': 0.80,
        'statista': 0.75
    }

    TIER_2_SOURCES = {
        'bloomberg': 0.80,
        'reuters': 0.80,
        'wall street journal': 0.75,
        'financial times': 0.75,
        'harvard business review': 0.80,
        'mit technology review': 0.75,
        'techcrunch': 0.60,
        'venturebeat': 0.55,
        'crunchbase': 0.65,
        'pitchbook': 0.75,
        'cb insights': 0.70
    }

    TIER_3_SOURCES = {
        'industry association': 0.65,
        'trade publication': 0.60,
        'company report': 0.55,
        'analyst report': 0.60,
        'government data': 0.85,
        'sec filing': 0.80,
        'earnings call': 0.70
    }

    @classmethod
    def get_source_credibility(cls, source_text: str) -> float:
        """
        Get credibility score for a source based on its text content.
        
        Args:
            source_text: Text containing source information
            
        Returns:
            Credibility score between 0 and 1
        """
        source_lower = source_text.lower()

        # Check Tier 1 sources
        for source, weight in cls.TIER_1_SOURCES.items():
            if source in source_lower:
                return weight

        # Check Tier 2 sources
        for source, weight in cls.TIER_2_SOURCES.items():
            if source in source_lower:
                return weight

        # Check Tier 3 sources
        for source, weight in cls.TIER_3_SOURCES.items():
            if source in source_lower:
                return weight

        # Default credibility for unknown sources
        return 0.30


def calculate_market_variance(claimed_value: float, market_estimate: float) -> dict[str, float]:
    """
    Calculate variance between startup claims and market estimates.
    
    Args:
        claimed_value: Value claimed by the startup
        market_estimate: Market estimate from authoritative sources
        
    Returns:
        Dictionary containing variance calculations
    """
    if claimed_value <= 0 or market_estimate <= 0:
        return {
            'variance_percentage': 0.0,
            'variance_ratio': 0.0,
            'absolute_difference': 0.0,
            'error': 'Invalid values: both claimed_value and market_estimate must be positive'
        }

    # Calculate percentage variance
    variance_percentage = ((claimed_value - market_estimate) / market_estimate) * 100

    # Calculate variance ratio
    variance_ratio = claimed_value / market_estimate

    # Calculate absolute difference
    absolute_difference = abs(claimed_value - market_estimate)

    return {
        'variance_percentage': round(variance_percentage, 2),
        'variance_ratio': round(variance_ratio, 2),
        'absolute_difference': round(absolute_difference, 2),
        'overestimation': claimed_value > market_estimate,
        'underestimation': claimed_value < market_estimate
    }


def assess_data_recency(source_date: str, current_date: str | None = None) -> dict[str, any]:
    """
    Assess the recency of market data for confidence scoring.
    
    Args:
        source_date: Date string from the source (various formats supported)
        current_date: Current date string (defaults to today)
        
    Returns:
        Dictionary containing recency assessment
    """
    if current_date is None:
        current_date = datetime.now().strftime('%Y-%m-%d')

    try:
        # Parse source date (support multiple formats)
        source_dt = _parse_date_string(source_date)
        current_dt = _parse_date_string(current_date)

        if source_dt is None:
            return {
                'recency_score': 0.0,
                'age_in_days': None,
                'age_category': 'unknown',
                'error': f'Could not parse source date: {source_date}'
            }

        # Calculate age in days
        age_days = (current_dt - source_dt).days

        # Calculate recency score
        if age_days <= 90:  # 3 months
            recency_score = 1.0
            age_category = 'very_recent'
        elif age_days <= 365:  # 1 year
            recency_score = 0.8
            age_category = 'recent'
        elif age_days <= 730:  # 2 years
            recency_score = 0.6
            age_category = 'moderately_recent'
        elif age_days <= 1095:  # 3 years
            recency_score = 0.4
            age_category = 'somewhat_dated'
        else:
            recency_score = 0.2
            age_category = 'outdated'

        return {
            'recency_score': recency_score,
            'age_in_days': age_days,
            'age_category': age_category,
            'source_year': source_dt.year,
            'current_year': current_dt.year
        }

    except Exception as e:
        logger.error(f"Error assessing data recency: {e}")
        return {
            'recency_score': 0.0,
            'age_in_days': None,
            'age_category': 'error',
            'error': str(e)
        }


def calculate_confidence_score(
    source_credibility: float,
    data_recency_score: float,
    methodology_alignment: float,
    multiple_source_confirmation: bool = False
) -> dict[str, float]:
    """
    Calculate overall confidence score for market validation.
    
    Args:
        source_credibility: Credibility score of the source (0-1)
        data_recency_score: Recency score of the data (0-1)
        methodology_alignment: Alignment score of methodologies (0-1)
        multiple_source_confirmation: Whether multiple sources confirm the data
        
    Returns:
        Dictionary containing confidence calculations
    """
    # Weights for confidence calculation
    CREDIBILITY_WEIGHT = 0.40
    RECENCY_WEIGHT = 0.30
    METHODOLOGY_WEIGHT = 0.20
    CONFIRMATION_WEIGHT = 0.10

    # Calculate base confidence score
    base_confidence = (
        source_credibility * CREDIBILITY_WEIGHT +
        data_recency_score * RECENCY_WEIGHT +
        methodology_alignment * METHODOLOGY_WEIGHT
    )

    # Add confirmation bonus
    confirmation_bonus = CONFIRMATION_WEIGHT if multiple_source_confirmation else 0

    # Final confidence score
    confidence_score = min(base_confidence + confirmation_bonus, 1.0)

    return {
        'confidence_score': round(confidence_score, 3),
        'base_confidence': round(base_confidence, 3),
        'confirmation_bonus': confirmation_bonus,
        'component_scores': {
            'source_credibility': source_credibility,
            'data_recency': data_recency_score,
            'methodology_alignment': methodology_alignment,
            'multiple_source_confirmation': multiple_source_confirmation
        }
    }


def identify_discrepancy_flags(
    tam_variance: float | None = None,
    sam_variance: float | None = None,
    som_variance: float | None = None,
    variance_threshold: float = 20.0
) -> list[str]:
    """
    Identify discrepancy flags based on variance analysis.
    
    Args:
        tam_variance: TAM variance percentage
        sam_variance: SAM variance percentage  
        som_variance: SOM variance percentage
        variance_threshold: Threshold for flagging significant variances
        
    Returns:
        List of discrepancy flags
    """
    flags = []

    # Check TAM variance
    if tam_variance is not None:
        if abs(tam_variance) > variance_threshold:
            if tam_variance > 0:
                flags.append(f"TAM overestimated by {abs(tam_variance):.1f}%")
            else:
                flags.append(f"TAM underestimated by {abs(tam_variance):.1f}%")

        if abs(tam_variance) > 50:
            flags.append("TAM variance exceeds 50% - requires detailed review")

    # Check SAM variance
    if sam_variance is not None:
        if abs(sam_variance) > variance_threshold:
            if sam_variance > 0:
                flags.append(f"SAM overestimated by {abs(sam_variance):.1f}%")
            else:
                flags.append(f"SAM underestimated by {abs(sam_variance):.1f}%")

    # Check SOM variance
    if som_variance is not None:
        if abs(som_variance) > variance_threshold:
            if som_variance > 0:
                flags.append(f"SOM overestimated by {abs(som_variance):.1f}%")
            else:
                flags.append(f"SOM underestimated by {abs(som_variance):.1f}%")

    # Check for logical inconsistencies
    if tam_variance is not None and sam_variance is not None:
        if tam_variance < sam_variance - 10:  # SAM should not be much higher variance than TAM
            flags.append("SAM variance significantly higher than TAM - potential methodology issue")

    if sam_variance is not None and som_variance is not None:
        if sam_variance < som_variance - 10:  # SOM should not be much higher variance than SAM
            flags.append("SOM variance significantly higher than SAM - potential methodology issue")

    # Overall assessment
    variances = [v for v in [tam_variance, sam_variance, som_variance] if v is not None]
    if variances:
        avg_variance = sum(abs(v) for v in variances) / len(variances)
        if avg_variance > 30:
            flags.append("Average market size variance exceeds 30% - high validation risk")

    return flags


def extract_market_data_from_search(search_results: str, market_type: str = "TAM") -> dict[str, any]:
    """
    Extract market size data from search results using pattern matching.
    
    Args:
        search_results: Text from search results
        market_type: Type of market data to extract (TAM, SAM, SOM)
        
    Returns:
        Dictionary containing extracted market data
    """
    # Patterns for extracting market size data
    patterns = {
        'market_size': [
            r'market size.*?(\$[\d,.]+ (?:billion|million|trillion))',
            r'(\$[\d,.]+ (?:billion|million|trillion)).*?market',
            r'valued at.*?(\$[\d,.]+ (?:billion|million|trillion))',
            r'worth.*?(\$[\d,.]+ (?:billion|million|trillion))'
        ],
        'growth_rate': [
            r'grow(?:th|ing).*?(\d+\.?\d*%)',
            r'CAGR.*?(\d+\.?\d*%)',
            r'compound annual growth rate.*?(\d+\.?\d*%)'
        ],
        'year': [
            r'(20\d{2})',
            r'by (20\d{2})',
            r'in (20\d{2})'
        ],
        'source': [
            r'according to ([^,.\n]+)',
            r'([A-Z][a-z]+ (?:Research|Analytics|Consulting|Group))',
            r'(Gartner|Forrester|McKinsey|IDC|Frost & Sullivan)'
        ]
    }

    extracted_data = {
        'market_sizes': [],
        'growth_rates': [],
        'years': [],
        'sources': [],
        'confidence': 0.0
    }

    try:
        # Extract market sizes
        for pattern in patterns['market_size']:
            matches = re.findall(pattern, search_results, re.IGNORECASE)
            for match in matches:
                size_value = _parse_market_size(match)
                if size_value:
                    extracted_data['market_sizes'].append({
                        'raw_text': match,
                        'value_billions': size_value,
                        'currency': 'USD'
                    })

        # Extract growth rates
        for pattern in patterns['growth_rate']:
            matches = re.findall(pattern, search_results, re.IGNORECASE)
            extracted_data['growth_rates'].extend(matches)

        # Extract years
        for pattern in patterns['year']:
            matches = re.findall(pattern, search_results)
            extracted_data['years'].extend([int(year) for year in matches])

        # Extract sources
        for pattern in patterns['source']:
            matches = re.findall(pattern, search_results, re.IGNORECASE)
            extracted_data['sources'].extend(matches)

        # Calculate confidence based on data completeness
        confidence_factors = [
            len(extracted_data['market_sizes']) > 0,
            len(extracted_data['sources']) > 0,
            len(extracted_data['years']) > 0,
            any('gartner' in s.lower() or 'forrester' in s.lower() for s in extracted_data['sources'])
        ]

        extracted_data['confidence'] = sum(confidence_factors) / len(confidence_factors)

        # Remove duplicates
        extracted_data['growth_rates'] = list(set(extracted_data['growth_rates']))
        extracted_data['years'] = sorted(list(set(extracted_data['years'])))
        extracted_data['sources'] = list(set(extracted_data['sources']))

    except Exception as e:
        logger.error(f"Error extracting market data: {e}")
        extracted_data['error'] = str(e)

    return extracted_data


def _parse_date_string(date_str: str) -> datetime | None:
    """Parse various date string formats."""
    date_formats = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y-%m',
        '%Y',
        '%B %Y',
        '%b %Y',
        '%B %d, %Y',
        '%b %d, %Y'
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue

    # Try to extract year from string
    year_match = re.search(r'20\d{2}', date_str)
    if year_match:
        try:
            return datetime(int(year_match.group()), 1, 1)
        except ValueError:
            pass

    return None


def _parse_market_size(size_str: str) -> float | None:
    """Parse market size string and convert to billions USD."""
    try:
        # Remove currency symbols and clean up
        clean_str = re.sub(r'[^\d.,a-zA-Z]', '', size_str)

        # Extract number
        number_match = re.search(r'([\d,]+\.?\d*)', clean_str)
        if not number_match:
            return None

        number_str = number_match.group(1).replace(',', '')
        number = float(number_str)

        # Convert to billions based on unit
        if 'trillion' in clean_str.lower():
            return number * 1000  # Convert trillions to billions
        elif 'billion' in clean_str.lower():
            return number
        elif 'million' in clean_str.lower():
            return number / 1000  # Convert millions to billions
        else:
            # Assume billions if no unit specified
            return number

    except (ValueError, AttributeError):
        return None


def validate_tam_sam_som_logic(tam: float | None, sam: float | None, som: float | None) -> dict[str, any]:
    """
    Validate the logical relationship between TAM, SAM, and SOM values.
    
    Args:
        tam: Total Addressable Market value
        sam: Serviceable Addressable Market value
        som: Serviceable Obtainable Market value
        
    Returns:
        Dictionary containing validation results
    """
    validation_result = {
        'is_valid': True,
        'warnings': [],
        'errors': [],
        'relationships': {}
    }

    try:
        # Check if values are provided
        values = {'TAM': tam, 'SAM': sam, 'SOM': som}
        provided_values = {k: v for k, v in values.items() if v is not None}

        if len(provided_values) < 2:
            validation_result['warnings'].append("Insufficient data for relationship validation")
            return validation_result

        # Validate TAM >= SAM >= SOM relationship
        if tam is not None and sam is not None:
            if sam > tam:
                validation_result['errors'].append(f"SAM ({sam:.2f}B) cannot be greater than TAM ({tam:.2f}B)")
                validation_result['is_valid'] = False
            else:
                validation_result['relationships']['SAM_to_TAM_ratio'] = round(sam / tam, 3)

        if sam is not None and som is not None:
            if som > sam:
                validation_result['errors'].append(f"SOM ({som:.2f}B) cannot be greater than SAM ({sam:.2f}B)")
                validation_result['is_valid'] = False
            else:
                validation_result['relationships']['SOM_to_SAM_ratio'] = round(som / sam, 3)

        if tam is not None and som is not None:
            if som > tam:
                validation_result['errors'].append(f"SOM ({som:.2f}B) cannot be greater than TAM ({tam:.2f}B)")
                validation_result['is_valid'] = False
            else:
                validation_result['relationships']['SOM_to_TAM_ratio'] = round(som / tam, 3)

        # Check for reasonable ratios
        if 'SAM_to_TAM_ratio' in validation_result['relationships']:
            ratio = validation_result['relationships']['SAM_to_TAM_ratio']
            if ratio < 0.1:
                validation_result['warnings'].append(f"SAM is only {ratio*100:.1f}% of TAM - unusually small serviceable market")
            elif ratio > 0.8:
                validation_result['warnings'].append(f"SAM is {ratio*100:.1f}% of TAM - unusually large serviceable market")

        if 'SOM_to_SAM_ratio' in validation_result['relationships']:
            ratio = validation_result['relationships']['SOM_to_SAM_ratio']
            if ratio < 0.05:
                validation_result['warnings'].append(f"SOM is only {ratio*100:.1f}% of SAM - very conservative obtainable market")
            elif ratio > 0.5:
                validation_result['warnings'].append(f"SOM is {ratio*100:.1f}% of SAM - aggressive obtainable market projection")

    except Exception as e:
        logger.error(f"Error validating TAM/SAM/SOM logic: {e}")
        validation_result['errors'].append(f"Validation error: {e!s}")
        validation_result['is_valid'] = False

    return validation_result

"""
Core data models for the startup evaluation system.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, validator


class CompetitorType(str, Enum):
    """Types of competitors."""

    DIRECT = "direct"
    INDIRECT = "indirect"
    SUBSTITUTE = "substitute"


class ValidationStatus(str, Enum):
    """Validation status for competitor data."""

    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    MISSING_INFO = "missing_info"


class CompetitiveAdvantageCategory(str, Enum):
    """Categories of competitive advantages."""

    TECHNOLOGY = "technology"
    MARKET_POSITION = "market_position"
    PARTNERSHIPS = "partnerships"
    PRICING = "pricing"
    FEATURES = "features"


class CompetitorMention(BaseModel):
    """A competitor mentioned by the startup."""

    name: str
    category: CompetitorType
    description: str
    claimed_differentiator: str
    validation_status: ValidationStatus


class CompetitiveAdvantage(BaseModel):
    """A competitive advantage claim made by the startup."""

    claim: str
    category: CompetitiveAdvantageCategory
    evidence_provided: str
    validation_needed: bool


class MarketPositioning(BaseModel):
    """Market positioning information from the startup."""

    target_market: str
    market_segment: str
    positioning_statement: str


class DataQuality(BaseModel):
    """Data quality assessment for competitor information."""

    completeness_score: float = Field(default=0.0, ge=0, le=1)
    consistency_score: float = Field(default=0.0, ge=0, le=1)
    missing_information: list[str] = Field(default_factory=list)
    validation_flags: list[str] = Field(default_factory=list)


class CompetitorInput(BaseModel):
    """Input data for competitor analysis."""

    startup_name: str
    market_segment: str
    existing_competitors: list[CompetitorMention] = Field(default_factory=list)
    competitive_advantages: list[str] = Field(default_factory=list)
    market_positioning: str
    target_customers: str


class CompetitorExtractionResult(BaseModel):
    """Results from competitor extraction process."""

    extraction_summary: dict[str, int]
    competitors: list[CompetitorMention]
    competitive_advantages: list[CompetitiveAdvantage]
    market_positioning: MarketPositioning
    data_quality: DataQuality
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


# Report Synthesis Models


class ConfidenceLevel(str, Enum):
    """Confidence levels for analysis findings."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INSUFFICIENT_DATA = "insufficient_data"


class RiskLevel(str, Enum):
    """Risk levels for competitive threats."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CompetitorProfile(BaseModel):
    """Comprehensive competitor profile."""

    name: str
    category: CompetitorType
    market_position: str
    funding_status: str = ""
    product_offerings: list[str] = Field(default_factory=list)
    customer_base: str = ""
    competitive_advantages: list[str] = Field(default_factory=list)
    competitive_vulnerabilities: list[str] = Field(default_factory=list)
    threat_level: RiskLevel
    intelligence_confidence: ConfidenceLevel
    validation_status: ValidationStatus


class CompetitiveAdvantageValidation(BaseModel):
    """Validation result for a competitive advantage claim."""

    claim: str
    category: CompetitiveAdvantageCategory
    validation_status: (
        str  # Validated/Partially Validated/Contradicted/Insufficient Data
    )
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    competitive_context: str = ""
    sustainability_assessment: str = ""
    confidence_level: ConfidenceLevel


class CompetitiveRisk(BaseModel):
    """A competitive risk identified in the analysis."""

    risk_name: str
    risk_description: str
    probability: RiskLevel
    impact: RiskLevel
    overall_risk_level: RiskLevel
    mitigation_strategies: list[str] = Field(default_factory=list)
    monitoring_requirements: list[str] = Field(default_factory=list)


class StrategicRecommendation(BaseModel):
    """A strategic recommendation from the analysis."""

    title: str
    description: str
    priority: (
        RiskLevel  # Using RiskLevel enum for priority (CRITICAL, HIGH, MEDIUM, LOW)
    )
    timeframe: str  # "immediate", "short-term", "medium-term", "long-term"
    resource_requirements: list[str] = Field(default_factory=list)
    expected_outcome: str = ""
    success_metrics: list[str] = Field(default_factory=list)


class CompetitiveLandscape(BaseModel):
    """Comprehensive competitive landscape analysis."""

    total_competitors: int
    direct_competitors: list[CompetitorProfile] = Field(default_factory=list)
    indirect_competitors: list[CompetitorProfile] = Field(default_factory=list)
    substitute_competitors: list[CompetitorProfile] = Field(default_factory=list)
    market_concentration: (
        str  # "fragmented", "moderately_concentrated", "highly_concentrated"
    )
    competitive_intensity: RiskLevel
    market_maturity: str  # "early", "growth", "mature", "declining"


class GapAnalysis(BaseModel):
    """Analysis of competitive gaps and missing competitors."""

    critical_missing_competitors: list[CompetitorProfile] = Field(default_factory=list)
    secondary_missing_competitors: list[str] = Field(default_factory=list)
    market_coverage_scores: dict[str, float] = Field(
        default_factory=dict
    )  # category -> coverage %
    competitive_blind_spots: list[str] = Field(default_factory=list)
    gap_impact_assessment: RiskLevel
    overall_gap_risk: RiskLevel


class ConfidenceScoring(BaseModel):
    """Confidence scores for different analysis areas."""

    competitive_landscape_confidence: float = Field(default=0.0, ge=0, le=10)
    competitor_intelligence_confidence: float = Field(default=0.0, ge=0, le=10)
    advantage_validation_confidence: float = Field(default=0.0, ge=0, le=10)
    gap_analysis_confidence: float = Field(default=0.0, ge=0, le=10)
    risk_assessment_confidence: float = Field(default=0.0, ge=0, le=10)
    overall_report_confidence: float = Field(default=0.0, ge=0, le=10)
    data_quality_score: float = Field(default=0.0, ge=0, le=10)
    validation_completeness: float = Field(default=0.0, ge=0, le=10)
    uncertainty_areas: list[str] = Field(default_factory=list)


class CompetitorAnalysisReport(BaseModel):
    """Complete competitor analysis report."""

    startup_name: str
    market_segment: str
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    report_version: str = "1.0"

    # Executive Summary
    competitive_landscape_complexity: RiskLevel
    competitive_intensity: RiskLevel
    startup_competitive_position: str  # "strong", "moderate", "weak"
    overall_risk_level: RiskLevel
    key_findings: list[str] = Field(default_factory=list)
    critical_competitive_risks: list[str] = Field(default_factory=list)
    investment_implications: str = ""

    # Analysis Results
    competitive_landscape: CompetitiveLandscape
    advantage_validations: list[CompetitiveAdvantageValidation] = Field(
        default_factory=list
    )
    gap_analysis: GapAnalysis
    competitive_risks: list[CompetitiveRisk] = Field(default_factory=list)
    strategic_recommendations: list[StrategicRecommendation] = Field(
        default_factory=list
    )
    confidence_scoring: ConfidenceScoring

    # Metadata
    data_sources: list[str] = Field(default_factory=list)
    analysis_limitations: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# Business KPI Analysis Models


class GrowthStage(str, Enum):
    """Startup growth stages."""

    SEED = "seed"
    EARLY = "early"
    GROWTH = "growth"
    MATURE = "mature"


class MarketSizeClaims(BaseModel):
    """Market size claims from startup."""

    tam: float | None = Field(None, description="Total Addressable Market")
    sam: float | None = Field(None, description="Serviceable Addressable Market")
    som: float | None = Field(None, description="Serviceable Obtainable Market")
    currency: str = Field(default="USD", description="Currency for market size values")
    year: int = Field(description="Year for market size projections")
    sources: list[str] = Field(
        default_factory=list, description="Sources for market size claims"
    )
    methodology: str | None = Field(
        None, description="Methodology used for market size calculation"
    )

    @validator("tam", "sam", "som")
    def validate_market_size(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Market size values must be positive")
        return v

    @validator("year")
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v < 2020 or v > current_year + 10:
            raise ValueError(f"Year must be between 2020 and {current_year + 10}")
        return v

    @validator("currency")
    def validate_currency(cls, v):
        valid_currencies = ["USD", "EUR", "GBP", "INR", "JPY", "CNY", "CAD", "AUD"]
        if v not in valid_currencies:
            raise ValueError(f"Currency must be one of: {', '.join(valid_currencies)}")
        return v


class BusinessKPIInput(BaseModel):
    """Input data for business KPI analysis."""

    startup_name: str = Field(description="Name of the startup")
    industry_description: str = Field(
        description="Description of the startup's industry"
    )
    business_model: str = Field(description="Description of the business model")
    market_size_claims: MarketSizeClaims = Field(
        description="Market size claims from the startup"
    )
    current_kpis: dict[str, Any] = Field(
        description="Current KPI values provided by the startup"
    )
    growth_stage: GrowthStage = Field(description="Current growth stage of the startup")
    geographic_focus: list[str] = Field(
        description="Geographic markets the startup focuses on"
    )
    target_customers: str = Field(description="Description of target customer segments")

    @field_validator("startup_name")
    def validate_startup_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Startup name must be at least 2 characters long")
        return v.strip()

    @field_validator("industry_description", "business_model", "target_customers")
    def validate_text_fields(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("Field must be at least 10 characters long")
        return v.strip()

    @field_validator("current_kpis")
    def validate_current_kpis(cls, v):
        if not v:
            raise ValueError("At least one KPI must be provided")
        return v

    @field_validator("geographic_focus")
    def validate_geographic_focus(cls, v):
        if not v:
            raise ValueError("At least one geographic focus must be specified")
        return [geo.strip() for geo in v if geo.strip()]


class IndustryClassification(BaseModel):
    """Industry classification results."""

    primary_industry: str = Field(description="Primary industry classification")
    secondary_industries: list[str] = Field(
        default_factory=list, description="Secondary industry classifications"
    )
    confidence_score: float = Field(
        ge=0, le=1, description="Confidence score for classification"
    )
    industry_code: str = Field(description="Industry code (NAICS or similar)")
    business_model_type: str = Field(description="Type of business model")

    @validator("primary_industry", "business_model_type")
    def validate_required_strings(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Field must be at least 2 characters long")
        return v.strip()

    @validator("industry_code")
    def validate_industry_code(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Industry code must be provided")
        return v.strip()


class ValidationResult(BaseModel):
    """Individual metric validation result."""

    claimed_value: float = Field(description="Value claimed by the startup")
    market_estimate: float = Field(
        description="Market estimate from authoritative sources"
    )
    variance_percentage: float = Field(
        description="Percentage variance between claimed and market estimate"
    )
    confidence_level: float = Field(
        ge=0, le=1, description="Confidence level in the validation"
    )
    sources: list[str] = Field(
        default_factory=list, description="Sources used for validation"
    )
    validation_status: ValidationStatus = Field(description="Status of the validation")

    @field_validator("claimed_value", "market_estimate")
    def validate_positive_values(cls, v):
        if v <= 0:
            raise ValueError("Values must be positive")
        return v


class MarketValidationResult(BaseModel):
    """Market size validation results."""

    tam_validation: ValidationResult | None = Field(
        None, description="TAM validation result"
    )
    sam_validation: ValidationResult | None = Field(
        None, description="SAM validation result"
    )
    som_validation: ValidationResult | None = Field(
        None, description="SOM validation result"
    )
    overall_confidence: float = Field(
        ge=0, le=1, description="Overall confidence in market validation"
    )
    discrepancy_flags: list[str] = Field(
        default_factory=list, description="Flags for significant discrepancies"
    )

    @field_validator("overall_confidence")
    def validate_confidence(cls, v):
        if v < 0 or v > 1:
            raise ValueError("Confidence must be between 0 and 1")
        return v


class KPIDefinition(BaseModel):
    """Individual KPI definition."""

    name: str = Field(description="Name of the KPI")
    description: str = Field(description="Description of the KPI")
    calculation_method: str = Field(description="Method for calculating the KPI")
    industry_benchmarks: dict[str, float] = Field(
        default_factory=dict, description="Industry benchmark percentile ranges"
    )
    importance_weight: float = Field(
        ge=0, le=1, description="Importance weight for this KPI"
    )

    @field_validator("name", "description", "calculation_method")
    def validate_required_fields(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Field must be at least 2 characters long")
        return v.strip()

    @field_validator("importance_weight")
    def validate_weight(cls, v):
        if v < 0 or v > 1:
            raise ValueError("Importance weight must be between 0 and 1")
        return v


class KPIFramework(BaseModel):
    """Industry-specific KPI framework."""

    industry: str = Field(description="Industry for this framework")
    primary_kpis: list[KPIDefinition] = Field(
        description="Primary KPIs for the industry"
    )
    secondary_kpis: list[KPIDefinition] = Field(
        default_factory=list, description="Secondary KPIs for the industry"
    )
    benchmark_sources: list[str] = Field(
        default_factory=list, description="Sources for benchmark data"
    )

    @field_validator("industry")
    def validate_industry(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Industry must be specified")
        return v.strip()

    @field_validator("primary_kpis")
    def validate_primary_kpis(cls, v):
        if not v:
            raise ValueError("At least one primary KPI must be defined")
        return v


class KPIPerformance(BaseModel):
    """Individual KPI performance analysis."""

    kpi_name: str = Field(description="Name of the KPI")
    current_value: float = Field(description="Current value of the KPI")
    industry_percentile: float = Field(
        ge=0, le=100, description="Industry percentile ranking"
    )
    benchmark_comparison: str = Field(description="Comparison against benchmarks")
    performance_trend: str = Field(description="Performance trend analysis")
    improvement_recommendations: list[str] = Field(
        default_factory=list, description="Recommendations for improvement"
    )

    @field_validator("kpi_name", "benchmark_comparison", "performance_trend")
    def validate_required_strings(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Field must be provided")
        return v.strip()

    @field_validator("industry_percentile")
    def validate_percentile(cls, v):
        if v < 0 or v > 100:
            raise ValueError("Percentile must be between 0 and 100")
        return v


class KPIAnalysisResult(BaseModel):
    """KPI performance analysis results."""

    analyzed_kpis: list[KPIPerformance] = Field(description="List of analyzed KPIs")
    missing_kpis: list[str] = Field(
        default_factory=list, description="KPIs that are missing from the analysis"
    )
    performance_summary: dict[str, Any] = Field(
        default_factory=dict, description="Summary of performance metrics"
    )
    trend_analysis: dict[str, Any] = Field(
        default_factory=dict, description="Trend analysis results"
    )

    @field_validator("analyzed_kpis")
    def validate_analyzed_kpis(cls, v):
        if not v:
            raise ValueError("At least one KPI must be analyzed")
        return v


class BenchmarkingResult(BaseModel):
    """Industry benchmarking results."""

    overall_performance_score: float = Field(
        ge=0, le=10, description="Overall performance score"
    )
    peer_comparison: dict[str, Any] = Field(
        default_factory=dict, description="Comparison with peer companies"
    )
    industry_position: str = Field(description="Position within the industry")
    competitive_advantages: list[str] = Field(
        default_factory=list, description="Identified competitive advantages"
    )
    improvement_areas: list[str] = Field(
        default_factory=list, description="Areas needing improvement"
    )

    @field_validator("overall_performance_score")
    def validate_score(cls, v):
        if v < 0 or v > 10:
            raise ValueError("Performance score must be between 0 and 10")
        return v

    @field_validator("industry_position")
    def validate_position(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Industry position must be specified")
        return v.strip()


class BusinessKPIAnalysisResult(BaseModel):
    """Complete business KPI analysis results."""

    startup_name: str = Field(description="Name of the analyzed startup")
    industry_classification: IndustryClassification = Field(
        description="Industry classification results"
    )
    market_validation: MarketValidationResult = Field(
        description="Market size validation results"
    )
    kpi_analysis: KPIAnalysisResult = Field(description="KPI performance analysis")
    benchmarking_results: BenchmarkingResult = Field(
        description="Industry benchmarking results"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Strategic recommendations"
    )
    risk_factors: list[str] = Field(
        default_factory=list, description="Identified risk factors"
    )
    confidence_scores: dict[str, float] = Field(
        default_factory=dict,
        description="Confidence scores for different analysis areas",
    )
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when analysis was generated",
    )

    @field_validator("startup_name")
    def validate_startup_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Startup name must be provided")
        return v.strip()

    @field_validator("confidence_scores")
    def validate_confidence_scores(cls, v):
        for key, score in v.items():
            if score < 0 or score > 1:
                raise ValueError(f"Confidence score for {key} must be between 0 and 1")
        return v

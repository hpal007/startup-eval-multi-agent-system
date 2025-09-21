"""Prompts and instructions for KPI Framework Selector agent."""

KPI_FRAMEWORK_SELECTOR_INSTRUCTION = """
You are a KPI Framework Selector agent specialized in selecting and customizing industry-specific Key Performance Indicator frameworks for startups based on their industry classification, growth stage, and business model.

Your primary responsibilities:
1. Select appropriate KPI frameworks based on industry classification
2. Customize frameworks for specific growth stages and business models
3. Validate framework completeness and relevance
4. Provide industry-specific KPI definitions and benchmarks

## Industry-Specific KPI Frameworks

### SaaS/Software Industry
**Primary KPIs:**
- ARR (Annual Recurring Revenue): Total recurring revenue normalized to annual basis
- MRR (Monthly Recurring Revenue): Predictable monthly revenue from subscriptions
- CAC (Customer Acquisition Cost): Total cost to acquire a new customer
- LTV (Lifetime Value): Total revenue expected from a customer over their lifetime
- Churn Rate: Percentage of customers who cancel subscriptions in a period
- NPS (Net Promoter Score): Customer satisfaction and loyalty metric
- ARPU (Average Revenue Per User): Average revenue generated per user/customer

**Secondary KPIs:**
- Gross Revenue Retention: Revenue retention from existing customers
- Net Revenue Retention: Revenue retention including expansion revenue
- Time to Value: Time for customers to realize value from the product
- Feature Adoption Rate: Percentage of users adopting key features
- Support Ticket Volume: Customer support request volume trends

### E-commerce Industry
**Primary KPIs:**
- GMV (Gross Merchandise Value): Total value of goods sold through platform
- Conversion Rate: Percentage of visitors who complete purchases
- AOV (Average Order Value): Average amount spent per transaction
- CAC (Customer Acquisition Cost): Cost to acquire new customers
- Customer Retention Rate: Percentage of customers who make repeat purchases
- Cart Abandonment Rate: Percentage of shopping carts abandoned before purchase

**Secondary KPIs:**
- Return Rate: Percentage of products returned by customers
- Inventory Turnover: How quickly inventory is sold and replaced
- Customer Satisfaction Score: Post-purchase satisfaction ratings
- Mobile Conversion Rate: Conversion rate specifically for mobile users
- Payment Success Rate: Percentage of successful payment transactions

### Fintech Industry
**Primary KPIs:**
- Transaction Volume: Total value of transactions processed
- User Growth Rate: Rate of new user acquisition
- Revenue per User: Average revenue generated per active user
- Regulatory Compliance Score: Adherence to financial regulations
- Fraud Rate: Percentage of fraudulent transactions detected
- Customer Onboarding Time: Time to complete customer verification and setup

**Secondary KPIs:**
- API Uptime: System availability and reliability metrics
- Cost per Transaction: Operational cost for processing transactions
- Customer Support Resolution Time: Time to resolve customer issues
- Cross-sell Rate: Success rate of selling additional products to existing customers
- Deposit Growth Rate: Growth in customer deposits or account balances

### Healthcare/Biotech Industry
**Primary KPIs:**
- Clinical Trial Progress: Advancement through trial phases
- Regulatory Approval Milestones: Progress toward regulatory approvals
- Patient Outcomes: Efficacy and safety metrics from trials
- R&D Efficiency: Research and development cost per milestone
- Time to Market: Timeline from research to market availability
- Intellectual Property Portfolio: Number and quality of patents

**Secondary KPIs:**
- Patient Recruitment Rate: Speed of enrolling patients in trials
- Adverse Event Rate: Safety incidents in clinical trials
- Manufacturing Yield: Efficiency of drug/device production
- Regulatory Submission Quality: Success rate of regulatory filings
- Partnership Development: Strategic partnerships with healthcare organizations

## Growth Stage Customization

### Seed Stage
- Focus on product-market fit indicators
- Emphasize user engagement and retention metrics
- Prioritize cost efficiency and runway extension
- Include early traction and validation metrics

### Early Stage
- Balance growth metrics with unit economics
- Include customer acquisition and retention KPIs
- Monitor operational efficiency improvements
- Track competitive positioning metrics

### Growth Stage
- Emphasize scalability and market expansion metrics
- Include advanced financial performance indicators
- Monitor operational leverage and efficiency gains
- Track market share and competitive advantages

### Mature Stage
- Focus on profitability and sustainable growth
- Include comprehensive financial performance metrics
- Monitor market leadership and innovation metrics
- Track long-term value creation indicators

## Business Model Customization

### B2B Models
- Emphasize enterprise sales metrics (deal size, sales cycle length)
- Include customer success and expansion revenue metrics
- Focus on relationship-based retention indicators
- Monitor contract value and renewal rates

### B2C Models
- Emphasize user acquisition and engagement metrics
- Include viral growth and referral indicators
- Focus on consumer behavior and satisfaction metrics
- Monitor brand awareness and market penetration

### Marketplace Models
- Balance supply and demand side metrics
- Include network effects and liquidity indicators
- Focus on transaction facilitation efficiency
- Monitor ecosystem health and growth

### Subscription Models
- Emphasize recurring revenue and retention metrics
- Include cohort analysis and lifetime value indicators
- Focus on subscription growth and churn prevention
- Monitor pricing optimization and expansion revenue

## Framework Selection Process

1. **Industry Classification Analysis**: Review primary and secondary industry classifications
2. **Business Model Assessment**: Analyze revenue model, customer type, and value proposition
3. **Growth Stage Evaluation**: Determine current stage and near-term trajectory
4. **Framework Customization**: Select and adapt appropriate KPI frameworks
5. **Validation and Completeness Check**: Ensure framework covers all critical business aspects

## Output Requirements

Provide a structured KPI framework selection that includes:
1. Selected primary KPIs with definitions and calculation methods
2. Relevant secondary KPIs for comprehensive analysis
3. Industry-specific benchmark ranges where available
4. Growth stage customizations and priorities
5. Business model adaptations and considerations
6. Framework validation and completeness assessment

Always justify your framework selection based on the startup's specific characteristics and provide clear rationale for KPI prioritization and customization decisions.
"""

# Industry-specific KPI framework databases
SAAS_KPI_FRAMEWORK = {
    "industry": "SaaS/Software",
    "primary_kpis": [
        {
            "name": "ARR",
            "description": "Annual Recurring Revenue - Total recurring revenue normalized to annual basis",
            "calculation": "MRR * 12 or sum of annual contract values",
            "importance_weight": 0.25,
            "benchmark_ranges": {
                "seed": {"p25": 0, "p50": 100000, "p75": 500000},
                "early": {"p25": 500000, "p50": 2000000, "p75": 10000000},
                "growth": {"p25": 10000000, "p50": 50000000, "p75": 200000000}
            }
        },
        {
            "name": "CAC",
            "description": "Customer Acquisition Cost - Total cost to acquire a new customer",
            "calculation": "Total sales and marketing costs / Number of new customers acquired",
            "importance_weight": 0.20,
            "benchmark_ranges": {
                "seed": {"p25": 100, "p50": 500, "p75": 2000},
                "early": {"p25": 500, "p50": 1500, "p75": 5000},
                "growth": {"p25": 1000, "p50": 3000, "p75": 10000}
            }
        },
        {
            "name": "LTV",
            "description": "Lifetime Value - Total revenue expected from a customer over their lifetime",
            "calculation": "ARPU / Churn Rate or more sophisticated cohort analysis",
            "importance_weight": 0.20,
            "benchmark_ranges": {
                "seed": {"p25": 1000, "p50": 5000, "p75": 20000},
                "early": {"p25": 5000, "p50": 15000, "p75": 50000},
                "growth": {"p25": 10000, "p50": 30000, "p75": 100000}
            }
        },
        {
            "name": "Churn Rate",
            "description": "Percentage of customers who cancel subscriptions in a period",
            "calculation": "Customers lost in period / Total customers at start of period",
            "importance_weight": 0.15,
            "benchmark_ranges": {
                "seed": {"p25": 0.02, "p50": 0.05, "p75": 0.10},
                "early": {"p25": 0.01, "p50": 0.03, "p75": 0.07},
                "growth": {"p25": 0.005, "p50": 0.02, "p75": 0.05}
            }
        },
        {
            "name": "NPS",
            "description": "Net Promoter Score - Customer satisfaction and loyalty metric",
            "calculation": "% Promoters (9-10) - % Detractors (0-6)",
            "importance_weight": 0.10,
            "benchmark_ranges": {
                "seed": {"p25": 20, "p50": 40, "p75": 60},
                "early": {"p25": 30, "p50": 50, "p75": 70},
                "growth": {"p25": 40, "p50": 60, "p75": 80}
            }
        },
        {
            "name": "ARPU",
            "description": "Average Revenue Per User - Average revenue generated per user/customer",
            "calculation": "Total Revenue / Number of Active Users",
            "importance_weight": 0.10,
            "benchmark_ranges": {
                "seed": {"p25": 50, "p50": 200, "p75": 1000},
                "early": {"p25": 100, "p50": 500, "p75": 2000},
                "growth": {"p25": 200, "p50": 1000, "p75": 5000}
            }
        }
    ],
    "secondary_kpis": [
        "Gross Revenue Retention", "Net Revenue Retention", "Time to Value",
        "Feature Adoption Rate", "Support Ticket Volume"
    ]
}

ECOMMERCE_KPI_FRAMEWORK = {
    "industry": "E-commerce",
    "primary_kpis": [
        {
            "name": "GMV",
            "description": "Gross Merchandise Value - Total value of goods sold through platform",
            "calculation": "Sum of all transaction values in a period",
            "importance_weight": 0.25,
            "benchmark_ranges": {
                "seed": {"p25": 10000, "p50": 100000, "p75": 1000000},
                "early": {"p25": 1000000, "p50": 10000000, "p75": 50000000},
                "growth": {"p25": 50000000, "p50": 200000000, "p75": 1000000000}
            }
        },
        {
            "name": "Conversion Rate",
            "description": "Percentage of visitors who complete purchases",
            "calculation": "Number of purchases / Number of unique visitors",
            "importance_weight": 0.20,
            "benchmark_ranges": {
                "seed": {"p25": 0.01, "p50": 0.02, "p75": 0.04},
                "early": {"p25": 0.02, "p50": 0.03, "p75": 0.05},
                "growth": {"p25": 0.03, "p50": 0.04, "p75": 0.07}
            }
        },
        {
            "name": "AOV",
            "description": "Average Order Value - Average amount spent per transaction",
            "calculation": "Total Revenue / Number of Orders",
            "importance_weight": 0.20,
            "benchmark_ranges": {
                "seed": {"p25": 25, "p50": 50, "p75": 100},
                "early": {"p25": 50, "p50": 75, "p75": 150},
                "growth": {"p25": 75, "p50": 100, "p75": 200}
            }
        },
        {
            "name": "CAC",
            "description": "Customer Acquisition Cost - Cost to acquire new customers",
            "calculation": "Total marketing costs / Number of new customers acquired",
            "importance_weight": 0.15,
            "benchmark_ranges": {
                "seed": {"p25": 10, "p50": 25, "p75": 50},
                "early": {"p25": 25, "p50": 50, "p75": 100},
                "growth": {"p25": 50, "p50": 75, "p75": 150}
            }
        },
        {
            "name": "Customer Retention Rate",
            "description": "Percentage of customers who make repeat purchases",
            "calculation": "Repeat customers / Total customers in period",
            "importance_weight": 0.10,
            "benchmark_ranges": {
                "seed": {"p25": 0.15, "p50": 0.25, "p75": 0.40},
                "early": {"p25": 0.25, "p50": 0.35, "p75": 0.50},
                "growth": {"p25": 0.35, "p50": 0.45, "p75": 0.60}
            }
        },
        {
            "name": "Cart Abandonment Rate",
            "description": "Percentage of shopping carts abandoned before purchase",
            "calculation": "Abandoned carts / Total carts created",
            "importance_weight": 0.10,
            "benchmark_ranges": {
                "seed": {"p25": 0.60, "p50": 0.70, "p75": 0.80},
                "early": {"p25": 0.55, "p50": 0.65, "p75": 0.75},
                "growth": {"p25": 0.50, "p50": 0.60, "p75": 0.70}
            }
        }
    ],
    "secondary_kpis": [
        "Return Rate", "Inventory Turnover", "Customer Satisfaction Score",
        "Mobile Conversion Rate", "Payment Success Rate"
    ]
}

FINTECH_KPI_FRAMEWORK = {
    "industry": "Fintech",
    "primary_kpis": [
        {
            "name": "Transaction Volume",
            "description": "Total value of transactions processed",
            "calculation": "Sum of all transaction amounts in a period",
            "importance_weight": 0.25,
            "benchmark_ranges": {
                "seed": {"p25": 100000, "p50": 1000000, "p75": 10000000},
                "early": {"p25": 10000000, "p50": 100000000, "p75": 1000000000},
                "growth": {"p25": 1000000000, "p50": 10000000000, "p75": 100000000000}
            }
        },
        {
            "name": "User Growth Rate",
            "description": "Rate of new user acquisition",
            "calculation": "(New users this period / Users last period) - 1",
            "importance_weight": 0.20,
            "benchmark_ranges": {
                "seed": {"p25": 0.10, "p50": 0.20, "p75": 0.50},
                "early": {"p25": 0.05, "p50": 0.15, "p75": 0.30},
                "growth": {"p25": 0.02, "p50": 0.10, "p75": 0.20}
            }
        },
        {
            "name": "Revenue per User",
            "description": "Average revenue generated per active user",
            "calculation": "Total Revenue / Number of Active Users",
            "importance_weight": 0.20,
            "benchmark_ranges": {
                "seed": {"p25": 10, "p50": 50, "p75": 200},
                "early": {"p25": 50, "p50": 150, "p75": 500},
                "growth": {"p25": 100, "p50": 300, "p75": 1000}
            }
        },
        {
            "name": "Regulatory Compliance Score",
            "description": "Adherence to financial regulations",
            "calculation": "Compliance metrics based on regulatory requirements",
            "importance_weight": 0.15,
            "benchmark_ranges": {
                "seed": {"p25": 0.80, "p50": 0.90, "p75": 0.95},
                "early": {"p25": 0.90, "p50": 0.95, "p75": 0.98},
                "growth": {"p25": 0.95, "p50": 0.98, "p75": 0.99}
            }
        },
        {
            "name": "Fraud Rate",
            "description": "Percentage of fraudulent transactions detected",
            "calculation": "Fraudulent transactions / Total transactions",
            "importance_weight": 0.10,
            "benchmark_ranges": {
                "seed": {"p25": 0.001, "p50": 0.005, "p75": 0.01},
                "early": {"p25": 0.0005, "p50": 0.002, "p75": 0.005},
                "growth": {"p25": 0.0001, "p50": 0.001, "p75": 0.003}
            }
        },
        {
            "name": "Customer Onboarding Time",
            "description": "Time to complete customer verification and setup",
            "calculation": "Average time from signup to first transaction",
            "importance_weight": 0.10,
            "benchmark_ranges": {
                "seed": {"p25": 24, "p50": 48, "p75": 120},
                "early": {"p25": 12, "p50": 24, "p75": 72},
                "growth": {"p25": 6, "p50": 12, "p75": 24}
            }
        }
    ],
    "secondary_kpis": [
        "API Uptime", "Cost per Transaction", "Customer Support Resolution Time",
        "Cross-sell Rate", "Deposit Growth Rate"
    ]
}

HEALTHCARE_KPI_FRAMEWORK = {
    "industry": "Healthcare/Biotech",
    "primary_kpis": [
        {
            "name": "Clinical Trial Progress",
            "description": "Advancement through trial phases",
            "calculation": "Phase completion percentage and milestone achievements",
            "importance_weight": 0.30,
            "benchmark_ranges": {
                "seed": {"p25": 0.1, "p50": 0.3, "p75": 0.6},
                "early": {"p25": 0.3, "p50": 0.6, "p75": 0.8},
                "growth": {"p25": 0.6, "p50": 0.8, "p75": 1.0}
            }
        },
        {
            "name": "Regulatory Approval Milestones",
            "description": "Progress toward regulatory approvals",
            "calculation": "Regulatory submission and approval status",
            "importance_weight": 0.25,
            "benchmark_ranges": {
                "seed": {"p25": 0.0, "p50": 0.2, "p75": 0.5},
                "early": {"p25": 0.2, "p50": 0.5, "p75": 0.8},
                "growth": {"p25": 0.5, "p50": 0.8, "p75": 1.0}
            }
        },
        {
            "name": "Patient Outcomes",
            "description": "Efficacy and safety metrics from trials",
            "calculation": "Clinical endpoint achievement rates",
            "importance_weight": 0.20,
            "benchmark_ranges": {
                "seed": {"p25": 0.3, "p50": 0.5, "p75": 0.7},
                "early": {"p25": 0.5, "p50": 0.7, "p75": 0.8},
                "growth": {"p25": 0.7, "p50": 0.8, "p75": 0.9}
            }
        },
        {
            "name": "R&D Efficiency",
            "description": "Research and development cost per milestone",
            "calculation": "R&D costs / Number of milestones achieved",
            "importance_weight": 0.15,
            "benchmark_ranges": {
                "seed": {"p25": 1000000, "p50": 5000000, "p75": 20000000},
                "early": {"p25": 5000000, "p50": 15000000, "p75": 50000000},
                "growth": {"p25": 10000000, "p50": 30000000, "p75": 100000000}
            }
        },
        {
            "name": "Intellectual Property Portfolio",
            "description": "Number and quality of patents",
            "calculation": "Patent applications, grants, and citation metrics",
            "importance_weight": 0.10,
            "benchmark_ranges": {
                "seed": {"p25": 1, "p50": 3, "p75": 10},
                "early": {"p25": 5, "p50": 15, "p75": 30},
                "growth": {"p25": 20, "p50": 50, "p75": 100}
            }
        }
    ],
    "secondary_kpis": [
        "Patient Recruitment Rate", "Adverse Event Rate", "Manufacturing Yield",
        "Regulatory Submission Quality", "Partnership Development"
    ]
}

# Framework database mapping
KPI_FRAMEWORK_DATABASE = {
    "saas": SAAS_KPI_FRAMEWORK,
    "software": SAAS_KPI_FRAMEWORK,
    "ecommerce": ECOMMERCE_KPI_FRAMEWORK,
    "e-commerce": ECOMMERCE_KPI_FRAMEWORK,
    "fintech": FINTECH_KPI_FRAMEWORK,
    "financial_services": FINTECH_KPI_FRAMEWORK,
    "healthcare": HEALTHCARE_KPI_FRAMEWORK,
    "biotech": HEALTHCARE_KPI_FRAMEWORK,
    "biotechnology": HEALTHCARE_KPI_FRAMEWORK
}

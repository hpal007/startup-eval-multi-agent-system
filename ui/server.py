#!/usr/bin/env python3
"""
ADK FastAPI Server for Startup Evaluation UI

This server uses Google's Agent Development Kit (ADK) to provide
FastAPI endpoints with Server-Sent Events (SSE) for real-time updates.
"""

import os
import sys
import uvicorn
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to import workflow modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.sessions import DatabaseSessionService

# Configuration
APP_NAME = "chatgpt_agentic_clone_app"  # Must match main.py APP_NAME
AGENT_DIR = str(parent_dir / "workflow" / "master")  # Directory containing the agent.py with root_agent
SESSION_DB_URL = "sqlite:///sessions.db"  # Session database
UPLOAD_DIR = str(parent_dir / "uploaded")  # Directory for uploaded files
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000", 
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
    "*"  # Allow all origins for development
]
SERVE_WEB_INTERFACE = False  # Disable ADK's built-in web interface to use our custom UI
PORT = int(os.environ.get("PORT", 8080))

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

def create_app():
    """Create and configure the FastAPI app using ADK."""
    
    # Get the ADK FastAPI app - this automatically includes:
    # - /run_sse endpoint for streaming agent responses
    # - /sessions endpoints for session management  
    # - Built-in web interface (if enabled)
    # - CORS handling
    app = get_fast_api_app(
        agents_dir=AGENT_DIR,
        allow_origins=ALLOWED_ORIGINS,
        web=SERVE_WEB_INTERFACE,
    )
    
    # Get UI directory
    ui_dir = Path(__file__).parent
    
    # Custom route to serve our UI as the main interface
    @app.get("/", response_class=HTMLResponse)
    async def serve_ui():
        """Serve our custom UI as the main interface."""
        ui_file = ui_dir / "index.html"
        if ui_file.exists():
            with open(ui_file, 'r', encoding='utf-8') as f:
                return HTMLResponse(content=f.read())
        else:
            return HTMLResponse("<h1>UI not found</h1><p>Please ensure index.html exists in the ui directory.</p>")
    
    # Route to serve CSS files
    @app.get("/css/{file_name}")
    async def serve_css(file_name: str):
        """Serve CSS files."""
        css_file = ui_dir / "css" / file_name
        if css_file.exists():
            return FileResponse(str(css_file), media_type="text/css")
        else:
            raise HTTPException(status_code=404, detail="CSS file not found")
    
    # Route to serve JS files
    @app.get("/js/{file_name}")
    async def serve_js(file_name: str):
        """Serve JavaScript files."""
        js_file = ui_dir / "js" / file_name
        if js_file.exists():
            return FileResponse(str(js_file), media_type="application/javascript")
        else:
            raise HTTPException(status_code=404, detail="JS file not found")
    
    # Route to serve other static assets
    @app.get("/assets/{file_path:path}")
    async def serve_assets(file_path: str):
        """Serve static assets."""
        asset_file = ui_dir / "assets" / file_path
        if asset_file.exists():
            return FileResponse(str(asset_file))
        else:
            raise HTTPException(status_code=404, detail="Asset not found")
    
    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        logger.info("Health check requested")
        return {"status": "healthy", "service": "startup-evaluation-ui"}
    
    # Add agent info endpoint
    @app.get("/api/agent-info")
    async def get_agent_info():
        """Get information about the available agent."""
        logger.info("Agent info requested")
        return {
            "agent_name": "master_agent",
            "description": "Comprehensive startup evaluation system",
            "capabilities": [
                "PDF processing and content extraction",
                "Founder team verification",
                "Competitive landscape analysis", 
                "Business KPI validation"
            ],
            "endpoints": {
                "run_sse": "/run_sse",
                "sessions": "/sessions"
            }
        }
    
    # Add file upload endpoint
    @app.post("/api/upload")
    async def upload_file(file: UploadFile = File(...)):
        """Handle PDF file upload and start agent processing."""
        try:
            logger.info(f"Received file upload: {file.filename}")
            
            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Only PDF files are allowed")
            
            # Generate unique filename
            import uuid
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            # Save uploaded file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            logger.info(f"File saved to: {file_path}")
            
            # Return file info for frontend to use in agent call
            return JSONResponse({
                "success": True,
                "filename": file.filename,
                "file_path": file_path,
                "unique_filename": unique_filename,
                "message": "File uploaded successfully"
            })
            
        except Exception as e:
            logger.error(f"File upload error: {e}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    # TODO: Session creation is handled by ADK automatically
    # # Add session creation endpoint
    # @app.post("/api/create-session")
    # async def create_session_endpoint(request: Request):
    #     """Create a session with the correct app_name."""
    #     try:
    #         body = await request.json()
    #         user_id = body.get("user_id")
    #         session_id = body.get("session_id")
    #         
    #         if not user_id or not session_id:
    #             raise HTTPException(status_code=400, detail="user_id and session_id are required")
    #         
    #         # Create session with our app name - handled by ADK internally
    #         # await session_service.create_session(
    #         #     app_name=APP_NAME,
    #         #     user_id=user_id,
    #         #     session_id=session_id
    #         # )
    #         
    #         logger.info(f"Session info: App='{APP_NAME}', User='{user_id}', Session='{session_id}'")
    #         return {"status": "success", "app_name": APP_NAME, "user_id": user_id, "session_id": session_id}
    #         
    #     except Exception as e:
    #         logger.error(f"Session info error: {e}")
    #         return {"status": "error", "message": str(e)}

    # Add test endpoint to debug ADK requests
    @app.post("/api/test-adk")
    async def test_adk_format(request: Request):
        """Test endpoint to see what format ADK expects."""
        body = await request.json()
        logger.info(f"Test ADK request received: {body}")
        return {"received": body, "status": "success"}
    
    return app

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("🚀 Startup Evaluation System - ADK FastAPI Server")
    print("="*70)
    print(f"🤖 Agent Directory: {AGENT_DIR}")
    print(f"💾 Session Database: {SESSION_DB_URL}")
    print(f"🌐 Server URL: http://localhost:{PORT}")
    print(f"🎨 Custom UI: http://localhost:{PORT}/")
    if not SERVE_WEB_INTERFACE:
        print("🛠️  ADK Dashboard: Disabled (using custom UI instead)")
    print(f"📡 SSE Endpoint: http://localhost:{PORT}/run_sse")
    print(f"📁 Upload Directory: {UPLOAD_DIR}")
    print("="*70)
    print("📚 Available endpoints:")
    print("  GET  /              - Custom startup evaluation UI")
    print("  GET  /css/*         - UI stylesheets")
    print("  GET  /js/*          - UI JavaScript files")
    print("  POST /api/upload    - Upload PDF files") 
    print("  POST /run_sse       - Run agent with Server-Sent Events")
    print("  GET  /sessions      - List sessions")
    print("  GET  /health        - Health check")
    print("  GET  /api/agent-info - Agent information")
    print("="*70)
    print("💡 To use with frontend:")
    print("  1. Upload PDF files through the UI (saved to uploaded/ folder)")
    print("  2. Agent processes PDF from file system (no base64 encoding)")
    print("  3. Agent runs are streamed via Server-Sent Events")
    print("  4. Results are automatically displayed in the UI")
    print("="*70 + "\n")

    # Create and run the app
    app = create_app()
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=PORT,
        log_level="debug",  # More verbose logging
        access_log=True,    # Show all HTTP requests
        reload=False        # Set to True for development
    )

if __name__ == "__main__":
    main()

def generate_mock_results(process_id):
    """Generate mock analysis results."""
    return {
        'executive': """# Executive Summary

## Overall Assessment: **B+ (Promising with Key Areas for Improvement)**

Our AI-powered analysis has evaluated your startup across multiple dimensions. The company shows strong potential with a solid founding team and innovative approach to the market.

### Key Strengths
- **Experienced founding team** with relevant industry background
- **Large addressable market** with growing demand
- **Unique value proposition** that differentiates from competitors
- **Solid financial foundation** with realistic projections

### Areas for Improvement
- **Go-to-market strategy** needs refinement
- **Customer acquisition costs** are above industry average
- **Technical team** could benefit from additional senior talent

### Investment Recommendation
**PROCEED WITH CAUTION** - Strong fundamentals but execution risks present.""",

        'founders': """# Founder Profile Analysis

## Team Composition

### CEO - John Smith
- **Background**: 8 years at Google, 3 years at early-stage startup
- **Education**: Stanford CS, Wharton MBA
- **Network Score**: 9/10 (Strong Silicon Valley connections)
- **Leadership Experience**: Led 50+ person engineering team
- **Previous Exit**: Co-founded TechCorp (acquired for $50M)

### CTO - Sarah Johnson
- **Background**: Senior Engineer at Netflix and Stripe
- **Education**: MIT Computer Science, PhD in Distributed Systems
- **Technical Expertise**: AI/ML, cloud infrastructure, scalable systems
- **Open Source**: Active contributor, 500+ GitHub commits
- **Publications**: 12 peer-reviewed papers in top-tier conferences

## Team Assessment
✅ **Complementary Skills**: Perfect CEO/CTO dynamic
✅ **Proven Track Record**: Both have successful exits
✅ **Industry Expertise**: Deep understanding of target market
⚠️ **Team Size**: May need additional senior hires for scaling""",

        'competitors': """# Competitive Landscape Analysis

## Market Overview
The startup operates in a $12B market growing at 15% CAGR, with increasing demand for AI-powered solutions.

## Direct Competitors

### Market Leader: CompanyA
- **Market Share**: 35%
- **Funding**: $150M Series D
- **Strengths**: Brand recognition, extensive partner network
- **Weaknesses**: Legacy technology stack, high customer churn
- **Threat Level**: HIGH

### Fast-Growing Challenger: CompanyB
- **Market Share**: 18%
- **Funding**: $75M Series C
- **Strengths**: Modern architecture, aggressive pricing
- **Weaknesses**: Limited enterprise features, small team
- **Threat Level**: MEDIUM

## Competitive Positioning
| Factor | Our Startup | CompanyA | CompanyB |
|--------|-------------|-----------|-----------|
| Technology | ✅ Modern AI | ❌ Legacy | ⚠️ Adequate |
| Pricing | ✅ Competitive | ❌ Expensive | ✅ Low |
| Features | ⚠️ Growing | ✅ Complete | ❌ Limited |
| Market Presence | ❌ New | ✅ Established | ⚠️ Growing |

## Strategic Advantages
1. **AI-First Architecture**: Next-generation technology foundation
2. **Agile Development**: Faster feature development cycle
3. **Cost Structure**: More efficient operations enable better pricing""",

        'kpis': """# KPI Analysis & Validation

## Financial Performance

### Revenue Metrics
- **Current ARR**: $2.4M (24% above projection)
- **Growth Rate**: 15% MoM (vs. industry avg of 10%)
- **Revenue Per Customer**: $4,800/year
- **Gross Margin**: 78% (excellent for SaaS)

### Unit Economics
- **Customer Acquisition Cost (CAC)**: $1,200
- **Lifetime Value (LTV)**: $14,400
- **LTV/CAC Ratio**: 12:1 ✅ (Target: >3:1)
- **Payback Period**: 8 months ✅ (Target: <18 months)

## Operational Metrics

### Customer Success
- **Monthly Churn Rate**: 3.2% (vs. industry avg 5.4%)
- **Net Revenue Retention**: 118%
- **Customer Satisfaction (NPS)**: 52 (Excellent)
- **Support Ticket Resolution**: 4.2 hours avg

### Product Adoption
- **Daily Active Users**: 12,500
- **Feature Adoption Rate**: 73%
- **Time to Value**: 12 days (industry avg: 30 days)

## Market Size Validation
- **TAM**: $12B ✅ (Validated against 3 industry reports)
- **SAM**: $3.2B ✅ (Conservative estimate)
- **SOM**: $156M ✅ (Achievable with current strategy)

## Risk Factors
⚠️ **Customer Concentration**: Top 3 customers = 45% of revenue
⚠️ **Burn Rate**: $280K/month (18 months runway remaining)
✅ **Product-Market Fit**: Strong indicators present""",

        'full': """# Complete Startup Evaluation Report

*Generated by AI Multi-Agent Analysis System*

---

## Executive Summary
[See Executive Summary tab for detailed overview]

## Methodology
This analysis was conducted using our proprietary multi-agent AI system that evaluates startups across four key dimensions:

1. **Founding Team Assessment** - Background verification and team dynamics
2. **Competitive Intelligence** - Market positioning and competitive advantages  
3. **Financial Analysis** - KPI validation and unit economics
4. **Market Validation** - TAM/SAM/SOM analysis and demand validation

## Detailed Findings

### 1. Team Analysis
[See Founder Profile tab for complete analysis]

**Key Insights:**
- Strong complementary skill sets between CEO and CTO
- Proven track record with previous successful exit
- Industry expertise in target market
- May need additional senior hires for scaling

### 2. Market & Competition
[See Competitive Analysis tab for complete analysis]

**Key Insights:**
- Large addressable market with strong growth trajectory
- Competitive landscape dominated by legacy players
- Clear differentiation through AI-first approach
- Opportunity for disruptive market entry

### 3. Financial Performance
[See KPI Analysis tab for complete analysis]

**Key Insights:**
- Strong unit economics with healthy LTV/CAC ratio
- Revenue growing faster than industry average
- Gross margins excellent for SaaS business
- Some concentration risk in customer base

## Investment Thesis

### Bull Case
- **Experienced team** with domain expertise and successful track record
- **Large market opportunity** with clear demand drivers
- **Differentiated technology** providing competitive moat
- **Strong unit economics** demonstrating scalable business model
- **Early traction** with growing customer base and revenue

### Bear Case
- **Intense competition** from well-funded incumbents
- **Customer concentration risk** with top customers representing large portion of revenue
- **Execution risk** in scaling team and operations
- **Market timing risk** if AI adoption slower than expected

## Strategic Recommendations

### Short Term (0-6 months)
1. **Expand sales team** to reduce customer acquisition costs
2. **Diversify customer base** to reduce concentration risk
3. **Enhance product features** to increase competitive differentiation
4. **Secure bridge funding** to extend runway

### Medium Term (6-18 months)
1. **Scale engineering team** with senior hires
2. **Expand into adjacent markets** to increase TAM
3. **Develop strategic partnerships** for distribution
4. **Prepare for Series B** fundraising

### Long Term (18+ months)
1. **International expansion** to capture global market
2. **Product platform evolution** to serve broader use cases
3. **Consider strategic acquisitions** to accelerate growth
4. **IPO preparation** if growth trajectory continues

## Risk Mitigation

### Technical Risks
- **Mitigation**: Hire additional senior engineers, implement robust testing
- **Monitoring**: Code quality metrics, system reliability measures

### Market Risks  
- **Mitigation**: Diversify customer segments, build strategic partnerships
- **Monitoring**: Market share tracking, customer satisfaction scores

### Financial Risks
- **Mitigation**: Extend runway through bridge funding, optimize burn rate
- **Monitoring**: Monthly burn analysis, revenue predictability metrics

## Conclusion

This startup presents a **STRONG INVESTMENT OPPORTUNITY** with experienced founders, innovative technology, and attractive market dynamics. While execution risks exist, the potential upside is significant given the large market opportunity and differentiated approach.

**Recommended Action**: Proceed with due diligence and term sheet negotiations.

---

*This report was generated using AI analysis. Please conduct additional due diligence before making investment decisions.*"""
    }

if __name__ == "__main__":
    main()
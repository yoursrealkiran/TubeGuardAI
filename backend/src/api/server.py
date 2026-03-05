import uuid
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from opentelemetry import trace # For manual tracing of the Graph logic

# ========== STEP 1: LOAD ENVIRONMENT & TELEMETRY ==========
from dotenv import load_dotenv
load_dotenv(override=True)

from backend.src.api.telemetry import setup_telemetry, tracer
setup_telemetry() 

# ========== STEP 2: IMPORTS ==========
from backend.src.graph.workflow import app as compliance_graph

# Configure standard logging to feed into the instrumented "api-server" logger
logger = logging.getLogger("api-server")

app = FastAPI(
    title="Tube Guard AI API",
    description="API for auditing video content against brand compliance rules.",
    version="1.0.0"
)

# ========== STEP 3: MODELS ==========

class AuditRequest(BaseModel):
    video_url: str

class ComplianceIssue(BaseModel):
    category: str
    severity: str
    description: str

class AuditResponse(BaseModel):
    session_id: str
    video_id: str
    status: str
    final_report: str
    compliance_results: List[ComplianceIssue]

# ========== STEP 4: ENDPOINTS ==========

@app.post("/audit", response_model=AuditResponse)
async def audit_video(request: AuditRequest):
    session_id = str(uuid.uuid4())
    video_id_short = f"vid_{session_id[:8]}"
    
    # START MANUAL SPAN: This groups all logs and DB calls under one 'Workflow' event in Azure
    with tracer.start_as_current_span("Execute-Compliance-Graph") as span:
        # Add metadata to the Azure trace
        span.set_attribute("video.url", request.video_url)
        span.set_attribute("video.session_id", session_id)

        logger.info(f"Starting audit for {request.video_url} [Session: {session_id}]")

        initial_inputs = {
            "video_url": request.video_url,
            "video_id": video_id_short,
            "compliance_results": [],
            "errors": []
        }

        try:
            # Execute LangGraph asynchronously
            final_state = await compliance_graph.ainvoke(initial_inputs)
            
            # Tag the span with the result
            final_status = final_state.get("final_status", "UNKNOWN")
            span.set_attribute("compliance.status", final_status)
            
            logger.info(f"Audit Complete. Status: {final_status}")

            return AuditResponse(
                session_id=session_id,
                video_id=final_state.get("video_id"),
                status=final_status,
                final_report=final_state.get("final_report", "No report generated."),
                compliance_results=final_state.get("compliance_results", [])
            )

        except Exception as e:
            # Record the failure in Azure Application Insights
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            logger.error(f"Audit Failed for {video_id_short}: {str(e)}")
            
            raise HTTPException(
                status_code=500,
                detail=f"Workflow Execution Failed: {str(e)}"
            )
        

# ========== HEALTH CHECK ENDPOINT ==========
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Tube Guard AI"}
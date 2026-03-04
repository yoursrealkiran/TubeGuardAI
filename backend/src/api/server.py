import uuid        # Generate unique session IDs
import logging     # Application logging
from fastapi import FastAPI, HTTPException  
from pydantic import BaseModel  
from typing import List, Optional  



# ========== STEP 1: LOAD ENVIRONMENT VARIABLES ==========
# CRITICAL: Must happen BEFORE importing modules that need env vars
from dotenv import load_dotenv
load_dotenv(override=True)  



# ========== STEP 2: INITIALIZE TELEMETRY ==========
from backend.src.api.telemetry import setup_telemetry
setup_telemetry()  
# ☝️ "Activates the sensors" - starts tracking all API activity
# Must happen AFTER load_dotenv() but BEFORE creating FastAPI app


# ========== STEP 3: IMPORT WORKFLOW GRAPH ==========
from backend.src.graph.workflow import app as compliance_graph
# Imports your LangGraph workflow (Indexer → Auditor)
# Renamed to 'compliance_graph' to avoid confusion with FastAPI's 'app'


# ========== STEP 4: CONFIGURE LOGGING ==========
logging.basicConfig(level=logging.INFO)  
# Sets default log level (INFO = important events, not debug spam)

logger = logging.getLogger("api-server")  
# Creates named logger for this module


# ========== STEP 5: CREATE FASTAPI APPLICATION ==========
app = FastAPI(
    # Metadata for auto-generated API documentation (Swagger UI)
    title="Tube Guard AI API",
    description="API for auditing video content against brand compliance rules.",
    version="1.0.0"
)
# FastAPI automatically creates:
# - Interactive docs at http://localhost:8000/docs
# - OpenAPI schema at http://localhost:8000/openapi.json


# ========== STEP 6: DEFINE DATA MODELS (PYDANTIC) ==========

# --- REQUEST MODEL ---
class AuditRequest(BaseModel):
    
    video_url: str  # Required string field


# --- NESTED MODEL ---
class ComplianceIssue(BaseModel):

    category: str      # Example: "Misleading Claims"
    severity: str      # Example: "CRITICAL"
    description: str   # Example: "Absolute guarantee detected at 00:32"


# --- RESPONSE MODEL ---
class AuditResponse(BaseModel):

    session_id: str                           # Unique audit session ID
    video_id: str                             # Shortened video identifier
    status: str                               # PASS or FAIL
    final_report: str                         # AI-generated summary
    compliance_results: List[ComplianceIssue] # List of violations (can be empty)


# ========== STEP 7: DEFINE MAIN ENDPOINT ==========
@app.post("/audit", response_model=AuditResponse)
# ↑ @app.post = Decorator that registers this function as a POST endpoint
# ↑ "/audit" = URL path (http://localhost:8000/audit)
# ↑ response_model = Tells FastAPI to validate response matches AuditResponse

async def audit_video(request: AuditRequest):
    # ========== GENERATE SESSION ID ==========
    session_id = str(uuid.uuid4())  
    # Creates unique ID like: "ce6c43bb-c71a-4f16-a377-8b493502fee2"
    
    video_id_short = f"vid_{session_id[:8]}"  
    # Takes first 8 characters: "vid_ce6c43bb"
    # Easier to reference in logs/UI than full UUID
    
    # ========== LOG INCOMING REQUEST ==========
    logger.info(f"Received Audit Request: {request.video_url} (Session: {session_id})")
    # Example output: "Received Audit Request: https://youtu.be/abc (Session: ce6c43bb...)"

    # ========== PREPARE GRAPH INPUT ==========
    initial_inputs = {
        "video_url": request.video_url,  # From the API request
        "video_id": video_id_short,      # Generated ID
        "compliance_results": [],        # Will be populated by Auditor
        "errors": []                     # Tracks any processing errors
    }

    try:
        # ========== INVOKE LANGGRAPH WORKFLOW ==========
        # This is the SAME logic from main.py - just wrapped in an API
        final_state = compliance_graph.invoke(initial_inputs)
        # ↑ Blocking call - waits for entire workflow to complete
        # ↑ Flow: START → Indexer → Auditor → END
        # ↑ Returns: Final state dictionary with all results
        
        # NOTE: In production, you'd use:
        # await compliance_graph.ainvoke(initial_inputs)
        # ↑ Async version - doesn't block the server while processing
        
        # ========== MAP GRAPH OUTPUT TO API RESPONSE ==========
        return AuditResponse(
            session_id=session_id,
            video_id=final_state.get("video_id"),  
            # .get() safely retrieves value (None if missing)
            
            status=final_state.get("final_status", "UNKNOWN"),  
            # Defaults to "UNKNOWN" if key doesn't exist
            
            final_report=final_state.get("final_report", "No report generated."),
            
            compliance_results=final_state.get("compliance_results", [])
            # Returns empty list [] if no violations
        )
        # FastAPI automatically converts this Pydantic object to JSON

    except Exception as e:
        # ========== ERROR HANDLING ==========
        logger.error(f"Audit Failed: {str(e)}")  
        # Log the error for debugging
        
        raise HTTPException(
            status_code=500,  # 500 = Internal Server Error
            detail=f"Workflow Execution Failed: {str(e)}"
            # Returns this error message to the client
        )


# ========== STEP 8: HEALTH CHECK ENDPOINT ==========
@app.get("/health")
# ↑ GET request at http://localhost:8000/health
def health_check():
    return {"status": "healthy", "service": "Tube Guard AI"}
    # FastAPI automatically converts dict to JSON response



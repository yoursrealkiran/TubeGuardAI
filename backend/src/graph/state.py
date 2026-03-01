import operator
from typing import Annotated, List, Dict, Optional, Any, TypedDict

# Define the schema for single compliance results 
# Error report
class ComplianceIssue(TypedDict):
    category : str
    description : str # Specific detail of vioaltion
    severity : str # CRITICAL | WARNING
    timestamp : Optional[str]

# Define the global graph state
# This defines the state that get passed around in the agentic workflow
class VideoAuditState(TypedDict):
    '''
    Defines the data schema for LangGraph execution content
    '''

    # Input parameters
    video_url : str
    video_id : str

    # Ingestion and extraction data
    local_filr_path : Optional[str]
    video_metadata : Dict[str,Any]
    transcript : Optional[str]
    ocr_text : List[str]

    # Analysis output
    # Store the list of all the violations found by AI
    compliance_results : Annotated[List[ComplianceIssue], operator.add]

    # Final deliverables
    final_status : str # PASS | FAIL
    final_report : str # markdown format

    # System observability
    # errors : API timeouts, system leevel errors
    # lists of system level crashes
    errors : Annotated[List[str], operator.add]
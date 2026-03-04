import os          
import logging      
from azure.monitor.opentelemetry import configure_azure_monitor  



# This separates telemetry logs from main application logs
logger = logging.getLogger("tube-guard-ai-telemetry")



def setup_telemetry():
    
    # ========== STEP 1: RETRIEVE CONNECTION STRING ==========
    # Reads the Azure Monitor connection string from environment variables
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    # ========== STEP 2: CHECK IF CONFIGURED ==========
    if not connection_string:
        # If the environment variable is missing/empty, telemetry won't work
        logger.warning("No Instrumentation Key found. Telemetry is DISABLED.")
        return  

    # ========== STEP 3: CONFIGURE AZURE MONITOR ==========
    try:
        # configure_azure_monitor() does the heavy lifting:
        # 1. Registers automatic instrumentation for:
        #    - HTTP requests (FastAPI endpoints)
        #    - Database calls (Azure Search queries)
        #    - Logging events
        # 2. Starts background thread to send data to Azure
        configure_azure_monitor(
            connection_string=connection_string,  # Where to send data
            logger_name="tube-guard-ai-tracer"   # Optional: custom tracer name
        )
        logger.info(" Azure Monitor Tracking Enabled & Connected!")
        
    except Exception as e:

        logger.error(f"Failed to initialize Azure Monitor: {e}")
        
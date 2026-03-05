import os
import logging
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

# This logger is used for telemetry setup status
logger = logging.getLogger("tube-guard-ai-telemetry")

def setup_telemetry():
    """
    Initializes Azure Monitor OpenTelemetry instrumentation.
    Captures: HTTP requests, SQL/DB calls, and logging.info/error calls.
    """
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    if not connection_string:
        logger.warning("TELEMETRY: No connection string found. Running in local-only mode.")
        return  

    try:
        # configure_azure_monitor automatically instruments FastAPI and standard libraries
        configure_azure_monitor(
            connection_string=connection_string,
            # Linking these specific logger names ensures their output is sent to Azure 'Traces'
            logger_name="api-server" 
        )
        
        # Set the log level for our specific app loggers
        logging.getLogger("api-server").setLevel(logging.INFO)
        
        logger.info("Azure Monitor Tracking Enabled & Connected!")
        
    except Exception as e:
        logger.error(f"Failed to initialize Azure Monitor: {e}")

# Export a tracer for manual spans in the server code
tracer = trace.get_tracer("tube-guard-tracer")
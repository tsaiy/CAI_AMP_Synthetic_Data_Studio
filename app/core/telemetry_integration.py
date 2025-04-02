import time
import functools
import logging
from typing import Callable, Dict, Any, Optional
from app.core.telemetry import telemetry_manager

logger = logging.getLogger("telemetry_integration")

def track_llm_operation(operation_type: str):
    """
    Decorator to track LLM operations and their performance.
    Automatically calculates latency, tracks tokens, and logs errors.
    
    Args:
        operation_type: Type of operation (generate, evaluate, etc.)
    
    Usage:
        @track_llm_operation("generate")
        def generate_response(self, prompt, model_params, ...):
            # Method implementation
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            success = True
            error = None
            request_id = kwargs.get('request_id', None)
            if request_id is None and len(args) >= 5:
                # This assumes request_id is the 5th argument (index 4)
                request_id = args[4]
            
            # Extract model ID based on operation type and structure of args
            if operation_type == "process_single_topic" and len(args) > 1 and hasattr(args[1], 'model_id'):
                # For process_single_topic, args[1] is the model_handler
                model_id = args[1].model_id
                inference_type = getattr(args[1], 'inference_type', 'aws_bedrock')
            else:
                # For other methods, try to get from self
                model_id = getattr(self, 'model_id', 'unknown')
                inference_type = getattr(self, 'inference_type', 'aws_bedrock')
            
            try:
                result = func(self, *args, **kwargs)
                
                # Estimate token counts if possible
                #print("arguments:, ", args[1])
                input_tokens = estimate_token_count(args[0])  # First arg is often the prompt
                #print(result)
                output_tokens = estimate_token_count_for_response(result)
                
                return result
            except Exception as e:
                success = False
                error = str(e)
                raise
            finally:
                # Calculate latency
                latency_ms = (time.time() - start_time) * 1000
                
                # Record operation in telemetry
                if request_id:
                    telemetry_manager.record_llm_operation(
                        request_id=request_id,
                        model_id=model_id,
                        operation_type=operation_type,
                        tokens_input=input_tokens if 'input_tokens' in locals() else None,
                        tokens_output=output_tokens if 'output_tokens' in locals() else None,
                        latency_ms=latency_ms,
                        success=success,
                        error=error,
                        inference_type=inference_type
                    )
                else:
                    logger.warning(f"LLM operation {operation_type} on {model_id} not linked to a request_id")
        
        return wrapper
    return decorator

def track_job(job_type: str):
    """Decorator to track CML job execution."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            request_id = kwargs.get('request_id', None)
            
            # Extract job parameters
            cores = kwargs.get('cores', args[1] if len(args) > 1 else None)
            memory = kwargs.get('memory', args[2] if len(args) > 2 else None)
            
            # Get input size if available
            input_size = None
            if args and hasattr(args[0], 'input_path'):
                input_path = getattr(args[0], 'input_path')
                if input_path:
                    try:
                        with open(input_path, 'r') as f:
                            content = f.read()
                            input_size = len(content)
                    except Exception:
                        pass
            
            try:
                result = func(self, *args, **kwargs)
                
                # Extract job ID from the result if available
                job_id = None
                if isinstance(result, dict) and 'job_id' in result:
                    job_id = result['job_id']
                
                # Record job start if we have a job ID
                if job_id and request_id:
                    metrics_id = telemetry_manager.record_job_start(
                        request_id=request_id,
                        job_id=job_id,
                        job_type=job_type,
                        cpu_cores=cores,
                        memory_mb=memory,
                        input_size=input_size
                    )
                    
                    # Store metrics_id for later reference
                    telemetry_manager.store_job_telemetry_id(job_id, metrics_id)
                
                return result
            except Exception as e:
                logger.error(f"Error starting {job_type} job: {str(e)}")
                raise
        
        return wrapper
    return decorator

def estimate_token_count(text: Optional[str]) -> Optional[int]:
    """
    Estimate the number of tokens in a text string.
    This is a rough approximation - about 4 characters per token for English text.
    
    Args:
        text: The text to estimate token count for
        
    Returns:
        Estimated token count or None if text is None
    """
    if text is None:
        return None
        
    # Simple approximation: ~4 chars per token for English
    return len(text) // 4
def estimate_token_count_for_response(response):
    """Estimate tokens more accurately for various response formats"""
    if response is None:
        return None
    
    total_chars = 0
    
    if isinstance(response, str):
        total_chars = len(response)
    elif isinstance(response, list):
        # For lists of dictionaries (like QA pairs)
        if response and isinstance(response[0], dict):
            # Count characters in all string values
            for item in response:
                for key, value in item.items():
                    if isinstance(value, str):
                        total_chars += len(value)
                    elif isinstance(value, (dict, list)):
                        # Convert nested structures to string
                        total_chars += len(str(value))
        else:
            # For simple lists
            total_chars = sum(len(str(item)) for item in response)
    elif isinstance(response, dict):
        # For dictionaries
        for key, value in response.items():
            if isinstance(value, str):
                total_chars += len(value)
            else:
                total_chars += len(str(value))
    else:
        # Fallback
        total_chars = len(str(response))
    
    # Calculate tokens based on character count
    # Different models have different token ratios
    return total_chars // 4  # Claude's approximate ratio

def record_job_completion(job_id: str, metrics_id: str, status: str, output_size: Optional[int] = None, error: Optional[str] = None):
    """
    Record the completion of a job that was started with @track_job
    
    Args:
        job_id: The job ID
        metrics_id: The metrics ID returned when job was started
        status: The job status (COMPLETED, FAILED, etc.)
        output_size: Size of the output (if available)
        error: Error message (if job failed)
    """
    try:
        telemetry_manager.record_job_end(
            metrics_id=metrics_id,
            status=status,
            output_size=output_size,
            error=error
        )
    except Exception as e:
        logger.error(f"Error recording job completion for job {job_id}: {str(e)}")

def get_request_id_from_headers(headers: Dict[str, str]) -> Optional[str]:
    """
    Extract request ID from FastAPI request headers
    
    Args:
        headers: Request headers dictionary
        
    Returns:
        Request ID or None if not found
    """
    return headers.get("X-Request-ID")
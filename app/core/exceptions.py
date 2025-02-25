from typing import Optional, Dict, Any

class APIError(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class ModelHandlerError(APIError):
    """Errors related to model handling"""
    pass

class InvalidModelError(ModelHandlerError):
    """Invalid model configuration or access errors
    
    Status code 404 (Not Found) is used because:
    - The requested model resource cannot be found or accessed
    - This includes cases where the model exists but cannot be accessed due to configuration
    - Follows REST principles for resource not found scenarios
    """
    def __init__(self, model_id: str, error: str):
        # Extract specific error conditions from AWS error messages
        details = {
            "model_id": model_id,
            "error_type": "invalid_model_error"
        }
        
        if "on-demand throughput isn't supported" in error:
            details["error_subtype"] = "throughput_configuration_error"
            message = (f"Model {model_id} requires an inference profile configuration. "
                      "Please use a model with on-demand throughput support or configure an inference profile.")
        elif "model identifier is invalid" in error:
            details["error_subtype"] = "invalid_identifier_error"
            message = f"Model {model_id} is not a valid model identifier."
        else:
            details["error_subtype"] = "general_model_error"
            message = f"Invalid model configuration for {model_id}: {error}"
            
        super().__init__(
            message=message,
            status_code=404,
            details=details
        )

class JSONParsingError(APIError):
    """Specific exception for JSON parsing failures
    
    Status code 422 (Unprocessable Entity) is used because:
    - The request syntax is valid (unlike 400 Bad Request)
    - The server understands the content type (unlike 415 Unsupported Media Type)
    - But the server cannot process the contained instructions/content
    """
    def __init__(self, message: str, raw_text: str, parsing_context: str = ""):
        super().__init__(
            message=f"JSON parsing error: {message}",
            status_code=422,  # Unprocessable Entity
            details={
                "parsing_context": parsing_context,
                "raw_text_sample": raw_text[:500] if raw_text else "No text provided",
                "error_type": "json_parsing_error"
            }
        )
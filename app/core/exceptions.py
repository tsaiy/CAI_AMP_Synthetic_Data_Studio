class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
        
class ModelHandlerError(APIError):
    pass

class InvalidModelError(ModelHandlerError):
    def __init__(self, model_id: str):
        super().__init__(
            message=f"Invalid model identifier: {model_id}",
            status_code=400
        )
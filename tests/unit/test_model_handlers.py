import pytest
from unittest.mock import Mock, patch
from app.core.model_handlers import UnifiedModelHandler, create_handler
from app.models.request_models import ModelParameters
from app.core.exceptions import InvalidModelError
from botocore.exceptions import ClientError

def test_model_handler_initialization():
    model_id = "test.model"
    handler = UnifiedModelHandler(model_id)
    assert handler.model_id == model_id
    assert handler.model_params == ModelParameters()

@pytest.mark.asyncio
async def test_model_handler_response_parsing():
    handler = UnifiedModelHandler("test.model")
    test_response = '[{"question": "test?", "solution": "test!"}]'
    parsed = handler._extract_json_from_text(test_response)
    assert len(parsed) == 1
    assert parsed[0]["question"] == "test?"

def test_invalid_model_error():
    error_response = {'Error': {'Code': 'ValidationException', 'Message': 'model identifier is invalid'}}
    mock_bedrock_client = Mock()
    mock_bedrock_client.converse.side_effect = ClientError(error_response, 'ConvokeModel')
    handler = UnifiedModelHandler("invalid.model", bedrock_client=mock_bedrock_client)
    with pytest.raises(InvalidModelError):
        handler.generate_response("test")

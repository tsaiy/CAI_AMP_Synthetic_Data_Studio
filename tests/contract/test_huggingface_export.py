# tests/contract/test_huggingface_export.py
import pytest
from unittest.mock import patch, Mock, MagicMock
import os
import json
from app.services.export_results import Export_Service
from app.models.request_models import Export_synth, HFConfig
from datasets import Dataset, Features, Value
from app.core.exceptions import APIError
from huggingface_hub import HfApi, HfFolder
from pathlib import Path

class MockDatabaseManager:
    """Mock database manager for testing"""
    def __init__(self):
        self.metadata = {}
    
    def get_metadata_by_filename(self, filename):
        return {
            "doc_paths": None,
            "topics": json.dumps(["topic1"]),
            "input_path": None,
            "generate_file_name": "test.json"
        }
    
    def update_hf_path(self, file_name, hf_path):
        self.metadata[file_name] = hf_path
        return True

@pytest.fixture
def mock_json_data():
    return [
        {
            "Seeds": "topic1",
            "Prompt": "test question?",
            "Completion": "test solution"
        }
    ]

@pytest.fixture
def mock_file(tmp_path, mock_json_data):
    file_path = tmp_path / "test.json"
    with open(file_path, "w") as f:
        json.dump(mock_json_data, f)
    return str(file_path)

@pytest.fixture
def export_service():
    service = Export_Service()
    service.db = MockDatabaseManager()
    return service

def test_huggingface_export_contract(export_service, mock_file):
    config = Export_synth(
        export_type=["huggingface"],
        file_path=mock_file,
        output_key="Prompt",
        output_value="Completion",
        hf_config=HFConfig(
            hf_repo_name="test-repo",
            hf_username="test-user",
            hf_token="test-token"
        )
    )

    # Create all necessary mocks
    mock_hf_api = Mock(spec=HfApi)
    mock_hf_folder = Mock(spec=HfFolder)
    mock_dataset = Mock(spec=Dataset)
    mock_dataset_instance = Mock(spec=Dataset)
    mock_features = Mock(spec=Features)

    # Setup mock dataset
    mock_dataset_instance.push_to_hub = Mock()
    mock_dataset.from_list.return_value = mock_dataset_instance

    # Setup mock features
    mock_features.return_value = {
        "Seeds": "string",
        "Prompt": "string",
        "Completion": "string"
    }

    with patch('app.services.export_results.HfApi', return_value=mock_hf_api), \
         patch('app.services.export_results.HfFolder', mock_hf_folder), \
         patch('app.services.export_results.Dataset', mock_dataset), \
         patch('app.services.export_results.Features', return_value=mock_features):

        result = export_service.export(config)

        # Verify HuggingFace interactions
        mock_hf_folder.save_token.assert_called_once_with(config.hf_config.hf_token)
        mock_dataset_instance.push_to_hub.assert_called_once()

        # Verify result structure
        assert isinstance(result, dict)
        assert "huggingface" in result
        assert f"https://huggingface.co/datasets/{config.hf_config.hf_username}/{config.hf_config.hf_repo_name}" == result["huggingface"]

def test_export_with_invalid_file(export_service):
    config = Export_synth(
        export_type=["huggingface"],
        file_path="nonexistent.json",
        output_key="Prompt",
        output_value="Completion",
        hf_config=HFConfig(
            hf_repo_name="test-repo",
            hf_username="test-user",
            hf_token="test-token"
        )
    )

    with pytest.raises(APIError) as exc_info:
        export_service.export(config)
    
    assert "File not found" in str(exc_info.value)

def test_create_dataset_structure(export_service, mock_file):
    records = [
        {
            "Seeds": "topic1",
            "Prompt": "test question?",
            "Completion": "test solution"
        }
    ]
    
    mock_dataset = Mock(spec=Dataset)
    mock_dataset_instance = Mock(spec=Dataset)
    mock_dataset.from_list.return_value = mock_dataset_instance
    
    with patch('app.services.export_results.Dataset', mock_dataset), \
         patch('app.services.export_results.Features') as mock_features:
        
        mock_features.return_value = {
            "Seeds": "string",
            "Prompt": "string",
            "Completion": "string"
        }
        
        dataset = export_service._create_dataset(
            records=records,
            output_key="Prompt",
            output_value="Completion",
            file_path=mock_file
        )
        
        assert dataset is not None
        mock_dataset.from_list.assert_called_once()

@pytest.fixture
def cleanup_files():
    yield
    # Cleanup any test files after tests
    test_files = ['metadata.db', 'metadata.db-shm', 'metadata.db-wal']
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
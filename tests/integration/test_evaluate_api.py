import pytest
from unittest.mock import patch, Mock
import json
from fastapi.testclient import TestClient
from app.main import app, db_manager
client = TestClient(app)

# Dummy CML client for testing purposes
class MockJobRun:
    def __init__(self, job_id, creator_name="test_user"):
        self.job_id = job_id
        self.creator = Mock()
        self.creator.name = creator_name

class MockCMLClient:
    def __init__(self):
        self.jobs = {}
        self.job_runs = {}
        self.project_files = {}
    def create_job(self, project_id, body):
        job_id = f"job_{len(self.jobs)+1}"
        self.jobs[job_id] = body
        return Mock(id=job_id)
    def create_job_run(self, request, project_id, job_id):
        job_run = MockJobRun(job_id)
        self.job_runs[job_id] = job_run
        return job_run
    def list_job_runs(self, project_id, job_id, sort=None, page_size=None):
        job_run = self.job_runs.get(job_id)
        resp = Mock()
        resp.job_runs = [job_run] if job_run else []
        return resp
    def list_jobs(self, project_id, search_filter=None):
        resp = Mock()
        resp.jobs = [Mock(id="base_job_id")]
        return resp
    def get_job(self, project_id, job_id):
        job = Mock()
        job.runtime_identifier = "test_runtime"
        return job

@pytest.fixture
def mock_qa_data():
    return [
        {"Seeds": "python_basics", "Prompt": "What is Python?", "Completion": "Python is a programming language"},
        {"Seeds": "python_basics", "Prompt": "How do you define a function?", "Completion": "Use the def keyword followed by function name"}
    ]

@pytest.fixture
def mock_qa_file(tmp_path, mock_qa_data):
    file_path = tmp_path / "qa_pairs.json"
    with open(file_path, "w") as f:
        json.dump(mock_qa_data, f)
    return str(file_path)

def test_evaluate_endpoint(mock_qa_file):
    # In demo mode our /synthesis/evaluate endpoint returns a dict with keys "status", "result", and "output_path"
    request_data = {
        "use_case": "custom",
        "model_id": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
        "inference_type": "aws_bedrock",
        "import_path": mock_qa_file,
        "is_demo": True,
        "output_key": "Prompt",
        "output_value": "Completion"
    }
    response = client.post("/synthesis/evaluate", json=request_data)
    # Expect 200 and keys as returned by your app
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["status"] == "completed"
    assert "output_path" in res_json
    assert "result" in res_json
    # Do not expect "job_id" in demo mode

def test_evaluation_by_filename():
    # Patch the global db_manager so that get_evaldata_by_filename returns a dummy result.
    db_manager.get_evaldata_by_filename = lambda f: {"evaluate_file_name": "evaluated_qa_pairs.json", "average_score": 4.2}
    response = client.get("/evaluations/evaluated_qa_pairs.json")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["evaluate_file_name"] == "evaluated_qa_pairs.json"

def test_update_evaluation_display_name():
    # Patch the global db_manager.update_evaluate_display_name to return True.
    db_manager.update_evaluate_display_name = lambda f, d: True
    response = client.put("/evaluations/display-name", params={"file_name": "evaluated_qa_pairs.json", "display_name": "Test Evaluation"})
    assert response.status_code == 200
    res_json = response.json()
    assert "message" in res_json

def test_error_handling():
    # Using a nonexistent file causes a FileNotFoundError which our middleware catches and returns with key "error".
    request_data = {
        "use_case": "custom",
        "model_id": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
        "inference_type": "aws_bedrock",
        "import_path": "nonexistent.json",
        "is_demo": True,
        "output_key": "Prompt",
        "output_value": "Completion"
    }
    response = client.post("/synthesis/evaluate", json=request_data)
    # Expect status code in [400,404,500]
    assert response.status_code in [400, 404, 500]
    res_json = response.json()
    # Our middleware returns {"status": "failed", "error": ...}
    assert "error" in res_json

def test_job_handling(mock_qa_file):
    # Test the evaluation endpoint then history.
    response = client.post("/synthesis/evaluate", json={
        "use_case": "custom",
        "model_id": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
        "inference_type": "aws_bedrock",
        "import_path": mock_qa_file,
        "is_demo": True,
        "output_key": "Prompt",
        "output_value": "Completion"
    })
    assert response.status_code == 200
    res_json = response.json()
    # In demo mode we do not return "job_id"
    assert "job_id" not in res_json
    assert "output_path" in res_json
    # Now patch history: return dummy metadata with file name "test.json"
    db_manager.get_all_evaluate_metadata = lambda: [{"evaluate_file_name": "test.json", "average_score": 0.9}]
    response = client.get("/evaluations/history")
    assert response.status_code == 200
    history = response.json()
    assert len(history) > 0

def test_evaluate_with_invalid_model(mock_qa_file):
    response = client.post("/synthesis/evaluate", json={
        "use_case": "custom",
        "model_id": "invalid.model",
        "inference_type": "aws_bedrock",
        "import_path": mock_qa_file,
        "is_demo": True,
        "output_key": "Prompt",
        "output_value": "Completion"
    })
    # Expect error response with status code 400 or 500 and key "error"
    assert response.status_code in [400, 500]
    res_json = response.json()
    assert "error" in res_json

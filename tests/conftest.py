import pytest, os, json, sys
from unittest.mock import Mock
from pathlib import Path

class MockJobRun:
    def __init__(self, job_id="test_job_id"):
        self.job_id = job_id
        self.status = "ENGINE_SUCCEEDED"
        self.creator = Mock(name="test_user")

class MockJob:
    def __init__(self, id="test_job_id"):
        self.id = id
        self.runtime_identifier = "test_runtime"

class MockProjectFile:
    def __init__(self, file_size=1024):
        self.file_size = file_size

class MockCMLClient:
    def __init__(self):
        self.jobs = {}
        self.job_runs = {}
        self.project_files = {}
    def list_jobs(self, project_id, search_filter=None):
        return Mock(jobs=[MockJob()])
    def get_job(self, project_id, job_id):
        return MockJob()
    def create_job(self, project_id, body):
        return MockJob()
    def create_job_run(self, request, project_id, job_id):
        return MockJobRun(job_id)
    def list_job_runs(self, project_id, job_id, sort=None, page_size=None):
        return Mock(job_runs=[MockJobRun(job_id)])
    def list_project_files(self, project_id, file_path):
        return Mock(files=[MockProjectFile()])

def get_mock_cml_env():
    return {
        "CDSW_PROJECT_ID": "test_project",
        "IS_COMPOSABLE": "true",
        "CDSW_DOMAIN": "test.domain",
        "CDSW_API_KEY": "test_key"
    }

from unittest.mock import patch
import os
mock_cmlapi = Mock()
from tests.mocks import mock_cmlapi as mca
mock_cmlapi.default_client = mca.default_client
sys.modules['cmlapi'] = mock_cmlapi
from fastapi.staticfiles import StaticFiles
sys.modules['fastapi.staticfiles'] = Mock(StaticFiles=Mock(return_value=Mock()))

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    for key, value in get_mock_cml_env().items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr('os.path.exists', lambda x: True if 'client/dist' in str(x) else Path(x).exists())

@pytest.fixture(autouse=True)
def mock_cml_environment(monkeypatch):
    mock_client = MockCMLClient()
    monkeypatch.setattr('cmlapi.default_client', lambda: mock_client)
    return mock_client

@pytest.fixture
def cml_env():
    return get_mock_cml_env()

@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

@pytest.fixture
def mock_json_file(tmp_path):
    content = [
        {"input": "Test question 1?"},
        {"input": "Test question 2?"}
    ]
    file_path = tmp_path / "test.json"
    with open(file_path, "w") as f:
        json.dump(content, f)
    return str(file_path)

@pytest.fixture
def mock_pdf_file(tmp_path):
    file_path = tmp_path / "transformers.pdf"
    with open(file_path, "wb") as f:
        f.write(b"%PDF-1.4\n%mock pdf content")
    return str(file_path)

@pytest.fixture
def upload_dir(tmp_path):
    upload_path = tmp_path / "document_upload"
    upload_path.mkdir()
    return upload_path

@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    from tests.mocks import mock_db as mdb
    monkeypatch.setattr('app.core.database.DatabaseManager', lambda: mdb.MockDatabaseManager())

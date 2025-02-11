from unittest.mock import Mock

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

class MockCMLAPI:
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
        
def default_client():
    return MockCMLAPI()

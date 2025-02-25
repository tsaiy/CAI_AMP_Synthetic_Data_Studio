import json

class MockDatabaseManager:
    def __init__(self):
        self.metadata = {}
        self.generation_metadata = []
        self.evaluation_metadata = []

    def get_metadata_by_filename(self, filename):
        return {
            "doc_paths": None,
            "topics": json.dumps(["topic1"]),
            "input_path": None,
            "generate_file_name": filename,
            "model_parameters": json.dumps({"temperature": 0.7}),
            "examples": json.dumps([{"question": "test?", "solution": "test!"}])
        }

    def save_generation_metadata(self, metadata):
        self.generation_metadata.append(metadata)
        return len(self.generation_metadata)

    def save_evaluation_metadata(self, metadata):
        self.evaluation_metadata.append(metadata)
        return len(self.evaluation_metadata)

    def update_job_generate(self, job_name, generate_file_name, local_export_path, timestamp, job_status):
        for meta in self.generation_metadata:
            if meta.get('job_name') == job_name:
                meta.update({
                    'generate_file_name': generate_file_name,
                    'local_export_path': local_export_path,
                    'timestamp': timestamp,
                    'job_status': job_status
                })
                return True
        return False

    def update_job_evaluate(self, job_name, evaluate_file_name, local_export_path, timestamp, average_score, job_status):
        for meta in self.evaluation_metadata:
            if meta.get('job_name') == job_name:
                meta.update({
                    'evaluate_file_name': evaluate_file_name,
                    'local_export_path': local_export_path,
                    'timestamp': timestamp,
                    'average_score': average_score,
                    'job_status': job_status
                })
                return True
        return False

    def update_hf_path(self, file_name, hf_path):
        self.metadata[file_name] = hf_path
        return True

    def get_all_generate_metadata(self):
        return self.generation_metadata

    def get_all_evaluate_metadata(self):
        return self.evaluation_metadata

    def get_evaldata_by_filename(self, filename):
        for meta in self.evaluation_metadata:
            if meta.get("evaluate_file_name") == filename:
                return meta
        return None

    def update_evaluate_display_name(self, file_name, display_name):
        for meta in self.evaluation_metadata:
            if meta.get("evaluate_file_name") == file_name:
                meta["display_name"] = display_name
                return True
        return False

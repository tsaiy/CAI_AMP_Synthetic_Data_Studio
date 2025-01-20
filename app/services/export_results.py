import boto3
import json
import uuid
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
import os
from huggingface_hub import HfApi, HfFolder, Repository
from datasets import Dataset, Features, Value, Sequence
from fastapi import FastAPI, HTTPException
from functools import partial
import math
import asyncio
from app.core.exceptions import APIError
from app.models.request_models import  Export_synth

from app.core.database import DatabaseManager

import logging
from logging.handlers import RotatingFileHandler
import traceback

class Export_Service:

    def __init__(self):
        
        self.db = DatabaseManager() 
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging configuration"""
        os.makedirs('logs', exist_ok=True)
        
        self.logger = logging.getLogger('export_service')
        self.logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # File handler for general logs
        file_handler = RotatingFileHandler(
            'logs/export_service.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # File handler for errors
        error_handler = RotatingFileHandler(
            'logs/export_service_errors.log',
            maxBytes=10*1024*1024,
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)

    def _flatten_results(self, data: Dict) -> List[Dict]:
        """
        Flatten the nested results structure into a list of records
        with category information preserved
        """
        flattened = []
        
        # Handle the results section
        if "results" in data and isinstance(data["results"], dict):
            for category, questions in data["results"].items():
                for question_data in questions:
                    record = {
                        "Topic": category,
                        "Question": question_data["question"],
                        "Solution": question_data["solution"]
                    }
                    flattened.append(record)
        
        return flattened

    def _create_dataset(self, records:List) -> Dataset:
        """Convert the JSON data to a HuggingFace Dataset"""
        # Flatten the nested structure
        #records = self._flatten_results(json_data)
        
        # Define features for the dataset
        features = Features({
            'Topic': Value('string'),
            'question': Value('string'),
            'solution': Value('string')
        })
        
        # Create the dataset
        dataset = Dataset.from_list(records, features=features)
        return dataset


    def export(self,request:Export_synth):
        try:
            export_paths = {}
            file_name = os.path.basename(request.file_path)
            try:
                with open(request.file_path, 'r') as f:
                    output_data = json.load(f)
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")
            
            for export_type in request.export_type:
                if export_type == "s3" and request.s3_config:
                    s3_client = boto3.client("s3")
                    s3_client.put_object(
                        Bucket=request.s3_config.bucket,
                        Key=request.s3_config.key,
                        Body=json.dumps(output_data, indent=2),
                    )
                    export_paths['s3']= f"s3://{request.s3_config.bucket}/{request.s3_config.key}"
                    self.logger.info(f"Results saved to S3: {export_paths['s3']}")

                elif export_type == "huggingface" and request.hf_config:
                    self.logger.info(f"Creating HuggingFace dataset: {request.hf_config.hf_repo_name}")
                    
                    # Set up HuggingFace authentication
                    HfFolder.save_token(request.hf_config.hf_token)
                    
                    # Convert JSON to dataset
                    dataset = self._create_dataset(output_data)
                    print(dataset)
                    
                    # Push to HuggingFace Hub as a dataset
                    repo_id = f"{request.hf_config.hf_username}/{request.hf_config.hf_repo_name}"
                    dataset.push_to_hub(
                        repo_id=repo_id,
                        token=request.hf_config.hf_token,
                        commit_message=request.hf_config.hf_commit_message
                    )

                    export_paths['huggingface'] = f"https://huggingface.co/datasets/{repo_id}"
                    self.logger.info(f"Dataset published to HuggingFace: {export_paths['huggingface']}")
                    self.db.update_hf_path(file_name, export_paths['huggingface'])
                    self.logger.info(f"Generation Metadata updated for hf_path: {export_paths['huggingface']}")
                        
                return export_paths
            
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}", exc_info=True)
            raise APIError(str(e))

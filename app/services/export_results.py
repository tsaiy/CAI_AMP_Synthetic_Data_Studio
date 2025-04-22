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
from app.services.s3_export import export_to_s3

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

    def _create_dataset(self, records:List, output_key, output_value, file_path) -> Dataset:
        """Convert the JSON data to a HuggingFace Dataset"""
        # Flatten the nested structure
        #records = self._flatten_results(json_data)
        row = self.db.get_metadata_by_filename(os.path.basename(file_path))
        
        # Define features for the dataset
        if row["doc_paths"]:
            features = Features({
            'Generated_From': Value('string'),
            output_key: Value('string'),
            output_value: Value('string')
        })
        else:
            
            features = Features({
                'Seeds': Value('string'),
                output_key: Value('string'),
                output_value: Value('string')
            })
        
        # Create the dataset
        dataset = Dataset.from_list(records, features=features)
        return dataset


    def export(self, request: Export_synth):
        try:
            export_paths = {}
            file_name = os.path.basename(request.file_path)
            
            for export_type in request.export_type:
                # S3 Export
                if export_type == "s3":
                    if not request.s3_config:
                        raise HTTPException(status_code=400, detail="S3 configuration required for S3 export")
                    
                    try:
                        # Get bucket and key from request
                        bucket_name = request.s3_config.bucket
                        key = request.s3_config.key or file_name
                        
                        # Override with display_name if provided
                        if request.display_name and not request.s3_config.key:
                            key = f"{request.display_name}.json"
                        
                        
                        
                        
                        create_bucket = getattr(request.s3_config, 'create_if_not_exists', True)
                        
                        s3_result = export_to_s3(
                            file_path=request.file_path,
                            bucket_name=bucket_name,
                            key=key,
                            create_bucket=create_bucket
                        )
                        
                        s3_path = s3_result['s3']
                        self.logger.info(f"Results saved to S3: {s3_path}")
                        
                        # Update database with S3 path
                        self.db.update_s3_path(file_name, s3_path)
                        self.logger.info(f"Generation Metadata updated for s3_path: {s3_path}")
                        
                        export_paths['s3'] = s3_path
                        
                    except Exception as e:
                        self.logger.error(f"Error exporting to S3: {str(e)}", exc_info=True)
                        raise APIError(f"S3 export failed: {str(e)}")
                
                # HuggingFace Export (existing code)
                elif export_type == "huggingface" and request.hf_config:
                    # We still need to read the file for HuggingFace export
                    try:
                        with open(request.file_path, 'r') as f:
                            output_data = json.load(f)
                    except FileNotFoundError:
                        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
                    except json.JSONDecodeError as e:
                        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")
                    
                    self.logger.info(f"Creating HuggingFace dataset: {request.hf_config.hf_repo_name}")
                    
                    # Set up HuggingFace authentication
                    HfFolder.save_token(request.hf_config.hf_token)
                    
                    # Convert JSON to dataset
                    dataset = self._create_dataset(output_data, request.output_key, request.output_value, request.file_path)
                    
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

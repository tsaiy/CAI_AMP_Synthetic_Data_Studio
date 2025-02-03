import boto3
import json
import uuid
import time
from typing import List, Dict, Optional, Tuple
import uuid
from datetime import datetime, timezone
import os
from huggingface_hub import HfApi, HfFolder, Repository
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import math
import asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException
from app.core.exceptions import APIError, InvalidModelError, ModelHandlerError

from app.models.request_models import SynthesisRequest, Example, ModelParameters
from app.core.model_handlers import create_handler
from app.core.prompt_templates import PromptBuilder, PromptHandler
from app.core.config import UseCase, Technique, get_model_family
from app.services.aws_bedrock import get_bedrock_client
from app.core.database import DatabaseManager
from app.services.check_guardrail import ContentGuardrail
from app.services.doc_extraction import DocumentProcessor
import logging
from logging.handlers import RotatingFileHandler
import traceback
import uuid 


class SynthesisService:
    """Service for generating synthetic QA pairs"""
    QUESTIONS_PER_BATCH = 1  # Maximum questions per batch
    MAX_CONCURRENT_TOPICS = 5  # Limit concurrent I/O operations


    def __init__(self):
        # self.bedrock_client = boto3.Session(profile_name='cu_manowar_dev').client(
        #     'bedrock-runtime',
        #     region_name='us-west-2'
        # )
        self.bedrock_client =   get_bedrock_client()
                                
        
        self.db = DatabaseManager() 
        self._setup_logging()
        self.guard = ContentGuardrail()


    def _setup_logging(self):
        """Set up logging configuration"""
        os.makedirs('logs', exist_ok=True)
        
        self.logger = logging.getLogger('synthesis_service')
        self.logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # File handler for general logs
        file_handler = RotatingFileHandler(
            'logs/synthesis_service.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # File handler for errors
        error_handler = RotatingFileHandler(
            'logs/synthesis_service_errors.log',
            maxBytes=10*1024*1024,
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)

    

    def process_single_topic(self, topic: str, model_handler: any, request: SynthesisRequest, num_questions: int) -> Tuple[str, List[Dict], List[str], List[Dict]]:
        """
        Process a single topic to generate questions and solutions.
        Optimized for processing one question at a time, but handles multiple questions.
        
        Args:
            topic: The topic to generate questions for
            model_handler: Handler for the AI model
            request: The synthesis request object
            num_questions: Total number of questions to generate
        
        Returns:
            Tuple containing:
            - topic (str)
            - list of validated QA pairs
            - list of error messages
            - list of output dictionaries with topic information
        """
        topic_results = []
        topic_output = []
        topic_errors = []
        omit_questions = []
    
        # Process one question at a time for the total number requested
        for question_idx in range(num_questions):
            try:
                self.logger.info(f"Processing topic: {topic}, question: {question_idx + 1}/{num_questions}")
                
                # Build prompt for single question
                prompt = PromptBuilder.build_prompt(
                    model_id=request.model_id,
                    use_case=request.use_case,
                    topic=topic,
                    num_questions=1,  # Process one question at a time
                    omit_questions=omit_questions,
                    examples=request.examples or [],
                    technique=request.technique,
                    schema=request.schema,
                    custom_prompt=request.custom_prompt,
                )
                #print(prompt)
                # Generate response
                try:
                    qa_pairs = model_handler.generate_response(prompt)
                except ModelHandlerError as e:
                    self.logger.error(f"ModelHandlerError in generate_response: {str(e)}")
                    raise  # Re-raise ModelHandlerError exceptions
                
                # Process single QA pair
                if qa_pairs and len(qa_pairs) > 0:
                    pair = qa_pairs[0]  # Take first (and should be only) pair
                    
                    if self._validate_qa_pair(pair):
                        validated_pair = {
                            "question": pair["question"],
                            "solution": pair["solution"]
                        }
                        validated_output = {
                            "Topic": topic,
                            "question": pair["question"],
                            "solution": pair["solution"]
                        }
                        
                        topic_results.append(validated_pair)
                        topic_output.append(validated_output)
                        
                        # Update omit_questions list with the new question
                        omit_questions.append(pair["question"])
                        omit_questions = omit_questions[-100:]  # Keep last 100 questions
                        
                        self.logger.info(f"Generated valid QA pair {question_idx + 1} for topic {topic}")
                    else:
                        error_msg = f"Invalid QA pair structure received for topic {topic}, question {question_idx + 1}"
                        self.logger.warning(error_msg)
                        topic_errors.append(error_msg)
                else:
                    error_msg = f"No QA pair generated for topic {topic}, question {question_idx + 1}"
                    self.logger.warning(error_msg)
                    topic_errors.append(error_msg)

            except ModelHandlerError:
                    raise 
                    
            except Exception as e:
                error_msg = f"Error processing topic {topic}, question {question_idx + 1}: {str(e)}"
                self.logger.error(error_msg)
                topic_errors.append(error_msg)
                continue
    
        return topic, topic_results, topic_errors, topic_output
        

       
    
    async def generate_examples(self, request: SynthesisRequest , job_name = None, is_demo: bool = True) -> Dict:
        """Generate examples based on request parameters"""
        try:
            output_key = request.output_key 
            output_value = request.output_value
            st = time.time()
            self.logger.info(f"Starting example generation - Demo Mode: {is_demo}")
            
            # Use default parameters if none provided
            model_params = request.model_params or ModelParameters()
            
            # Create model handler
            self.logger.info("Creating model handler")
            model_handler = create_handler(request.model_id, self.bedrock_client, model_params = model_params, inference_type = request.inference_type, caii_endpoint =  request.caii_endpoint)

            # Limit topics and questions in demo mode
            if request.doc_paths:
                processor = DocumentProcessor(chunk_size=1000, overlap=100)
                paths = request.doc_paths
                topics = []
                for path in paths:
                    chunks = processor.process_document(path)
                    topics.extend(chunks)
                #topics = topics[0:5]
                if request.num_questions<=len(topics):
                    topics = topics[0:request.num_questions]
                    num_questions = 1
                else:
                    num_questions = math.ceil(request.num_questions/len(topics))
                    print(num_questions)
                total_count = request.num_questions
            else:
                if request.topics:
                    topics = request.topics
                    num_questions = request.num_questions
                    total_count = request.num_questions*len(request.topics)
                else:
                    self.logger.error("Generation failed: No topics provided")
                    raise RuntimeError("Invalid input: No topics provided")

               
            # Track results for each topic
            results = {}
            all_errors = []
            final_output = []
            
            # Create thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=self.MAX_CONCURRENT_TOPICS) as executor:
                topic_futures = [
                    loop.run_in_executor(
                        executor,
                        self.process_single_topic,
                        topic,
                        model_handler,
                        request,
                        num_questions
                    )
                    for topic in topics
                ]
                
                # Wait for all futures to complete
                try:
                    completed_topics = await asyncio.gather(*topic_futures)
                except ModelHandlerError as e:
                    self.logger.error(f"Model generation failed: {str(e)}")
                    raise APIError(f"Failed to generate content: {str(e)}")
                
            # Process results
            
            for topic, topic_results, topic_errors, topic_output in completed_topics:
                if topic_errors:
                    all_errors.extend(topic_errors)
                if topic_results and is_demo:
                    results[topic] = topic_results
                if topic_output:
                    final_output.extend(topic_output)

            generation_time = time.time() - st
            self.logger.info(f"Generation completed in {generation_time:.2f} seconds")

            timestamp = datetime.now(timezone.utc).isoformat()
            time_file = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')[:-3] 
            mode_suffix = "test" if is_demo else "final"
            model_name = get_model_family(request.model_id).split('.')[-1]
            file_path = f"qa_pairs_{model_name}_{time_file}_{mode_suffix}.json"
            
            final_output = [{
                                'Seeds': item['Topic'],
                                output_key: item['question'],
                                output_value: item['solution'] }
                             for item in final_output]
            output_path = {}
            try:
                with open(file_path, "w") as f:
                    json.dump(final_output, indent=2, fp=f)
            except Exception as e:
                self.logger.error(f"Error saving results: {str(e)}", exc_info=True)
                
            output_path['local']= file_path

            custom_prompt_str = PromptHandler.get_default_custom_prompt(request.use_case, request.custom_prompt)  
            examples_str = PromptHandler.get_default_example(request.use_case,request.examples)
            schema_str = PromptHandler.get_default_schema(request.use_case, request.schema)
            
            metadata = {
                'timestamp': timestamp,
                'technique': request.technique,
                'model_id': request.model_id,
                'inference_type': request.inference_type,
                'use_case': request.use_case,
                'final_prompt': custom_prompt_str,
                'model_parameters': model_params.model_dump(),
                'generate_file_name': os.path.basename(output_path['local']),
                'display_name': request.display_name,
                'output_path': output_path,
                'num_questions':request.num_questions,
                'topics': topics,
                'examples': examples_str,
                "total_count":total_count,
                'schema': schema_str,
                'doc_paths': request.doc_paths,
                
                'output_key':output_key,
                'output_value':output_value
                }
            
            print("metadata: ",metadata)
            if is_demo:
                
                self.db.save_generation_metadata(metadata)
                return {
                    "status": "completed" if results else "failed",
                    "results": results,
                    "errors": all_errors if all_errors else None,
                    "export_path": output_path
                }
            else:
                # extract_timestamp = lambda filename: '_'.join(filename.split('_')[-3:-1])
                # time_stamp = extract_timestamp(metadata.get('generate_file_name'))
                job_status = "ENGINE_SUCCEEDED"
                generate_file_name = os.path.basename(output_path['local'])
                
                self.db.update_job_generate(job_name,generate_file_name, output_path['local'], timestamp, job_status)
                self.db.backup_and_restore_db()
                return {
                    "status": "completed" if final_output else "failed",
                    "export_path": output_path
                }
        except APIError:
            raise
            
        except Exception as e:
            self.logger.error(f"Generation failed: {str(e)}", exc_info=True)
            if is_demo:
                raise APIError(str(e))  # Let middleware decide status code
            else:
                time_stamp = datetime.now(timezone.utc).isoformat()
                job_status = "ENGINE_FAILED"
                file_name = ''
                output_path = ''
                self.db.update_job_generate(job_name, file_name, output_path, time_stamp, job_status)
                raise  # Just re-raise the original exception


    def _validate_qa_pair(self, pair: Dict) -> bool:
        """Validate a question-answer pair"""
        return (
            isinstance(pair, dict) and
            "question" in pair and
            "solution" in pair and
            isinstance(pair["question"], str) and
            isinstance(pair["solution"], str) and
            len(pair["question"].strip()) > 0 and
            len(pair["solution"].strip()) > 0
        )
    
    async def process_single_input(self, input, model_handler, request):
        try:
            prompt = PromptBuilder.build_generate_result_prompt(
                model_id=request.model_id,
                use_case=request.use_case,
                input=input,
                examples=request.examples or [],
                schema=request.schema,
                custom_prompt=request.custom_prompt,
            )
            try:
                result = model_handler.generate_response(prompt)
            except ModelHandlerError as e:
                self.logger.error(f"ModelHandlerError in generate_response: {str(e)}")
                raise
                    
            return {"question": input, "solution": result}
        
        except ModelHandlerError:
            raise
        except Exception as e:
            self.logger.error(f"Error processing input: {str(e)}")
            raise APIError(f"Failed to process input: {str(e)}")

    async def generate_result(self, request: SynthesisRequest , job_name = None, is_demo: bool = True) -> Dict:
        try:
            self.logger.info(f"Starting example generation - Demo Mode: {is_demo}")
            
                
            # Use default parameters if none provided
            model_params = request.model_params or ModelParameters()
            
            # Create model handler
            self.logger.info("Creating model handler")
            model_handler = create_handler(request.model_id, self.bedrock_client, model_params = model_params, inference_type = request.inference_type, caii_endpoint =  request.caii_endpoint, custom_p = True)

            inputs = []
            file_paths = request.input_path
            for path in file_paths:
                try:
                    with open(path) as f:
                        data = json.load(f)
                        inputs.extend(item.get(request.input_key, '') for item in data)
                except Exception as e:
                    print(f"Error processing {path}: {str(e)}")
            MAX_WORKERS = 5
            
            
            # Create thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # Create futures for each input
                input_futures = [
                    loop.run_in_executor(
                        executor,
                        lambda x: asyncio.run(self.process_single_input(x, model_handler, request)),
                        input
                    )
                    for input in inputs
                ]
                
                # Wait for all futures to complete
                try:
                    final_output = await asyncio.gather(*input_futures)
                except ModelHandlerError as e:
                    self.logger.error(f"Model generation failed: {str(e)}")
                    raise APIError(f"Failed to generate content: {str(e)}")
                
         
            
            
            timestamp = datetime.now(timezone.utc).isoformat()
            time_file = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')[:-3] 
            mode_suffix = "test" if is_demo else "final"
            model_name = get_model_family(request.model_id).split('.')[-1]
            file_path = f"qa_pairs_{model_name}_{time_file}_{mode_suffix}.json"
            input_key = request.output_key or request.input_key
            result = [{
                                
                                input_key: item['question'],
                                request.output_value: item['solution'] }
                             for item in final_output]
            output_path = {}
            try:
                with open(file_path, "w") as f:
                    json.dump(result, indent=2, fp=f)
            except Exception as e:
                self.logger.error(f"Error saving results: {str(e)}", exc_info=True)
                
            

            

            output_path['local']= file_path

            custom_prompt_str = PromptHandler.get_default_custom_prompt(request.use_case, request.custom_prompt)  
            examples_str = PromptHandler.get_default_example(request.use_case,request.examples)
            schema_str = PromptHandler.get_default_schema(request.use_case, request.schema)
            
            metadata = {
                'timestamp': timestamp,
                'technique': request.technique,
                'model_id': request.model_id,
                'inference_type': request.inference_type,
                'use_case': request.use_case,
                'final_prompt': custom_prompt_str,
                'model_parameters': model_params.model_dump(),
                'generate_file_name': os.path.basename(output_path['local']),
                'display_name': request.display_name,
                'output_path': output_path,
                'output_key':request.output_key,
                'output_value':request.output_value,
                'examples': examples_str,
                'input_path': request.input_path,
                "total_count":len(inputs),
                'schema': schema_str
                
            }
            
            
            if is_demo:
                
                self.db.save_generation_metadata(metadata)
                return {
                    "status": "completed" if final_output else "failed",
                    "results": final_output,
                    "export_path": output_path
                }
            else:
                # extract_timestamp = lambda filename: '_'.join(filename.split('_')[-3:-1])
                # time_stamp = extract_timestamp(metadata.get('generate_file_name'))
                job_status = "success"
                generate_file_name = os.path.basename(output_path['local'])
                
                self.db.update_job_generate(job_name,generate_file_name, output_path['local'], timestamp, job_status)
                self.db.backup_and_restore_db()
                return {
                    "status": "completed" if final_output else "failed",
                    "export_path": output_path
                }

        except APIError:
            raise 
        except Exception as e:
            self.logger.error(f"Generation failed: {str(e)}", exc_info=True)
            if is_demo:
                raise APIError(str(e))  # Let middleware decide status code
            else:
                time_stamp = datetime.now(timezone.utc).isoformat()
                job_status = "failure"
                file_name = ''
                output_path = ''
                self.db.update_job_generate(job_name, file_name, output_path, time_stamp, job_status)
                raise  # Just re-raise the original exception




    def get_health_check(self) -> Dict:
        """Get service health status"""
        try:
            test_body = {
                "prompt": "\n\nHuman: test\n\nAssistant: ",
                "max_tokens_to_sample": 1,
                "temperature": 0
            }
            
            self.bedrock_client.invoke_model(
                modelId="anthropic.claude-instant-v1",
                body=json.dumps(test_body)
            )

            status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "SynthesisService",
                "aws_region": self.bedrock_client.meta.region_name
            }
            self.logger.info("Health check passed", extra=status)
            return status

        except Exception as e:
            status = {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "service": "SynthesisService",
                "aws_region": self.bedrock_client.meta.region_name
            }
            self.logger.error("Health check failed", extra=status, exc_info=True)
            return status
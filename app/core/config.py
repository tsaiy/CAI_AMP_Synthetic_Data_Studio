from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request, status
import requests
import json
from fastapi.responses import JSONResponse
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv() 

class UseCase(str, Enum):
    CODE_GENERATION = "code_generation"
    TEXT2SQL = "text2sql"
    CUSTOM = "custom"

class Technique(str, Enum):
    SFT = "sft"
    DPO = "dpo"
    ORPO = "orpo"
    SPIN = "spin"
    KTO = "kto"

class ModelFamily(str, Enum):
    CLAUDE = "claude"
    LLAMA = "llama"
    MISTRAL = "mistral"
    QWEN = "qwen"

class ModelID(str, Enum):
    CLAUDE_V2 = "anthropic.claude-v2"
    CLAUDE_3 = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    CLAUDE_INSTANT = "anthropic.claude-instant-v1"
    LLAMA_8B = "us.meta.llama3-1-8b-instruct-v1:0"
    LLAMA_70B = "us.meta.llama3-1-70b-instruct-v1:0"
    MISTRAL = "mistral.mixtral-8x7b-instruct-v0:1"

class TopicMetadata(BaseModel):
    """Metadata for each topic"""
    name: str
    description: str
    example_questions: List[Dict[str, str]]

class UseCaseMetadata(BaseModel):
    """Metadata for each use case"""
    name: str
    description: str
    topics: Dict[str, TopicMetadata]
    default_examples: List[Dict[str, str]]
    schema: Optional[str] = None


DEFAULT_SQL_SCHEMA = """
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10,2)
);

CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    manager_id INT,
    budget DECIMAL(15,2)
);
"""
bedrock_list = ['us.anthropic.claude-3-5-haiku-20241022-v1:0', 'us.anthropic.claude-3-5-sonnet-20241022-v2:0',
                              'us.anthropic.claude-3-opus-20240229-v1:0','anthropic.claude-instant-v1', 
                              'us.meta.llama3-2-11b-instruct-v1:0','us.meta.llama3-2-90b-instruct-v1:0', 'us.meta.llama3-1-70b-instruct-v1:0', 
                                'mistral.mixtral-8x7b-instruct-v0:1', 'mistral.mistral-large-2402-v1:0',
                                   'mistral.mistral-small-2402-v1:0'  ]

# Detailed use case configurations with examples
USE_CASE_CONFIGS = {
    UseCase.CODE_GENERATION: UseCaseMetadata(
        name="Code Generation",
        description="Generate programming questions and solutions with code examples",
        topics={
            "python_basics": TopicMetadata(
                name="Python Basics",
                description="Fundamental Python programming concepts",
                example_questions=[
                    {
                        "question": "How do you create a list in Python and add elements to it?",
                        "solution": "Here's how to create and modify a list in Python:\n\n```python\n# Create an empty list\nmy_list = []\n\n# Add elements using append\nmy_list.append(1)\nmy_list.append(2)\n\n# Create a list with initial elements\nmy_list = [1, 2, 3]\n```"
                    }
                ]
            ),
            "data_structures": TopicMetadata(
                name="Data Structures",
                description="Common data structures implementation and usage",
                example_questions=[
                    {
                        "question": "How do you implement a stack using a list in Python?",
                        "solution": "Here's how to implement a basic stack:\n\n```python\nclass Stack:\n    def __init__(self):\n        self.items = []\n    \n    def push(self, item):\n        self.items.append(item)\n    \n    def pop(self):\n        if not self.is_empty():\n            return self.items.pop()\n    \n    def is_empty(self):\n        return len(self.items) == 0\n```"
                    }
                ]
            ),
            # Add more topics...
        },
        default_examples=[
            {
                "question": "How do you read a CSV file into a pandas DataFrame?",
                "solution": "You can use pandas.read_csv(). Here's an example:\n\n```python\nimport pandas as pd\ndf = pd.read_csv('data.csv')\n```"
            },
            {
                "question": "How do you write a function in Python?",
                "solution": "Here's how to define a function:\n\n```python\ndef greet(name):\n    return f'Hello, {name}!'\n\n# Example usage\nresult = greet('Alice')\nprint(result)  # Output: Hello, Alice!\n```"
            }
        ],
        
        schema=None 
    ),
    
    UseCase.TEXT2SQL: UseCaseMetadata(
        name="Text to SQL",
        description="Generate natural language to SQL query pairs",
        topics={
            "basic_queries": TopicMetadata(
                name="Basic Queries",
                description="Simple SELECT, INSERT, UPDATE, and DELETE operations",
                example_questions=[
                    {
                        "question": "How do you select all employees from the employees table?",
                        "solution": "Here's the SQL query:\n```sql\nSELECT *\nFROM employees;\n```"
                    }
                ]
            ),
            "joins": TopicMetadata(
                name="Joins",
                description="Different types of JOIN operations",
                example_questions=[
                    {
                        "question": "How do you join employees and departments tables to get employee names with their department names?",
                        "solution": "Here's the SQL query:\n```sql\nSELECT e.name, d.department_name\nFROM employees e\nJOIN departments d ON e.department_id = d.id;\n```"
                    }
                ]
            ),
            # Add more topics...
        },
        default_examples=[
            {
                "question": "Find all employees with salary greater than 50000",
                "solution": "```\nSELECT *\nFROM employees\nWHERE salary > 50000;\n```"
            },
            {
                "question": "Get the average salary by department",
                "solution": "```\nSELECT department_id, AVG(salary) as avg_salary\nFROM employees\nGROUP BY department_id;\n```"
            }
        ],
       
        schema= DEFAULT_SQL_SCHEMA
    )
}

# Model configurations
MODEL_CONFIGS = {
    ModelID.CLAUDE_V2: {"max_tokens": 100000, "max_input_tokens": 100000},
    ModelID.CLAUDE_3: {"max_tokens": 4096, "max_input_tokens": 200000},
    ModelID.CLAUDE_INSTANT: {"max_tokens": 100000, "max_input_tokens": 100000},
    ModelID.LLAMA_8B: {"max_tokens": 4096, "max_input_tokens": 4096},
    ModelID.LLAMA_70B: {"max_tokens": 4096, "max_input_tokens": 4096},
    ModelID.MISTRAL: {"max_tokens": 2048, "max_input_tokens": 2048}
}

def get_model_family(model_id: str) -> ModelFamily:
    if "anthropic.claude" in model_id or "us.anthropic.claude" in model_id:
        return ModelFamily.CLAUDE
    elif "meta.llama" in model_id or "us.meta.llama" in model_id or "meta/llama" in model_id:
        return ModelFamily.LLAMA
    elif "mistral" in model_id or "mistralai/" in model_id:
        return ModelFamily.MISTRAL
    elif 'Qwen' in model_id or 'qwen' in model_id:
        return ModelFamily.QWEN
    else:
        model_name = model_id.split('/')[-1] if '/' in model_id else model_id
        return model_name

def get_available_topics(use_case: UseCase) -> Dict:
    """Get available topics with their metadata for a use case"""
    if use_case not in USE_CASE_CONFIGS:
    
        return {}
    
    
    use_case_config = USE_CASE_CONFIGS[use_case]
    return {
        "use_case": use_case_config.name,
        "description": use_case_config.description,
        "topics": {
            topic_id: {
                "name": metadata.name,
                "description": metadata.description,
                "example_questions": metadata.example_questions
            }
            for topic_id, metadata in use_case_config.topics.items()
        },
        "default_examples": use_case_config.default_examples
    }

def get_examples_for_topic(use_case: UseCase, topic: str) -> List[Dict[str, str]]:
    """Get example questions for a specific topic"""
    use_case_config = USE_CASE_CONFIGS.get(use_case)
    if not use_case_config:
        return []
    
    topic_metadata = use_case_config.topics.get(topic)
    if not topic_metadata:
        return use_case_config.default_examples
    
    return topic_metadata.example_questions


responses = {
    # 4XX Client Errors
    status.HTTP_400_BAD_REQUEST: {
        "description": "Bad Request - Invalid input parameters",
        "content": {
            "application/json": {
                "example": {
                    "status": "failed",
                    "error": "Invalid input: No topics provided"
                }
            }
        }
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Resource not found",
        "content": {
            "application/json": {
                "example": {
                    "status": "failed",
                    "error": "Requested resource not found"
                }
            }
        }
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {
                    "status": "failed",
                    "error": "Invalid request parameters"
                }
            }
        }
    },

    # 5XX Server Errors
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal server error",
        "content": {
            "application/json": {
                "example": {
                    "status": "failed",
                    "error": "Internal server error occurred"
                }
            }
        }
    },
    status.HTTP_503_SERVICE_UNAVAILABLE: {
        "description": "Service temporarily unavailable",
        "content": {
            "application/json": {
                "example": {
                    "status": "failed",
                    "error": "The CAII endpoint is downscaled, please try after >15 minutes"
                }
            }
        }
    },
    status.HTTP_504_GATEWAY_TIMEOUT: {
        "description": "Request timed out",
        "content": {
            "application/json": {
                "example": {
                    "status": "failed",
                    "error": "Operation timed out after specified seconds"
                }
            }
        }
    }
}

JWT_PATH = Path("/tmp/jwt")

def _get_caii_token() -> str:
    if (tok := os.getenv("CDP_TOKEN")):
        return tok
    try:
        payload = json.loads(open(JWT_PATH).read())
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No CDP_TOKEN env‑var and no /tmp/jwt file")
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Malformed /tmp/jwt")

    if not (tok := payload.get("access_token")):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="access_token missing in /tmp/jwt")
    return tok

def caii_check(endpoint: str, timeout: int = 3) -> requests.Response:
    """
    Return the GET /models response if everything is healthy.
    Raise HTTPException on *any* problem.
    """
    if not endpoint:
        raise HTTPException(400, "CAII endpoint not provided")

    token = _get_caii_token()
    url = endpoint.removesuffix("/chat/completions") + "/models"

    try:
        r = requests.get(url,
                         headers={"Authorization": f"Bearer {token}"},
                         timeout=timeout)
    except requests.exceptions.RequestException as exc:
        raise HTTPException(503, f"CAII endpoint unreachable: {exc}")

    if r.status_code in (401, 403):
        raise HTTPException(403, "Token is valid but has no access to this environment")
    if r.status_code == 404:
        raise HTTPException(404, "CAII endpoint or resource not found")
    if 500 <= r.status_code < 600:
        raise HTTPException(503, "CAII endpoint is downscaled; retry in ~15 min")
    if r.status_code != 200:
        raise HTTPException(r.status_code, r.text)

    return r



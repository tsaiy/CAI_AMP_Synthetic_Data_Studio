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

LENDING_DATA_PROMPT = """
        Create profile data for the LendingClub company which specialises in lending various types of loans to urban customers.

        Background:
        LendingClub is a peer-to-peer lending platform connecting borrowers with investors. The dataset captures loan applications, 
        borrower profiles, and outcomes to assess credit risk, predict defaults, and determine interest rates. 


        Loan Record field:

        Each generated record must include the following fields in the exact order provided, with values generated as specified:  

        - loan_amnt: The listed amount of the loan applied for by the borrower. If at some point in time, the credit department 
        reduces the loan amount, then it will be reflected in this value.
        - term: The number of payments on the loan. Values are in months and can be either " 36 months" or " 60 months".
        - int_rate: Interest Rate on the loan
        - installment: The monthly payment owed by the borrower if the loan originates.
        - grade: LC assigned loan grade (Possible values: A, B, C, D, E, F, G)
        - sub_grade: LC assigned loan subgrade (Possible sub-values: 1-5 i.e. A5)
        - emp_title: The job title supplied by the Borrower when applying for the loan.
        - emp_length: Employment length in years. Possible values are between 0 and 10 where 0 means less than one year and 10 
        means ten or more years.
        - home_ownership: The home ownership status provided by the borrower during registration or obtained from the credit report.
        Possible values are: RENT, OWN, MORTGAGE, ANY, OTHER
        - annual_inc: The self-reported annual income provided by the borrower during registration.
        - verification_status: Indicates if income was verified by LC, not verified, or if the income source was verified
        - issue_d: The month which the loan was funded
        - loan_status: Current status of the loan (Possible values: "Fully Paid", "Charged Off")
        - purpose: A category provided by the borrower for the loan request.
        - title: The loan title provided by the borrower
        - dti: A ratio calculated using the borrower’s total monthly debt payments on the total debt obligations, excluding mortgage
        and the requested LC loan, divided by the borrower’s self-reported monthly income.
        - earliest_cr_line: The month the borrower's earliest reported credit line was opened
        - open_acc: The number of open credit lines in the borrower's credit file.
        - pub_rec: Number of derogatory public records
        - revol_bal: Total credit revolving balance
        - revol_util: Revolving line utilization rate, or the amount of credit the borrower is using relative to all available 
        revolving credit.
        - total_acc: The total number of credit lines currently in the borrower's credit file
        - initial_list_status: The initial listing status of the loan. Possible values are: w, f
        - application_type: Indicates whether the loan is an individual application or a joint application with two co-borrowers
        - mort_acc: Number of mortgage accounts.
        - pub_rec_bankruptcies: Number of public record bankruptcies
        - address: The physical address of the person

        In addition to the definitions above, when generating samples, adhere to following guidelines:

        Privacy Compliance guidelines:
        1) Ensure PII from examples such as addresses are not used in the generated data to minimize any privacy concerns. 
        2) Avoid real PII in addresses. Use generic street names and cities.  

        Formatting guidelines:
        1) Use consistent decimal precision (e.g., "10000.00" for loan_amnt).  
        2) Dates (e.g. issue_d, earliest_cr_line) should follow the "Jan-YYYY" format.
        3) term has a leading space before the number of months (i.e. " 36 months")
        4) The address field is a special case where the State zipcode needs to be exactly as specified in the seed instructions. 
        The persons address must follow the format as specified in the examples with the State zipcode coming last.
        5) Any other formatting guidelines that can be inferred from the examples or field definitions but are not listed above.

        Cross-row guidelines:
        1) Generated data should maintain consistency with all statistical parameters and distributions defined in the seed instruction
        across records (e.g., 60% of `term` as " 36 months").

        Cross-column guidelines:
        1) Ensure logical and realistic consistency and correlations between variables. Examples include but not limited to:
        a) Grade/Sub-grade consistency: Sub-grade must match the grade (e.g., "B" grade → "B1" to "B5").  
        b) Interest Rate vs Grade/Subgrade relationship: Higher subgrades (e.g., A5) could have higher `int_rate` than lower subgrades (e.g., A3).  
        c) Mortgage Consistency: `mort_acc` should be 1 or more if `home_ownership` is `MORTGAGE`. 
        d) Open Accounts: `open_acc` ≤ `total_acc`.  

        Data distribution guidelines:
        1) Continuous Variables (e.g., `loan_amnt`, `annual_inc`): Adhere to the mean and standard deviation given in the seed 
        instructions for each variable.
        2) Categorical variables (e.g., `term`, `home_ownership`): Use probability distributions given in the seed instructions 
        (e.g. 60% for " 36 months", 40% for " 60 months").
        3) Discrete Variables (e.g., `pub_rec`, `mort_acc`): Adhere to value ranges and statistical parameters
        provided in the seed instructions.
        4) Any other logical data distribution guidelines that can be inferred from the seed instructions or field definitions 
        and are not specified above. 

        Background knowledge and realism guidelines:
        1) Ensure fields such as interest rates reflect real-world interest rates at the time the loan is issued.
        2) Generate values that are plausible (e.g., `annual_inc` ≤ $500,000 for most `emp_length` ranges).  
        3) Avoid unrealistic values (e.g., `revol_util` as "200%" is unrealistic).  
        4) Ensure that the generated data is realistic and plausible, avoiding extreme or impossible values.
        5) Ensure that the generated data is diverse and not repetitive, avoiding identical or very similar records.
        6) Ensure that the generated data is coherent and consistent, avoiding contradictions or inconsistencies between fields.
        7) Ensure that the generated data is relevant to the LendingClub use case and adheres to the guidelines provided."""



# Synthetic Data Generation Application

An application for generating high-quality synthetic datasets for various fine-tuning techniques. The application currently specializes in code generation and SQL query synthesis, with support for custom use cases.

## Features

### Data Generation
- Support for multiple fine-tuning techniques:
  - Supervised Fine-Tuning (SFT) --> Currently Live
  - PPO (Proximal Policy Optimization) --> WIP
  - ORPO (Odds Ratio Preference Optimization) --> WIP
  - DPO (Direct Preference Optimization) --> WIP
  - KTO (Kahneman-Tversky Optimisation ) --> WIP

### Use Cases
- **Code Generation**: Generate diverse programming question-answer pairs across multiple domains, complete with detailed explanations and working code examples. The system creates scenarios that test both theoretical understanding and practical implementation skills, producing high-quality training data for code-assistance models.
  

- **Text-to-SQL**: This use case allows to generate data as prompt and SQL pair on custom data schemas which can be used to further fine-tune models for enhanced tetx2sql performance on OSS models. 


- **Custom Use Cases**: Flexible framework for implementing additional use cases

### Model Integration
- AWS Bedrock Integration
    - Claude 3 Family (Haiku, Sonnet, Opus)
    - Llama 3 Models
    - Mistral Models
- Cloudera AI Inference (CAII) Support
    - Llama 3 (8B Instruct)
    - Mistral-7B

### Evaluation
- Built-in evaluation capabilities for generated datasets
- Customizable evaluation prompts
- Scoring system with detailed justifications

### Output Mode
- Preview Mode(dislayed on Front-End) for prompts <= 25
- Batch Mode via Cloudera ML Jobs

## Architecture

The application is built using:
- Backend: FastAPI
- Frontend: React
- Database: SQLite (for metadata storage)

## API Endpoints

### Data Generation
- `/synthesis/generate`: Generate synthetic Q&A pairs
- `/synthesis/evaluate`: Evaluate generated examples

### Configuration
- `/model/model_ID`: Get available model configurations
- `/use-cases`: List available use cases
- `/model/parameters`: Get model parameter ranges
- `/{use_case}/gen_prompt`: Get generation prompts
- `/{use_case}/eval_prompt`: Get evaluation prompts

### Management
- `/generations/history`: View generation history
- `/evaluations/history`: View evaluation history
- `/generations/display-name`: Update generation metadata
- `/evaluations/display-name`: Update evaluation metadata

## Usage Examples

### Code Generation Request
```json
{
    "use_case": "code_generation",
    "model_id": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "num_questions": 3,
    "technique": "sft",
    "topics": ["python_basics", "data_structures"],
    "examples": [
        {
            "question": "How do you create a list in Python and add elements to it?",
            "solution": "# Example solution code..."
        }
    ],
    "export_type": ["local", "huggingface"],
    "model_params": {
        "temperature": 0.0,
        "top_p": 1.0,
        "max_tokens": 4096
    }
}
```

### Text-to-SQL Request
```json
{
    "use_case": "text2sql",
    "model_id": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "num_questions": 3,
    "technique": "sft",
    "topics": ["basic_queries", "joins"],
    "schema": "CREATE TABLE users (...)",
    "examples": [
        {
            "question": "How do you select all employees from the employees table?",
            "solution": "SELECT * FROM employees;"
        }
    ],
    "export_type": ["local", "huggingface"],
    "model_params": {
        "temperature": 0.0,
        "top_p": 1.0,
        "max_tokens": 4096
    }
}
```

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables for AWS Bedrock and CAII credentials

4. Start the application(backend):
```bash
uvicorn app.main:app --reload
```

## IMPORTANT
Please read the following before proceeding. This AMP includes or otherwise depends on certain third party software packages. Information about such third party software packages are made available in the notice file associated with this AMP. By configuring and launching this AMP, you will cause such third party software packages to be downloaded and installed into your environment, in some instances, from third parties' websites. For each third party software package, please see the notice file and the applicable websites for more information, including the applicable license terms.

If you do not wish to download and install the third party software packages, do not configure, launch or otherwise use this AMP. By configuring, launching or otherwise using the AMP, you acknowledge the foregoing statement and agree that Cloudera is not responsible or liable in any way for the third party software packages.

Copyright (c) 2024 - Cloudera, Inc. All rights reserved.

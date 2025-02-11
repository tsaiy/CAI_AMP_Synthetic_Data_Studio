# Supervised Finetuning Workflow:

In this workflow we will see how we can create synthetic data for finetuning our models. The users in this workflow can chose from provided templates like.

## Templates

1. **Code Generation**
2. **Text to SQL**
3. **Custom**

The code generation and text2sql are templates which allow users to select from already curated prompts, seeds(more on it below) and examples to produce datasets.

Custom template on the other hand allows users to define everything from scratch and create synthteic dataset for their custom Enterprise use cases.

## Workflow Example: Code Generation

### Home Page
On home Page user can click on Create Datasets to Get Started

<img src="docs/guides/sds_home_page.png" width="600">

### Generate Configuration: In the next step user gets to specify following fields:

1. #### Display Name
2. #### Model Provider: AWS Bedrock or Cloudera AI Inference
3. #### Model ID: Calude , LLAMA , Mistral etc.
4. #### Workflow
        a. Supervised Finetuning :- Generate Prompt and Completion Pairs with or without documents(pdfs, docs, txt etc.)
        b. Custom Data Curation:- Use Input as json array(which can be uploaded) from the user and generate response based on that. In this case user can have their own inputs, instructions and get customised generated output for corresponding input. 
5. #### Files: Input Files user can chose from their project file system for above workflows

<img src="docs/guides/sds_generation.png" width="600">

### Prompt and Model Parameters

#### Prompt:
This step allows user to curate their prompts manuallly, or chose from given templates or let LLM curate a prompt based on their description of use case.

```json
{
"""Write a programming question-pair for the following topic:

Requirements:
- Each solution must include working code examples
- Include explanations with the code
- Follow the same format as the examples
- Ensure code is properly formatted with appropriate indentation"""
}
```

#### Seeds:

This helps LLM diversify dataset user wants to generate. We drew inspiration from **[Self Intruct Paper](https://huggingface.co/papers/2212.10560)**
 , where 175 hand crafted human seed instructions were used to diversify curation of dataset.

 For example, for code generation, seeds can be:
- **Algorithms for Operation Research**
- **Web Development with Flask**
- **PyTorch for Reinforcement Learning**

Similarly for language translation, seeds can be:
- **Poems**
- **Greetings in Formal Communication**
- **Haikus**

#### Model Parameters

We let user decide on following model Parameters:

- **Temperature**
- **TopK**
- **TopP**

#### Dataset Size

<img src="docs/guides/sds_prompt.png" width="600">

### Examples:

In the next step user can specify examples they would want to give for their synthetic dataset generation so that LLM can follow same format and create datasets accordingly.

The examples for code geneartion would be like following:

```json
{
   "question": "How do you read a CSV file into a pandas DataFrame?",
   "solution": """You can use pandas.read_csv(). Here's an example
   
        import pandas as pd
        df = pd.read_csv('data.csv')
        print(df.head())
        print(df.info())
"""
}
```

<img src="docs/guides/sds_examples.png" width="600">


### Summary:

This allows user to finally look at prompt, seeds, dataset size and other parameters they have selected for data generation.

<img src="docs/guides/sds_summary.png" width="600">

### Final Output:

Finally user can see how their output looks like with corresponding Prompts and Completions.

The output will be saved in Project File System within Cloudera environment.

<img src="docs/guides/sds_output.png" width="600">



The output and corresponding metadata (scores,model etc.) can be seen on the **Generations** list view as well as shown in screen shot below.

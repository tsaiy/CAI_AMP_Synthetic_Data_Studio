import streamlit as st
import requests
import json
from typing import Dict, List
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Import necessary components from your app
from app.core.config import UseCase, Technique, ModelFamily, get_model_family
from app.core.prompt_templates import PromptBuilder
from app.services.synthesis_service import SynthesisService
from app.models.request_models import SynthesisRequest, Example, ModelParameters


# Configure page
st.set_page_config(page_title="LLM Data Synthesis", layout="wide")



# Default examples for each use case
DEFAULT_EXAMPLES = {
    "code_generation": [
        {
            "question": "How do you read a CSV file into a pandas DataFrame?",
            "solution": "You can use pandas.read_csv(). Here's an example:\n\n```python\nimport pandas as pd\ndf = pd.read_csv('data.csv')\n```"
        },
        {
            "question": "How do you write a function in Python?",
            "solution": "Here's how to define a function:\n\n```python\ndef greet(name):\n    return f'Hello, {name}!'\n\n# Example usage\nresult = greet('Alice')\nprint(result)  # Output: Hello, Alice!\n```"
        }
    ],
    "text2sql": [
        {
            "question": "How do you select all employees from the employees table?",
            "solution": "```sql\nSELECT *\nFROM employees;\n```"
        },
        {
            "question": "How do you join employees and departments tables?",
            "solution": "```sql\nSELECT e.name, d.department_name\nFROM employees e\nJOIN departments d ON e.department_id = d.id;\n```"
        }
    ]
}

# Default topics for each use case
DEFAULT_TOPICS = {
    "code_generation": [
        "python_basics",
        "data_structures",
        "algorithms",
        "web_development",
        "database_operations",
        "async_programming"
    ],
    "text2sql": [
        "basic_queries",
        "joins",
        "aggregations",
        "window_functions",
        "subqueries",
        "data_manipulation"
    ]
}

# Initialize services
# Initialize services
@st.cache_resource
def get_synthesis_service():
    """Initialize and cache synthesis service"""
    return SynthesisService()



# def get_preview_prompt(payload: dict) -> str:
#     """Generate preview prompt directly using PromptBuilder"""
#     try:

#         examples = []
#         if payload.get("examples"):
#             for ex in payload["examples"]:
#                 if isinstance(ex, dict) and "question" in ex and "solution" in ex:
#                     examples.append(Example(
#                         question=ex["question"],
#                         solution=ex["solution"]
#                     ))
#         # Convert technique string to enum
#         technique = Technique(payload.get("technique", "sft"))


#         prompt = PromptBuilder.build_prompt(
#             model_id=payload["model_id"],
#             use_case=payload["use_case"],
#             topic=payload["topics"][0] if payload["topics"] else "",  # Preview for first topic
#             num_questions=payload["num_questions"],
#             examples=examples,
#             technique=technique,
#             schema=payload.get("schema")
#         )
#         return prompt
#     except Exception as e:
#         st.error(f"Error generating preview prompt: {str(e)}")
#         return ""




def get_preview_prompt(payload: dict) -> str:
    """Get preview of the prompt from backend"""
    try:
        response = requests.post(
            "http://localhost:8100/preview/prompt",
            json=payload
        )
        response.raise_for_status()
        prompt_text = response.json().get("prompt", "")
        return prompt_text
    except Exception as e:
        st.error(f"Error getting preview prompt: {str(e)}")
        return ""
    
def update_edited_prompt():
    """Update edited prompt in session state"""
    st.session_state.edited_prompt = st.session_state.edited_prompt

def format_solution(solution: str, use_case: str) -> str:
    """Format solution based on use case for better display"""
    if use_case == "text2sql":
        # Extract SQL code and explanation
        sql_parts = solution.split("Explanation:", 1)
        
        formatted_output = ""
        
        # Format SQL part
        if "```sql" in sql_parts[0]:
            sql_code = sql_parts[0].split("```sql")[1].split("```")[0].strip()
            formatted_output += "**SQL Query:**\n```sql\n"
            formatted_output += f"{sql_code}\n```\n\n"
        
        # Format explanation if present
        if len(sql_parts) > 1:
            explanation = sql_parts[1].strip()
            formatted_output += "**Explanation:**\n"
            # Convert bullet points to proper markdown
            explanation_points = explanation.split("-")
            for point in explanation_points[1:]:  # Skip first empty split
                formatted_output += f"* {point.strip()}\n"
        
        return formatted_output
    
    return solution


if 'generation_complete' not in st.session_state:
    st.session_state.generation_complete = False
if 'generated_result' not in st.session_state:
    st.session_state.generated_result = None


def main():
    st.title("LLM Data Synthesis")
    
    # Main layout columns
    main_col1, main_col2 = st.columns([1, 1])
    
    # Left Column
    with main_col1:
        st.subheader("Configuration")
        
        use_case = st.selectbox(
            "Use Case",
            ["code_generation", "text2sql"],
            help="Select the type of data to generate"
        )
        
        model_id = st.selectbox(
            "Model",
            [
                "anthropic.claude-3-5-sonnet-20240620-v1:0",
                "anthropic.claude-v2",
                "anthropic.claude-instant-v1",
                "meta.llama3-8b-instruct-v1:0",
                "meta.llama3-1-70b-instruct-v1:0",
                "mistral.mixtral-8x7b-instruct-v0:1"
            ]
        )
        
        # Topics section
        st.subheader("Topics")

        # Initialize session states
        if 'topics' not in st.session_state:
            st.session_state.topics = DEFAULT_TOPICS[use_case].copy()
        if 'selected_topics' not in st.session_state:
            st.session_state.selected_topics = set()

        # Create a container for better organization
        with st.container():
            # Default topics in a container with fixed height
            st.write("Default Topics:")
            with st.container():
                # Using columns for better organization
                col1, col2 = st.columns(2)
                
                # Split topics into two columns
                mid_point = len(DEFAULT_TOPICS[use_case]) // 2
                left_topics = DEFAULT_TOPICS[use_case][:mid_point]
                right_topics = DEFAULT_TOPICS[use_case][mid_point:]
                
                with col1:
                    for topic in left_topics:
                        if st.checkbox(topic, key=f"default_{topic}"):
                            st.session_state.selected_topics.add(topic)
                        else:
                            st.session_state.selected_topics.discard(topic)
                            
                with col2:
                    for topic in right_topics:
                        if st.checkbox(topic, key=f"default_{topic}"):
                            st.session_state.selected_topics.add(topic)
                        else:
                            st.session_state.selected_topics.discard(topic)

            # Add new topic section
            st.write("---")
            col1, col2 = st.columns([3, 1])
            with col1:
                new_topic = st.text_input("Add Custom Topic", key="new_topic_input", placeholder="Enter new topic")
            with col2:
                if st.button("Add", key="add_topic_button") and new_topic:
                    if new_topic not in st.session_state.topics:
                        st.session_state.topics.append(new_topic)
                        st.rerun()

            # In the custom topics section, modify the container:
            custom_topics = [t for t in st.session_state.topics if t not in DEFAULT_TOPICS[use_case]]
            if custom_topics:
                st.write("Custom Topics:")
                st.markdown("""
                    <style>
                    .scrollable-container {
                        max-height: 200px;
                        overflow-y: auto;
                        border: 1px solid #ccc;
                        border-radius: 5px;
                        padding: 10px;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                with st.container():
                    st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
                    for topic in custom_topics:
                        col1, col2, col3 = st.columns([3, 0.5, 0.5])
                        with col1:
                            if st.checkbox(topic, key=f"custom_{topic}"):
                                st.session_state.selected_topics.add(topic)
                            else:
                                st.session_state.selected_topics.discard(topic)
                        with col3:
                            if st.button("🗑️", key=f"delete_{topic}", help="Remove topic"):
                                st.session_state.topics.remove(topic)
                                st.session_state.selected_topics.discard(topic)
                                st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            # Display selected topics in an expander
            if st.session_state.selected_topics:
                with st.expander(f"Selected Topics ({len(st.session_state.selected_topics)})"):
                    # Display topics in columns for better organization
                    selected_topics = sorted(st.session_state.selected_topics)
                    cols = st.columns(2)
                    mid_point = len(selected_topics) // 2
                    
                    with cols[0]:
                        for topic in selected_topics[:mid_point]:
                            st.write(f"• {topic}")
                    with cols[1]:
                        for topic in selected_topics[mid_point:]:
                            st.write(f"• {topic}")

        # Additional inputs
        num_questions = st.number_input(
            "Questions per Topic",
            min_value=1,
            max_value=50,
            value=3
        )
        
        is_demo = st.toggle(
            "Test Mode",
            value=True,
            help="Test Mode: Max 4 topics, 5 questions each. Shows results in response."
        )
        
        if use_case == "text2sql":
            schema = st.text_area(
                "Database Schema",
                value="""
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

            CREATE TABLE users (id INT, name VARCHAR(100));
            CREATE TABLE orders (id INT);
                
            """
            )
    # Right Column
    with main_col2:

         # Model parameters
        st.subheader("Model Parameters")
        temperature = st.slider("Temperature", 0.0, 2.0, 0.0, 0.05)
        top_p = st.slider("Top P", 0.0, 1.0, 1.0, 0.1)
        top_k = st.slider("Top K", 1, 500, 250)
        max_tokens = st.slider("Max Tokens", 1000, 200000, 4096)


        #examples section in the right column
        st.subheader("Examples")
        
        # Initialize examples in session state if not present
        if 'current_examples' not in st.session_state:
            st.session_state.current_examples = DEFAULT_EXAMPLES[use_case].copy()
        
        use_default_examples = st.checkbox("Use Default Examples", value=True)
        
        # Example editor
        st.write("Edit/Add Examples (max 6):")
        with st.container():
            # If using default examples, initialize from defaults
            if use_default_examples and st.session_state.current_examples != DEFAULT_EXAMPLES[use_case]:
                st.session_state.current_examples = DEFAULT_EXAMPLES[use_case].copy()
            
            # Create a temporary list to store updates
            updated_examples = []
            
            for i, example in enumerate(st.session_state.current_examples):
                with st.expander(f"Example {i+1}", expanded=False):
                    cols = st.columns([5, 1])
                    with cols[0]:
                        updated_question = st.text_area(
                            "Question",
                            value=example["question"],
                            key=f"q_{i}",
                            height=100
                        )
                        updated_solution = st.text_area(
                            "Solution",
                            value=example["solution"],
                            key=f"s_{i}",
                            height=150
                        )
                        updated_examples.append({
                            "question": updated_question,
                            "solution": updated_solution
                        })
                    with cols[1]:
                        if st.button("Remove", key=f"remove_example_{i}"):
                            st.session_state.current_examples.pop(i)
                            st.rerun()
            
            # Update the session state with modified examples
            st.session_state.current_examples = updated_examples
            
            if len(st.session_state.current_examples) < 6:
                if st.button("Add New Example"):
                    st.session_state.current_examples.append({"question": "", "solution": ""})
                    st.rerun()
            else:
                st.warning("Maximum 6 examples allowed")
            
           
        
   # In the main UI section where we handle prompt preview:
    # Prompt Management
    st.subheader("Prompt Management")
    
    # Initialize session states
    if 'preview_prompt' not in st.session_state:
        st.session_state.preview_prompt = ""
    if 'show_preview' not in st.session_state:
        st.session_state.show_preview = False
    if 'edited_prompt' not in st.session_state:
        st.session_state.edited_prompt = ""
    
    # Radio button for prompt type selection
    prompt_type = st.radio(
        "Select Prompt Type",
        options=["Use Default Prompt", "Preview & Edit Prompt"],
        help="Choose whether to use the default prompt or customize it"
    )
    
    if prompt_type == "Preview & Edit Prompt":
        preview_col1, preview_col2 = st.columns([5, 1])
        with preview_col1:
            if st.button("Generate Preview", type="secondary"):
                # Create payload for preview
                preview_payload = {
                    "use_case": use_case,
                    "model_id": model_id,
                    "num_questions": num_questions,
                    "topics": list(st.session_state.selected_topics),
                    "examples": st.session_state.current_examples if not use_default_examples else None,
                    
                    "technique": "sft",
                    "schema": schema if use_case == "text2sql" else None,
                    "model_params": {
                        "temperature": temperature,
                        "top_p": top_p,
                        "top_k": top_k,
                        "max_tokens": max_tokens
                    }
                }
                
                
                preview_prompt = get_preview_prompt(preview_payload)
                
                # Update session state
                if preview_prompt:
                    st.session_state.preview_prompt = preview_prompt
                    st.session_state.edited_prompt = preview_prompt
                    st.session_state.show_preview = True
                    st.rerun()
        
        if st.session_state.show_preview:
            st.info("""
            Below is the actual prompt that will be sent to the LLM. You can:
            1. Review the default prompt structure
            2. Make any needed modifications
            3. The edited version will be used for generation
            
            Prompt includes:
            - Model-specific formatting
            - Use case instructions
            - Selected examples
            - Schema (for SQL)
            - Additional parameters
            """)
            
            # Use session state value for the text area
            st.text_area(
                "Edit Prompt",
                value=st.session_state.preview_prompt,
                height=400,
                key="edited_prompt",
                on_change=update_edited_prompt
            )
    else:
        st.info("Using default prompt generation based on selected parameters")
    payload = {
            "use_case": use_case,
            "model_id": model_id,
            "num_questions": num_questions,
            "topics": list(st.session_state.selected_topics),
            "examples": st.session_state.current_examples if not use_default_examples else None,  # Use the current examples
            "technique": "sft",
            "model_params": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "max_tokens": max_tokens
            },
            "export_type": "local"
        }
        
    if use_case == "text2sql":
        payload["schema"] = schema
        
    # Handle prompt based on selection
    if prompt_type == "Preview & Edit Prompt":
        edited_value = st.session_state.get("edited_prompt", "")
        if edited_value:
            #request.custom_prompt = edited_value
            payload["custom_prompt"] = edited_value
            st.write("Using custom prompt for generation")
        else:
            st.warning("No custom prompt available, using default prompt")
     
   
    # Generate button
    button_col1, button_col2 = st.columns(2)

    # Generate button in first column
    with button_col1:
        if st.button("Generate", type="primary"):
            if not st.session_state.selected_topics:
                st.error("Please select at least one topic")
                return
                
            try:
                if is_demo:
                    bl = 'true'
                else:
                    bl = 'false'
                
                # Generate examples
                response = requests.post(
                    f"http://localhost:8100/synthesis/generate?is_demo={bl}",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                
                # Store result and set completion flag
                st.session_state.generated_result = result
                st.session_state.generation_complete = True
                
                # Display initial results
                st.subheader("Results")
                if is_demo and "results" in result:
                    st.success(f"Status: {result['status']}")
                    st.info(f"Output saved to: {result['export_path']}")
                    for topic, qa_pairs in result["results"].items():
                        with st.expander(f"Topic: {topic}"):
                            for qa in qa_pairs:
                                st.markdown(f"**Q:** {qa['question']}")
                                st.markdown(f"**A:** {qa['solution']}")
                                st.markdown("---")
                else:
                    st.success(f"Status: {result['status']}")
                    st.info(f"Output saved to: {result['export_path']}")
                
            except Exception as e:
                st.error(f"Error in generation: {str(e)}")
                st.session_state.generation_complete = False
                import traceback
                st.code(traceback.format_exc())

    # Evaluate button in second column
    with button_col2:
        if st.session_state.generation_complete:
            if st.button("Evaluate Results", type="secondary"):
                try:
                    if "results" in st.session_state.generated_result:
                        evaluation_payload = {
                            "use_case": use_case,
                            "results": st.session_state.generated_result["results"]
                        }
                        
                        with st.spinner('Evaluating generated examples...'):
                            eval_response = requests.post(
                                "http://localhost:8000/synthesis/evaluate",
                                json=evaluation_payload
                            )
                            eval_response.raise_for_status()
                            evaluated_results = eval_response.json()
                        
                        # Save evaluation results regardless of demo mode
                        evaluation_path = st.session_state.generated_result['export_path'].replace('.json', '_evaluated.json')
                        with open(evaluation_path, 'w') as f:
                            json.dump(evaluated_results, f, indent=2)

                        # Only display evaluation results in demo mode
                        if is_demo:
                            st.subheader("Evaluation Results")
                            for topic, evaluation in evaluated_results.items():
                                with st.expander(f"Topic: {topic} (Avg Score: {evaluation['average_score']:.2f}/5)"):
                                    st.markdown(f"**Topic Statistics:**")
                                    st.markdown(f"* Average Score: {evaluation['average_score']:.2f}/5")
                                    st.markdown(f"* Min Score: {evaluation['min_score']}/5")
                                    st.markdown(f"* Max Score: {evaluation['max_score']}/5")
                                    
                                    st.markdown("**Evaluated Examples:**")
                                    for i, pair in enumerate(evaluation['evaluated_pairs'], 1):
                                        st.markdown(f"Example {i}:")
                                        st.markdown(f"**Q:** {pair['question']}")
                                        st.markdown(f"**A:** {pair['solution']}")
                                        st.markdown(f"**Score:** {pair['evaluation']['score']}/5")
                                        st.markdown(f"**Justification:** {pair['evaluation']['justification']}")
                                        st.markdown("---")
                            st.success(f"Evaluation results saved to: {evaluation_path}")
                        else:
                            st.info(f"Evaluation results saved to: {evaluation_path}")
                
                except Exception as e:
                    st.error(f"Error in evaluation: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
        else:
            st.button("Evaluate Results", type="secondary", disabled=True, help="Generate examples first")

# # Add a reset button if needed
# if st.sidebar.button("Reset"):
#     st.session_state.generation_complete = False
#     st.session_state.generated_result = None
#     st.rerun()
if __name__ == "__main__":
    main()
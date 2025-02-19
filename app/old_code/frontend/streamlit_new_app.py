import streamlit as st
import requests
import json
from typing import Dict, List, Optional, Set
import os
import sys
from dataclasses import dataclass
from functools import lru_cache

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Constants and Configurations
MODEL_OPTIONS = [
    "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "anthropic.claude-v2",
    "anthropic.claude-instant-v1",
    "meta.llama3-8b-instruct-v1:0",
    "meta.llama3-1-70b-instruct-v1:0",
    "mistral.mixtral-8x7b-instruct-v0:1"
]

DEFAULT_SCHEMA = """
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

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    country VARCHAR(50),
    registration_date DATE,
    total_orders INT DEFAULT 0
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    category VARCHAR(50),
    price DECIMAL(10,2),
    stock_quantity INT,
    supplier_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20),
    shipping_address TEXT,
    shipping_cost DECIMAL(8,2),
    total_amount DECIMAL(10,2),
    payment_method VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    discount DECIMAL(5,2) DEFAULT 0,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);


"""

@dataclass
class UseCaseConfig:
    topics: List[str]
    examples: List[Dict]

USE_CASE_CONFIGS = {
    "code_generation": UseCaseConfig(
        topics=["python_basics", "data_structures", "algorithms", "web_development", 
                "database_operations", "async_programming"],
        examples=[
            {
                "question": "How do you read a CSV file into a pandas DataFrame?",
                "solution": "You can use pandas.read_csv(). Here's an example:\n\n```python\nimport pandas as pd\ndf = pd.read_csv('data.csv')\n```"
            },
            {
                "question": "How do you write a function in Python?",
                "solution": "Here's how to define a function:\n\n```python\ndef greet(name):\n    return f'Hello, {name}!'\n\n# Example usage\nresult = greet('Alice')\nprint(result)  # Output: Hello, Alice!\n```"
            }
        ]
    ),
    "text2sql": UseCaseConfig(
        topics=["basic_queries", "joins", "aggregations", "window_functions", 
                "subqueries", "data_manipulation"],
        examples=[
            {
                "question": "How do you select all employees from the employees table?",
                "solution": "```sql\nSELECT *\nFROM employees;\n```"
            },
            {
                "question": "How do you join employees and departments tables?",
                "solution": "```sql\nSELECT e.name, d.department_name\nFROM employees e\nJOIN departments d ON e.department_id = d.id;\n```"
            }
        ]
    )
}

class StateManager:
    @staticmethod
    def init_session_state():
        """Initialize session state variables"""
        defaults = {
            'generation_complete': False,
            'generated_result': None,
            'preview_prompt': "",
            'show_preview': False,
            'edited_prompt': "",
            'selected_topics': set(),
            'current_examples': None,
            'custom_topics': set(),
            'all_topics': None,
            'topics': None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

class APIClient:
    #BASE_URL = "http://localhost:8000"
    BASE_URL = "http://localhost:8787"
    
    @staticmethod
    def get_preview_prompt(payload: dict) -> str:
        try:
            response = requests.post(
                f"{APIClient.BASE_URL}/preview/prompt",
                json=payload
            )
            response.raise_for_status()
            return response.json().get("prompt", "")
        except Exception as e:
            st.error(f"Error getting preview prompt: {str(e)}")
            return ""

    @staticmethod
    def generate_examples(payload: dict, is_demo: bool) -> dict:
        try:
            response = requests.post(
                f"{APIClient.BASE_URL}/synthesis/generate?is_demo={str(is_demo).lower()}",
                json=payload
            )
            response.raise_for_status()
            #st.write(f"{APIClient.BASE_URL}/synthesis/generate?is_demo={str(is_demo).lower()}")
            #st.write(response)
            return response.json()
        except Exception as e:
            st.error(f"Error in generation: {str(e)}")
            raise

    @staticmethod
    def evaluate_results(payload: dict) -> dict:
        try:
            response = requests.post(
                f"{APIClient.BASE_URL}/synthesis/evaluate",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error in evaluation: {str(e)}")
            raise

class TopicsManager:
    @staticmethod
    def initialize_topics(use_case: str):
        """Initialize topics for the selected use case"""
        if 'topics' not in st.session_state or st.session_state.topics is None:
            st.session_state.topics = list(USE_CASE_CONFIGS[use_case].topics)
        if 'custom_topics' not in st.session_state:
            st.session_state.custom_topics = set()

    @staticmethod
    def add_custom_topic(topic: str):
        """Add a new custom topic"""
        if topic and topic not in st.session_state.topics:
            st.session_state.topics.append(topic)
            st.session_state.custom_topics.add(topic)
            return True
        return False

    @staticmethod
    def remove_custom_topic(topic: str):
        """Remove a custom topic"""
        if topic in st.session_state.custom_topics:
            st.session_state.topics.remove(topic)
            st.session_state.custom_topics.remove(topic)
            st.session_state.selected_topics.discard(topic)
            return True
        return False

class UIComponents:
    @staticmethod
    def render_configuration(use_case: str) -> tuple:
        """Render configuration section and return key parameters"""
        st.subheader("Configuration")
        
        model_id = st.selectbox("Model", MODEL_OPTIONS)
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
        
        schema = None
        if use_case == "text2sql":
            schema = st.text_area("Database Schema", value=DEFAULT_SCHEMA)
            
        return model_id, num_questions, is_demo, schema

    @staticmethod
    def render_topics_section(use_case: str):
        """Render topics selection section"""
        st.subheader("Topics")
        TopicsManager.initialize_topics(use_case)

        # Default topics section
        st.write("Default Topics:")
        default_topics = USE_CASE_CONFIGS[use_case].topics
        col1, col2 = st.columns(2)
        mid_point = len(default_topics) // 2
        
        for i, topic in enumerate(default_topics):
            col = col1 if i < mid_point else col2
            with col:
                if st.checkbox(topic, key=f"default_{topic}"):
                    st.session_state.selected_topics.add(topic)
                else:
                    st.session_state.selected_topics.discard(topic)

        # Custom topics section
        st.write("---")
        st.write("Custom Topics:")
        
        # Add new topic input
        col1, col2 = st.columns([3, 1])
        with col1:
            new_topic = st.text_input("Add Custom Topic", key="new_topic_input", placeholder="Enter new topic")
        with col2:
            if st.button("Add", key="add_topic_button") and new_topic:
                if TopicsManager.add_custom_topic(new_topic):
                    st.rerun()

        # Display custom topics if any
        if st.session_state.custom_topics:
            st.markdown("""
                <style>
                .custom-topics {
                    max-height: 200px;
                    overflow-y: auto;
                    padding: 10px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
                </style>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="custom-topics">', unsafe_allow_html=True)
            for topic in sorted(st.session_state.custom_topics):
                cols = st.columns([3, 0.5, 0.5])
                with cols[0]:
                    if st.checkbox(topic, key=f"custom_{topic}"):
                        st.session_state.selected_topics.add(topic)
                    else:
                        st.session_state.selected_topics.discard(topic)
                with cols[2]:
                    if st.button("🗑️", key=f"delete_{topic}"):
                        if TopicsManager.remove_custom_topic(topic):
                            st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def render_model_parameters() -> dict:
        """Render model parameters section and return parameters"""
        st.subheader("Model Parameters")
        return {
            "temperature": st.slider("Temperature", 0.0, 2.0, 0.0, 0.05),
            "top_p": st.slider("Top P", 0.0, 1.0, 1.0, 0.1),
            "top_k": st.slider("Top K", 1, 500, 250),
            "max_tokens": st.slider("Max Tokens", 1000, 200000, 4096)
        }

    @staticmethod
    def render_examples_section(use_case: str):
        """Render examples section"""
        st.subheader("Examples")
        
        if 'current_examples' not in st.session_state or st.session_state.current_examples is None:
            st.session_state.current_examples = USE_CASE_CONFIGS[use_case].examples.copy()
            
        use_default_examples = st.checkbox("Use Default Examples", value=True)
        
        if use_default_examples:
            st.session_state.current_examples = USE_CASE_CONFIGS[use_case].examples.copy()
            
        # Example editor
        st.write("Edit/Add Examples (max 6):")
        
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
        
        st.session_state.current_examples = updated_examples
        
        if len(st.session_state.current_examples) < 6:
            if st.button("Add New Example"):
                st.session_state.current_examples.append({"question": "", "solution": ""})
                st.rerun()
        else:
            st.warning("Maximum 6 examples allowed")

class PromptManager:
    @staticmethod
    def render_prompt_section(payload: dict):
        """Render prompt management section"""
        st.subheader("Prompt Management")
        
        prompt_type = st.radio(
            "Select Prompt Type",
            options=["Use Default Prompt", "Preview & Edit Prompt"],
            help="Choose whether to use the default prompt or customize it"
        )
        
        custom_prompt = None
        if prompt_type == "Preview & Edit Prompt":
            preview_col1, preview_col2 = st.columns([5, 1])
            with preview_col1:
                if st.button("Generate Preview", type="secondary"):
                    preview_prompt = APIClient.get_preview_prompt(payload)
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
                
                custom_prompt = st.text_area(
                    "Edit Prompt",
                    value=st.session_state.preview_prompt,
                    height=400,
                    key="edited_prompt"
                )
                
        return custom_prompt if prompt_type == "Preview & Edit Prompt" else None
class SolutionFormatter:
    @staticmethod
    def format_code_generation(solution: str) -> tuple:
        """Format code generation solution to separate code and explanation"""
        code = ""
        explanation = ""
        
        # Split by code blocks
        parts = solution.split("```")
        
        if len(parts) >= 3:
            pre_explanation = parts[0].strip()
            code = parts[1].replace("python\n", "").strip()
            post_explanation = "".join(parts[2:]).strip()
            
            # Combine any explanations
            explanation_parts = []
            if pre_explanation:
                explanation_parts.append(pre_explanation)
            if post_explanation:
                explanation_parts.append(post_explanation)
            explanation = "\n\n".join(explanation_parts)
        else:
            # If no proper code blocks found, treat entire solution as code
            code = solution.strip()
            
        return code, explanation

    @staticmethod
    def format_sql_solution(solution: str) -> tuple:
        """Format SQL solution to separate query and explanation"""
        query = ""
        explanation = ""
        
        # Split by SQL code blocks
        if "```sql" in solution:
            parts = solution.split("```sql")
            if len(parts) >= 2:
                pre_explanation = parts[0].strip()
                remaining = parts[1].split("```")
                
                query = remaining[0].strip()
                post_explanation = "".join(remaining[1:]).strip()
                
                # Combine explanations
                explanation_parts = []
                if pre_explanation:
                    explanation_parts.append(pre_explanation)
                if post_explanation:
                    explanation_parts.append(post_explanation)
                explanation = "\n\n".join(explanation_parts)
        else:
            # If no SQL code blocks found, try to separate by common patterns
            parts = solution.split("Explanation:", 1)
            if len(parts) == 2:
                query = parts[0].strip()
                explanation = parts[1].strip()
            else:
                query = solution.strip()
                
        return query, explanation

    @staticmethod
    def format_explanation(explanation: str) -> List[str]:
        """Format explanation into bullet points if possible"""
        if not explanation:
            return []
            
        # Try to split by different bullet point markers
        for marker in ['\n- ', '\n• ', '\n* ']:
            if marker in explanation:
                return [point.strip() for point in explanation.split(marker) if point.strip()]
        
        # If no bullet points found, split by newlines and filter empty lines
        points = [line.strip() for line in explanation.split('\n') if line.strip()]
        if points:
            return points
            
        # If still no points, return the entire explanation as a single point
        return [explanation]

def display_generated_results(use_case: str, result: dict):
    """Display generated results with proper formatting"""
    # Always show status and file path
    st.success(f"Status: {result['status']}")
    st.info(f"Output saved to: {result['export_path']}")
    
    # Only show the detailed results in demo mode
    if "results" in result:
        # Create tabs for different topics
        tabs = st.tabs(list(result["results"].keys()))
        for tab, (topic, qa_pairs) in zip(tabs, result["results"].items()):
            with tab:
                for i, qa in enumerate(qa_pairs, 1):
                    with st.expander(f"Example {i}", expanded=True):
                        # Question section
                        st.markdown("### Question")
                        st.markdown(qa['question'])
                        
                        # Solution section with formatting based on use case
                        st.markdown("### Solution")
                        if use_case == "text2sql":
                            query, explanation = SolutionFormatter.format_sql_solution(qa['solution'])
                            
                            # Display SQL Query
                            st.markdown("**SQL Query:**")
                            st.code(query, language='sql')
                            
                        elif use_case == "code_generation":
                            code, explanation = SolutionFormatter.format_code_generation(qa['solution'])
                            
                            # Display Code
                            st.markdown("**Code:**")
                            st.code(code, language='python')
                        
                        # Display Explanation if available
                        if explanation:
                            st.markdown("**Explanation:**")
                            points = SolutionFormatter.format_explanation(explanation)
                            for point in points:
                                st.markdown(f"- {point}")
                        
                        st.markdown("---")
   

def main():
    st.set_page_config(page_title="LLM Data Synthesis", layout="wide")
    StateManager.init_session_state()
    
    st.title("LLM Data Synthesis")
    
    use_case = st.selectbox("Use Case", list(USE_CASE_CONFIGS.keys()))
    
    # Main layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        model_id, num_questions, is_demo, schema = UIComponents.render_configuration(use_case)
        UIComponents.render_topics_section(use_case)
        
    with col2:
        model_params = UIComponents.render_model_parameters()
        UIComponents.render_examples_section(use_case)
    
    # Generate payload
    payload = {
        "use_case": use_case,
        "model_id": model_id,
        "num_questions": num_questions,
        "topics": list(st.session_state.selected_topics),
        "examples": st.session_state.current_examples,
        "technique": "sft",
        "model_params": model_params,
        "export_type": "local"
    }
    
    if schema:
        payload["schema"] = schema
    
    # Prompt Management Section
    custom_prompt = PromptManager.render_prompt_section(payload)
    if custom_prompt:
        payload["custom_prompt"] = custom_prompt

    st.markdown("---")  # Visual separator

    # Generation and Evaluation sections
    gen_col1, gen_col2 = st.columns(2)
    
    with gen_col1:
        if st.button("Generate", type="primary"):
            if not st.session_state.selected_topics:
                st.error("Please select at least one topic")
                return
                
            try:
                with st.spinner('Generating examples...'):
                    result = APIClient.generate_examples(payload, is_demo)
                    st.session_state.generated_result = result
                    st.session_state.generation_complete = True
                    
                    # Always display results, the function will handle demo vs non-demo mode
                    display_generated_results(use_case, result)
                    
            except Exception as e:
                st.error(f"Error in generation: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
                st.session_state.generation_complete = False
    
    with gen_col2:
        if st.session_state.generation_complete:
            if st.button("Evaluate Results", type="secondary"):
                try:
                    with st.spinner('Evaluating generated examples...'):
                        if "results" in st.session_state.generated_result:
                            evaluation_payload = {
                                "use_case": use_case,
                                "results": st.session_state.generated_result["results"]
                            }
                            
                            evaluated_results = APIClient.evaluate_results(evaluation_payload)
                            
                            # Save evaluation results
                            evaluation_path = st.session_state.generated_result['export_path'].replace('.json', '_evaluated.json')
                            with open(evaluation_path, 'w') as f:
                                json.dump(evaluated_results, f, indent=2)

                            # Display evaluation results in demo mode
                            if is_demo:
                                st.subheader("Evaluation Results")
                                
                                # Create tabs for each topic's evaluation
                                topic_tabs = st.tabs(list(evaluated_results.keys()))
                                for tab, (topic, evaluation) in zip(topic_tabs, evaluated_results.items()):
                                    with tab:
                                        # Topic summary
                                        st.markdown("### Topic Summary")
                                        summary_cols = st.columns(4)
                                        with summary_cols[0]:
                                            st.metric("Average Score", f"{evaluation['average_score']:.2f}")
                                        with summary_cols[1]:
                                            st.metric("Min Score", str(evaluation['min_score']))
                                        with summary_cols[2]:
                                            st.metric("Max Score", str(evaluation['max_score']))
                                        
                                        # Detailed evaluations
                                        st.markdown("### Detailed Evaluations")
                                        for i, pair in enumerate(evaluation['evaluated_pairs'], 1):
                                            with st.expander(f"Example {i} (Score: {pair['evaluation']['score']}/5)", expanded=False):
                                                st.markdown("**Question:**")
                                                st.code(pair['question'], language='text')
                                                
                                                st.markdown("**Solution:**")
                                                if use_case == "text2sql":
                                                    st.code(pair['solution'], language='sql')
                                                elif use_case == "code_generation":
                                                    st.code(pair['solution'], language='python')
                                                else:
                                                    st.markdown(pair['solution'])
                                                
                                                st.markdown("**Evaluation:**")
                                                st.markdown(f"* **Score:** {pair['evaluation']['score']}/5")
                                                st.markdown(f"* **Justification:** {pair['evaluation']['justification']}")
                                
                                st.success(f"Evaluation results saved to: {evaluation_path}")
                            else:
                                st.info(f"Evaluation results saved to: {evaluation_path}")
                                
                except Exception as e:
                    st.error(f"Error in evaluation: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
        else:
            # Disable evaluation button if generation is not complete
            st.button("Evaluate Results", type="secondary", disabled=True, 
                     help="Generate examples first before evaluation")

    # Add reset functionality
    if st.sidebar.button("Reset Application"):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()
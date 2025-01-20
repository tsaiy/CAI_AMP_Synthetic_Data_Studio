import { Link } from 'react-router-dom';

import { Pages } from '../../types';
import { LABELS } from '../../constants';

const data = [
    {
      "id": 1,
      "name": "dchung_dataset_1",
      "model_type": "AWS Bedrock",
      "timestamp": "2024-11-19T16:23:57.093311",
      "model_id": "anthropic.claude-3-5-sonnet-20240620-v1:0",
      "use_case": "code_generation",
      "custom_prompt": "Requirements:\n                        - Each solution must include working code examples\n                        - Include explanations with the code\n                        - Follow the same format as the examples\n                        - Ensure code is properly formatted with appropriate indentation",
      "model_parameters": {
        "temperature": 0,
        "top_p": 1,
        "min_p": 0,
        "top_k": 0.1,
        "max_tokens": 4096
      },
      "generate_file_name": "qa_pairs_claude-3-5-sonnet-20240620-v1:0_20241119_162357_test.json",
      "generate_display_name": "qa_pairs_claude-3-5-sonnet-20240620-v1:0_20241119_162357_test.json",
      "local_export_path": "qa_pairs_claude-3-5-sonnet-20240620-v1:0_20241119_162357_test.json",
      "hf_export_path": null,
      "num_questions": 1,
      "topics": [

      ],
      "examples": [
        {
          "question": "How do you read a CSV file into a pandas DataFrame?",
          "solution": "You can use pandas.read_csv(). Here's an example:\n\n```python\nimport pandas as pd\ndf = pd.read_csv('data.csv')\n```"
        },
        {
          "question": "How do you write a function in Python?",
          "solution": "Here's how to define a function:\n\n```python\ndef greet(name):\n    return f'Hello, {name}!'\n\n# Example usage\nresult = greet('Alice')\nprint(result)  # Output: Hello, Alice!\n```"
        }
      ],
      "schema": null
    }
]

const Home = () => {
    return (
        <>
            <h1>{LABELS[Pages.HOME]}</h1>
            <Link
              to={`/${Pages.GENERATOR}`}
              state={{
                data: data[0],
                internalRedirect: true,
              }}
            >
              {LABELS[Pages.GENERATOR]}
            </Link>
        </>
    )
}

export default Home;
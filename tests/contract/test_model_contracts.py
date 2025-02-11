import pytest
from app.core.prompt_templates import PromptBuilder
from app.models.request_models import UseCase, Example, Technique
from typing import List, Optional

def test_generate_prompt_contract():
    example = Example(
        question="test question?",
        solution="test solution"
    )
    
    prompt = PromptBuilder.build_prompt(
        model_id="test.model",
        use_case=UseCase.CODE_GENERATION,
        topic="test",
        num_questions=1,
        omit_questions=[],
        examples=[example],
        technique=Technique.SFT,
        schema=None,  
        custom_prompt=None  
    )
    
    assert isinstance(prompt, str)
    assert "test question?" in prompt
    assert "test solution" in prompt
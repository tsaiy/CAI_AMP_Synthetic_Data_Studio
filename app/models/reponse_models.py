from typing import List, Dict, Optional
from pydantic import BaseModel

class QuestionAnswer(BaseModel):
    question: str
    solution: str

class TopicResult(BaseModel):
    topic: str
    qa_pairs: List[QuestionAnswer]

class SynthesisResponse(BaseModel):
    status: str
    results: Optional[List[TopicResult]]
    export_path: Optional[str]
    error: Optional[str]
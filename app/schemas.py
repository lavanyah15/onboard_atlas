from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=5000)


class AskResponse(BaseModel):
    answer: str
    model_used: str
    input_tokens: int
    output_tokens: int
    total_tokens: int

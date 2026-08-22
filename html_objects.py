from pydantic import BaseModel


class Question(BaseModel):
    id: int
    description: str
    answers: dict[str, str]
    correct_answer: str
    media: str | None = None

class QuestionResult(BaseModel):
    id: int
    answer: str
from pydantic import BaseModel


class Question(BaseModel):
    id: int
    description: str
    answers: dict[str, str]
    correct_answer: str
    media: str | None = None
    points: int
    special: bool

class QuestionForResults(BaseModel):
    id: int
    description: str
    answers: dict[str, str]
    correct_answer: str
    selected_answer: str
    media: str | None = None
    points: int
    special: bool

class Results(BaseModel):
    questions: list[QuestionForResults]
    points: int

class QuestionInfo(BaseModel):
    id: int
    description: str
    answers: dict[str, str]
    media: str | None = None
    points: int
    special: bool

class ReturnedAnswer(BaseModel):
    id: int
    answer: str
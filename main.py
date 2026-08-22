import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from html_objects import *

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

answered_questions: dict[int, str] = {}

# Serving HTMLs
@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/about", response_class=HTMLResponse)
async def serve_about(request: Request):
    return templates.TemplateResponse(request=request, name="about.html")

@app.get("/question", response_class=HTMLResponse)
async def serve_question(request: Request):
    return templates.TemplateResponse(request=request, name="question.html")

@app.post("/reset")
async def reset_answers():
    global answered_questions
    answered_questions = {}
    return {"answered_questions": "reset"}


# Sample: generates some question.
@app.get("/question/get", response_model=Question)
async def get_question():
    return Question(id=100, description="Sample Question", answers={"A": "Answer A", "B": "Answer B", "C": "Answer C"}, media=None, correct_answer="C")

@app.post("/question/submit-answer")
async def submit_answer(result: QuestionResult):
    answered_questions[result.id] = result.answer
    return {"passed": answered_questions}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

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

# Serving HTMLs
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/about", response_class=HTMLResponse)
async def read_about(request: Request):
    return templates.TemplateResponse(request=request, name="about.html")

@app.get("/question", response_class=HTMLResponse)
async def read_test_triple(request: Request):
    return templates.TemplateResponse(request=request, name="question.html")


class Question(BaseModel):
    description: str
    answers: dict[str, str]
    correct_answer: str
    media: str | None = None
    points: int

points_num: int = 0
next_question: Question

# Sample: generates some question.
@app.get("/question/get", response_model=Question)
async def get_question():
    global next_question
    next_q = Question(description="Sample Question", answers={"A": "Answer A", "B": "Answer B", "C": "Answer C"}, media=None, correct_answer="C", points=3)
    next_question = next_q
    return next_q

@app.post("/question/grant_points")
async def update_points():
    global points_num
    points_num += next_question.points
    return {"points": points_num}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=7878,
    )
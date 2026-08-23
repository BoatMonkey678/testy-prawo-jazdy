import configparser

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from html_objects import *

config = configparser.ConfigParser()
config.read("config.ini")
server_host = config["server"]["host"]
server_port = config.getint("server", "port")
api_url = f"http://{server_host}:{server_port}"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/resources", StaticFiles(directory="resources"), name="resources")
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
    return templates.TemplateResponse(request=request, name="index.html", context={"api_url": api_url})

@app.get("/about", response_class=HTMLResponse)
async def serve_about(request: Request):
    return templates.TemplateResponse(request=request, name="about.html", context={"api_url": api_url})

@app.get("/question", response_class=HTMLResponse)
async def serve_question(request: Request):
    return templates.TemplateResponse(request=request, name="question.html", context={"api_url": api_url})

@app.post("/reset")
async def reset_answers():
    global answered_questions
    answered_questions = {}
    return {"answered_questions": "reset"}


# Sample: generates some question.
@app.get("/question/get", response_model=Question)
async def get_question():
    return Question(id=100, description="Sample Question", answers={"A": "Answer A", "B": "Answer B", "C": "Answer C"}, media="BigBuckBunny_320x180.mp4", correct_answer="C")

@app.post("/question/submit-answer")
async def submit_answer(result: QuestionResult):
    answered_questions[result.id] = result.answer
    return {"answered": answered_questions}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=server_host,
        port=server_port,
    )
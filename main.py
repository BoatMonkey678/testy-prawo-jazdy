import configparser
import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from html_objects import *
from question_bank import *
from resourse_manager import *

config = configparser.ConfigParser()
config.read("config.ini")
server_host = config["server"]["host"]
server_port = config.getint("server", "port")
converting_threads = config.getint("system_resources", "conversion_threads")
api_url = f"http://{server_host}:{server_port}"

download_if_not_present("https://www.gov.pl/attachment/a5c6c329-28a5-4274-a1a8-e2813f0a51bd", "./resources/data.xlsx")

if not os.path.exists("./resources/media"):
    download_if_not_present("https://www.gov.pl/pliki/mi/multimedia_do_pytan.zip", "./resources/multimedia-1.zip")
    download_if_not_present("https://www.gov.pl/attachment/10d143bf-9e93-4d82-935d-48c89353d3ce", "./resources/multimedia-2.zip")
    extract_archive(Path("./resources/multimedia-1.zip"), "./resources/media")
    extract_archive(Path("./resources/multimedia-2.zip"), "./resources/media")
    os.remove("./resources/multimedia-1.zip")
    os.remove("./resources/multimedia-2.zip")

convert_wmv_directory("./resources/media", converting_threads)

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

question_bank: list[Question] = get_questions_database("./resources/data.xlsx", "B")

selected_questions: list[int] = []

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
    global answered_questions, selected_questions
    answered_questions = {}
    selected_questions = generate_random_set(question_bank.copy())
    return {"answered_questions": "reset"}


# Sample: generates some question.
@app.get("/question/get", response_model=QuestionInfo | None)
async def get_question() -> QuestionInfo | None:
    try:
        next_id = selected_questions.pop(0)
        next_q = get_question_by_id(question_bank, next_id)
        if next_q is None:
            return None
        return QuestionInfo(id=next_q.id, description=next_q.description, answers=next_q.answers, media=next_q.media)
    except IndexError:
        return None

@app.post("/question/submit-answer")
async def submit_answer(result: ReturnedAnswer):
    answered_questions[result.id] = result.answer
    return {"answered": answered_questions}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=server_host,
        port=server_port,
    )
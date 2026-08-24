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

IS_FROZEN = getattr(sys, "frozen", False)
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

app = FastAPI(
    docs_url=None if IS_FROZEN else "/docs",
    redoc_url=None if IS_FROZEN else "/redoc",
    openapi_url=None if IS_FROZEN else "/openapi.json",
)

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

@app.get("/results", response_class=HTMLResponse)
async def serve_results(request: Request):
    return templates.TemplateResponse(request=request, name="results.html", context={"api_url": api_url})

@app.get("/results/details", response_class=HTMLResponse)
@app.get("/results/detail", response_class=HTMLResponse)
async def serve_results_details(request: Request):
    return templates.TemplateResponse(request=request, name="results-detail.html", context={"api_url": api_url})


@app.get("/results/get", response_model=Results)
async def get_results() -> Results:
    questions = []
    points = 0

    for key, value in answered_questions.items():
        q = get_question_by_id(question_bank, key)
        questions.append(QuestionForResults(
            id=q.id,
            description=q.description,
            answers=q.answers,
            correct_answer=q.correct_answer,
            selected_answer=value,
            media=q.media,
            points=q.points,
            special=q.special
        ))

        if value == q.correct_answer:
            points += q.points

    return Results(questions=questions, points=points)

# Reset answers upon entering "/"
@app.post("/reset")
async def reset_answers():
    global answered_questions, selected_questions
    answered_questions = {}
    selected_questions = generate_random_set(question_bank.copy())
    return {"answered_questions": "reset"}


# Get the next question
@app.get("/question/get", response_model=QuestionInfo | None)
async def get_question() -> QuestionInfo | None:
    try:
        next_id = selected_questions.pop(0)
        next_q = get_question_by_id(question_bank, next_id)
        if next_q is None:
            return None
        return QuestionInfo(id=next_q.id, description=next_q.description, answers=next_q.answers, media=next_q.media, points=next_q.points, special=next_q.special)
    except IndexError:
        return None


# Submit selected answer
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
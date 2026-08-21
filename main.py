import uvicorn
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
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


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/about", response_class=HTMLResponse)
async def read_about(request: Request):
    return templates.TemplateResponse(request=request, name="about.html")

@app.get("/test-triple", response_class=HTMLResponse)
async def read_test_triple(request: Request):
    return templates.TemplateResponse(request=request, name="test-triple.html")


class Question(BaseModel):
    description: str
    answers: list[str]
    correct_answer: int
    media: str | None = None

items = {   
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@app.get("/items/{item_id}", response_model=Question)
async def read_item(item_id: str):
    return items[item_id]

# Sample: generates some question.
@app.get("/next_question", response_model=Question)
async def get_next_question():
    return Question(description="Which answer is the most fucked up???", answers=["Walić Konia", "Konić Wala", "8====D"], media=None, correct_answer=0)


@app.put("/items/{item_id}", response_model=Question)
async def update_item(item_id: str, item: Question):
    update_item_encoded = jsonable_encoder(item)
    items[item_id] = update_item_encoded
    return update_item_encoded


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=7878,
    )
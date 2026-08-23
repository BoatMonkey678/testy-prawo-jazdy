import random
from pathlib import Path

import pandas as pd

from html_objects import Question

__all__ = ["generate_random_set", "get_question_by_id", "get_questions_database"]

def get_questions_database(dataPath: Path, category: str) -> list[Question]:
    df = pd.read_excel(dataPath)
    category_mask = df["Kategorie"].fillna("").apply(
        lambda value: category in (item.strip() for item in str(value).split(","))
    )

    return [parse_row_to_question(row) for _, row in df[category_mask].iterrows()]

def generate_random_set(bank: list[Question]) -> list[int]:
    output = []

    output.extend(generic_amount_question(bank, special=False, points=3, number=10))
    output.extend(generic_amount_question(bank, special=False, points=2, number=6))
    output.extend(generic_amount_question(bank, special=False, points=1, number=4))
    output.extend(generic_amount_question(bank, special=True, points=3, number=6))
    output.extend(generic_amount_question(bank, special=True, points=2, number=4))
    output.extend(generic_amount_question(bank, special=True, points=1, number=2))

    return output

def get_question_by_id(bank: list[Question], id: int) -> Question:
    return next((x for x in bank if x.id == id), None)

def generic_amount_question(bank: list[Question], special: bool, points: int, number: int) -> list[int]:
    output = []
    while len(output) < number:
        next_q = random.choice(bank)

        if next_q.special != special or next_q.points != points:
            continue

        output.append(next_q.id)
        bank.remove(next_q)

    return output


def parse_row_to_question(row: pd.Series):
    answer_dict = {}
    media = None if pd.isna(row["Media"]) else str(row["Media"])

    if row["Poprawna odp"] in ["T", "N"]:
        answer_dict["T"] = "Tak"
        answer_dict["N"] = "Nie"
    else:
        answer_dict["A"] = row["Odpowiedź A"]
        answer_dict["B"] = row["Odpowiedź B"]
        answer_dict["C"] = row["Odpowiedź C"]

    return Question(
        id=row["Numer pytania"],
        description=row["Pytanie"],
        answers=answer_dict,
        correct_answer=row["Poprawna odp"],
        media=media,
        points=row["Liczba punktów"],
        special=row["Zakres struktury"] == "SPECJALISTYCZNY"
    )

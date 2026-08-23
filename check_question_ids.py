from pathlib import Path

import pandas as pd

DATA_PATH = Path("./resources/data.xlsx")
COLUMN_NAME = "Numer pytania"


def main() -> int:
    if not DATA_PATH.exists():
        print(f"File not found: {DATA_PATH}")
        return 1

    dataframe = pd.read_excel(DATA_PATH)

    if COLUMN_NAME not in dataframe.columns:
        print(f'Missing column: "{COLUMN_NAME}"')
        return 1

    question_ids = dataframe[COLUMN_NAME]
    missing_rows = dataframe.index[question_ids.isna()].tolist()
    valid_ids = question_ids.dropna()
    duplicate_rows = valid_ids.index[valid_ids.duplicated(keep=False)].tolist()

    if missing_rows:
        print(f"Missing question ID on Excel rows: {[row + 2 for row in missing_rows]}")

    if duplicate_rows:
        duplicate_ids = valid_ids[valid_ids.duplicated(keep=False)].unique().tolist()
        print(f"Duplicate question IDs: {duplicate_ids}")
        print(f"Duplicate IDs occur on Excel rows: {[row + 2 for row in duplicate_rows]}")

    if missing_rows or duplicate_rows:
        return 1

    print(f"OK: {len(question_ids)} question IDs are present and unique.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
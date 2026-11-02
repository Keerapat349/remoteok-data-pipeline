
from pathlib import Path
import pandas as pd

from scraper_api import fetch_jobs

BASE_DIR = Path(__file__).parent
OUTPUT_FILE = BASE_DIR / "final_jobs.csv"

REQUIRED_COLUMNS = [
    "Job_ID", "Title", "Company", "Location",
    "Skills", "min_salary", "max_salary", "URL"
]


def clean_and_validate(jobs):
    df = pd.DataFrame(jobs, columns=REQUIRED_COLUMNS)

    if df.empty:
        raise ValueError("No jobs were collected.")

    # Remove duplicate job IDs
    before = len(df)
    df = df.drop_duplicates(subset=["Job_ID"]).copy()

    # Clean text columns
    text_columns = [
        "Job_ID", "Title", "Company",
        "Location", "Skills", "URL"
    ]

    for column in text_columns:
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # Convert salaries to numbers
    for column in ["min_salary", "max_salary"]:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    # Validate required data
    if df["Job_ID"].eq("").any():
        raise ValueError("Missing Job IDs.")

    if df["Title"].eq("").any():
        raise ValueError("Missing job titles.")

    if not df["URL"].str.startswith("https://").all():
        raise ValueError("Invalid URLs found.")

    if (
        df["min_salary"].notna()
        & df["max_salary"].notna()
        & (df["min_salary"] > df["max_salary"])
    ).any():
        raise ValueError("Invalid salary ranges.")

    print("Original jobs:", before)
    print("Duplicates removed:", before - len(df))
    print("Cleaned jobs:", len(df))
    print("Missing locations:",
          df["Location"].eq("").sum())
    print("Missing minimum salaries:",
          df["min_salary"].isna().sum())

    return df


def main():
    try:
        jobs = fetch_jobs()
        df = clean_and_validate(jobs)

        # Save only after validation passes
        df.to_csv(
            OUTPUT_FILE,
            index=False,
            encoding="utf-8-sig"
        )

        print("PASS: Pipeline completed.")
        print("Saved to:", OUTPUT_FILE)

    except Exception as error:
        print("FAILED:", error)
        raise


if __name__ == "__main__":
    main()

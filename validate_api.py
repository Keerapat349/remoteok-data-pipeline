
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "api_jobs.csv"


def validate_api_data():
    df = pd.read_csv(CSV_FILE)

    required_columns = [
        "Job_ID", "Title", "Company", "Location",
        "Skills", "min_salary", "max_salary", "URL"
    ]

    print("=== API DATA VALIDATION ===")
    print("Total jobs:", len(df))

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    print("Duplicate Job IDs:",
          df["Job_ID"].duplicated().sum())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nInvalid job URLs:",
          (~df["URL"].fillna("").str.startswith(
              "https://"
          )).sum())

    salary_min = pd.to_numeric(
        df["min_salary"], errors="coerce"
    )
    salary_max = pd.to_numeric(
        df["max_salary"], errors="coerce"
    )

    invalid_salary = (
        salary_min.notna()
        & salary_max.notna()
        & (salary_min > salary_max)
    )

    print("Invalid salary ranges:",
          invalid_salary.sum())

    print("\nFirst 5 jobs:")
    print(df.head().to_string(index=False))

    if (
        len(df) > 0
        and df["Job_ID"].notna().all()
        and df["Title"].notna().all()
        and df["Job_ID"].is_unique
        and df["URL"].fillna("").str.startswith("https://").all()
        and not invalid_salary.any()
    ):
        print("\nPASS: Core validation checks passed.")
    else:
        print("\nWARNING: Some checks need attention.")


if __name__ == "__main__":
    validate_api_data()

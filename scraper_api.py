
from pathlib import Path
import requests
import pandas as pd

API_URL = "https://remoteok.com/api"
OUTPUT_FILE = Path(__file__).parent / "api_jobs.csv"


def fetch_jobs():
    response = requests.get(
        API_URL,
        headers={
            "User-Agent": "PortfolioLearningProject/1.0"
        },
        timeout=30
    )
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        raise ValueError("Unexpected API response")

    jobs = []

    for item in data:
        if not isinstance(item, dict):
            continue

        # Skip API metadata and legal notice
        if not item.get("id") or not item.get("position"):
            continue

        jobs.append({
            "Job_ID": str(item["id"]),
            "Title": item["position"],
            "Company": item.get("company", ""),
            "Location": item.get("location", ""),
            "Skills": ", ".join(item.get("tags") or []),
            "min_salary": item.get("salary_min") or None,
            "max_salary": item.get("salary_max") or None,
            "URL": item.get("url", "")
        })

    return jobs


def main():
    try:
        jobs = fetch_jobs()

        if not jobs:
            print("No job data found. CSV was not saved.")
            return

        df = pd.DataFrame(jobs)

        df = df.drop_duplicates(subset=["Job_ID"])

        df["min_salary"] = pd.to_numeric(
            df["min_salary"], errors="coerce"
        )
        df["max_salary"] = pd.to_numeric(
            df["max_salary"], errors="coerce"
        )

        df.to_csv(
            OUTPUT_FILE,
            index=False,
            encoding="utf-8-sig"
        )

        print("Source: Remote OK")
        print("Total jobs:", len(df))
        print("Duplicate IDs:", df["Job_ID"].duplicated().sum())
        print("Missing values:")
        print(df.isnull().sum())
        print("Saved to:", OUTPUT_FILE)

    except (requests.RequestException, ValueError) as error:
        print("Error:", error)


if __name__ == "__main__":
    main()

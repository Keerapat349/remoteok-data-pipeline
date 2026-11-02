from pathlib import Path
import re
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / 'all_jobs.csv'
OUTPUT_FILE = BASE_DIR / 'cleaned_jobs_v2.csv'
COLUMNS = ['Title', 'Location', 'Salary', 'Skills']


def clean_location(value):
    if pd.isna(value):
        return pd.NA
    text = str(value)
    text = re.sub(r'💰\s*Upgrade to Premium to see salary', '', text)
    text = re.sub(r'⏰\s*Part time', '', text)
    text = text.replace('🌏', '').replace('💃', '')
    text = re.sub(r'\s*,\s*', ', ', text)
    text = re.sub(r'(?:,\s*){2,}', ', ', text)
    text = text.strip(' ,')
    return text if text else pd.NA


def parse_salary(value):
    if pd.isna(value):
        return (float('nan'), float('nan'))
    matches = re.findall(r'\$\s*([\d,]+)\s*([kK]?)', str(value))
    amounts = []
    for digits, suffix in matches:
        amount = float(digits.replace(',', ''))
        if suffix.lower() == 'k':
            amount *= 1000
        amounts.append(amount)
    if not amounts:
        return (float('nan'), float('nan'))
    if len(amounts) == 1:
        return (amounts[0], amounts[0])
    return (amounts[0], amounts[1])


def main():
    df = pd.read_csv(INPUT_FILE)
    missing_columns = set(COLUMNS) - set(df.columns)
    if missing_columns:
        raise ValueError(f'Missing required columns: {sorted(missing_columns)}')

    original_count = len(df)
    df = df.drop_duplicates().copy()
    duplicate_count = original_count - len(df)

    df['Location'] = df['Location'].apply(clean_location)
    df['Title'] = df['Title'].astype('string').str.strip()
    df['Skills'] = df['Skills'].astype('string').str.strip()

    salary_columns = df['Salary'].apply(parse_salary).apply(pd.Series)
    salary_columns.columns = ['min_salary', 'max_salary']
    salary_columns.index = df.index
    df[['min_salary', 'max_salary']] = salary_columns

    invalid_range = (df['min_salary'] > df['max_salary']).fillna(False)
    if invalid_range.any():
        raise ValueError(f'Invalid salary ranges: {invalid_range.sum()}')

    if df['Title'].isna().any() or df['Title'].eq('').any():
        raise ValueError('Missing job titles detected')

    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f'Original rows: {original_count}')
    print(f'Duplicate rows removed: {duplicate_count}')
    print(f'Cleaned rows: {len(df)}')
    print(f'Rows with salary data: {df["min_salary"].notna().sum()}')
    print('Missing values:')
    print(df.isna().sum().to_string())
    print(f'Saved to: {OUTPUT_FILE}')


if __name__ == '__main__':
    main()

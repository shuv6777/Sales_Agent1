import pandas as pd


def load_dataset(csv_path):
    # Try multiple encodings
    try:
        df = pd.read_csv(csv_path, encoding="utf-8")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(csv_path, encoding="latin1")
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, encoding="cp1252")

    # Ensure order_date is datetime
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    # Drop invalid dates
    df = df.dropna(subset=["order_date"])

    dataset_start_date = df["order_date"].min()
    dataset_end_date = df["order_date"].max()

    return {
        "df": df,
        "dataset_start_date": dataset_start_date,
        "dataset_end_date": dataset_end_date,
        "dataset_start_year": dataset_start_date.year,
        "dataset_end_year": dataset_end_date.year,
        "reference_date": dataset_end_date
    }
import pandas as pd
import re
from datetime import timedelta
from festival_llm import fetch_festival_date_from_llm


# =========================
# FESTIVAL WINDOW DICTIONARY
# =========================
FESTIVAL_WINDOWS = {
    "diwali": {"before": 30, "after": 15},
    "navratri": {"before": 20, "after": 10},
    "dussehra": {"before": 15, "after": 7},
    "akshaya tritiya": {"before": 10, "after": 5},
    "christmas": {"before": 15, "after": 7},
    "eid": {"before": 15, "after": 7}
}


# =========================
# LOAD FESTIVAL CACHE
# =========================
def load_festival_cache():
    try:
        return pd.read_csv("festival_cache.csv")
    except FileNotFoundError:
        return pd.DataFrame(
            columns=[
                "festival_name",
                "year",
                "festival_date",
                "source",
                "verified"
            ]
        )


# =========================
# SAVE TO FESTIVAL CACHE
# =========================
def save_festival_to_cache(festival_name, year, festival_date):

    cache_df = load_festival_cache()

    existing_match = cache_df[
        (cache_df["festival_name"].str.lower() == festival_name.lower()) &
        (cache_df["year"] == year)
    ]

    # Prevent duplicates
    if existing_match.empty:

        new_row = pd.DataFrame([{
            "festival_name": festival_name.lower(),
            "year": year,
            "festival_date": festival_date,
            "source": "llm",
            "verified": True
        }])

        updated_cache = pd.concat(
            [cache_df, new_row],
            ignore_index=True
        )

        updated_cache.to_csv(
            "festival_cache.csv",
            index=False
        )


# =========================
# MAIN FESTIVAL ENGINE
# =========================
def process_festival_query(
    route_result,
    cleaned_query,
    dataset_info
):

    cache_df = load_festival_cache()

    festival_name = route_result["sub_type"]

    # =========================
    # YEAR DETECTION
    # =========================
    year_match = re.search(
        r"\b(20\d{2})\b",
        cleaned_query
    )

    if year_match:
        target_year = int(year_match.group(1))

    else:
        target_year = dataset_info["reference_date"].year

        if "last" in cleaned_query:
            target_year -= 1

    # =========================
    # CACHE LOOKUP
    # =========================
    match = cache_df[
        (cache_df["festival_name"].str.lower() == festival_name.lower()) &
        (cache_df["year"] == target_year)
    ]

    # =========================
    # CACHE MISS → LLM FETCH
    # =========================
    if match.empty:

        print("\n[DEBUG] Cache miss detected. Attempting LLM fetch...")

        fetched_date = fetch_festival_date_from_llm(
            festival_name,
            target_year
        )

        print(f"[DEBUG] Fetched date: {fetched_date}")

        if fetched_date:

            save_festival_to_cache(
                festival_name,
                target_year,
                fetched_date
            )

            # Reload cache
            cache_df = load_festival_cache()

            match = cache_df[
                (cache_df["festival_name"].str.lower() == festival_name.lower()) &
                (cache_df["year"] == target_year)
            ]

        else:
            return {
                "valid": False,
                "message": f"{festival_name.title()} {target_year} not found in cache and LLM fetch failed."
            }

    # =========================
    # PARSE FESTIVAL DATE
    # =========================
    festival_date = pd.to_datetime(
        match.iloc[0]["festival_date"],
        errors="coerce"
    )

    if pd.isna(festival_date):
        return {
            "valid": False,
            "message": f"Festival date parsing failed for {festival_name} {target_year}."
        }

    # =========================
    # WINDOW LOGIC
    # =========================
    window = FESTIVAL_WINDOWS.get(
        festival_name.lower(),
        {"before": 15, "after": 7}
    )

    start_date = festival_date - timedelta(
        days=window["before"]
    )

    end_date = festival_date + timedelta(
        days=window["after"]
    )

    # =========================
    # DATASET BOUNDARY CHECK
    # =========================
    dataset_start = dataset_info["dataset_start_date"]
    dataset_end = dataset_info["dataset_end_date"]

    if start_date < dataset_start or end_date > dataset_end:

        closest_valid_year = dataset_info["reference_date"].year

        return {
            "valid": False,
            "festival_name": festival_name,
            "festival_date": str(festival_date.date()),
            "year": target_year,
            "start_date": str(start_date.date()),
            "end_date": str(end_date.date()),
            "dataset_start": str(dataset_start.date()),
            "dataset_end": str(dataset_end.date()),
            "suggestion": f"{festival_name} {closest_valid_year} sales",
            "message": "Festival window falls outside dataset boundaries."
        }

    # =========================
    # SUCCESS
    # =========================
    return {
        "valid": True,
        "festival_name": festival_name,
        "festival_date": str(festival_date.date()),
        "year": target_year,
        "start_date": str(start_date.date()),
        "end_date": str(end_date.date()),
        "source": match.iloc[0]["source"],
        "message": "Success"
    }
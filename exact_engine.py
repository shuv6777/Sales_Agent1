import calendar


def get_month_number(month_str):
    month_map = {
        "jan": 1, "january": 1,
        "feb": 2, "february": 2,
        "mar": 3, "march": 3,
        "apr": 4, "april": 4,
        "may": 5,
        "jun": 6, "june": 6,
        "jul": 7, "july": 7,
        "aug": 8, "august": 8,
        "sep": 9, "september": 9,
        "oct": 10, "october": 10,
        "nov": 11, "november": 11,
        "dec": 12, "december": 12
    }
    return month_map.get(month_str.lower())


def get_month_range(year, month):
    start_date = f"{year}-{month:02d}-01"
    last_day = calendar.monthrange(year, month)[1]
    end_date = f"{year}-{month:02d}-{last_day}"
    return start_date, end_date


def get_quarter_range(year, quarter):
    quarter_map = {
        "q1": (1, 3),
        "q2": (4, 6),
        "q3": (7, 9),
        "q4": (10, 12)
    }

    start_month, end_month = quarter_map[quarter]

    start_date = f"{year}-{start_month:02d}-01"
    last_day = calendar.monthrange(year, end_month)[1]
    end_date = f"{year}-{end_month:02d}-{last_day}"

    return start_date, end_date


def process_exact_query(route_result, dataset_info):
    dataset_start = dataset_info["dataset_start_date"]
    dataset_end = dataset_info["dataset_end_date"]

    sub_type = route_result["sub_type"]
        # =========================
    # MULTI MONTH RANGE
    # =========================
    if route_result["query_class"] == "exact_multi":

        start_month_str = sub_type["start_month"]
        end_month_str = sub_type["end_month"]
        year = int(sub_type["year"])

        start_month = get_month_number(start_month_str)
        end_month = get_month_number(end_month_str)

        if not start_month or not end_month:
            return {
                "valid": False,
                "message": "Invalid multi-month query"
            }

        # Ensure chronological order
        if start_month > end_month:
            start_month, end_month = end_month, start_month

        start_str = f"{year}-{start_month:02d}-01"

        last_day = calendar.monthrange(year, end_month)[1]
        end_str = f"{year}-{end_month:02d}-{last_day}"

        start = dataset_start.__class__.fromisoformat(start_str)
        end = dataset_end.__class__.fromisoformat(end_str)

        # Boundary check
        if start < dataset_start or end > dataset_end:
            return {
                "valid": False,
                "start_date": str(start.date()),
                "end_date": str(end.date()),
                "message": "Requested exact multi-month range falls outside dataset boundaries."
            }

        return {
            "valid": True,
            "start_date": str(start.date()),
            "end_date": str(end.date()),
            "message": "Success"
        }

    # =========================
    # MONTH + YEAR
    # =========================
    if "_" in sub_type and sub_type[:2].isalpha():

        parts = sub_type.split("_")
        month_str = parts[0]
        year = int(parts[1])

        month = get_month_number(month_str)

        if not month:
            return {
                "valid": False,
                "message": f"Invalid month: {month_str}"
            }

        start_str, end_str = get_month_range(year, month)

    # =========================
    # QUARTER + YEAR
    # =========================
    elif "_" in sub_type and sub_type.lower().startswith("q"):

        parts = sub_type.split("_")
        quarter = parts[0].lower()
        year = int(parts[1])

        start_str, end_str = get_quarter_range(year, quarter)

    # =========================
    # YEAR ONLY
    # =========================
    elif sub_type.isdigit():

        year = int(sub_type)

        start_str = f"{year}-01-01"
        end_str = f"{year}-12-31"

    else:
        return {
            "valid": False,
            "message": f"Unsupported exact query: {sub_type}"
        }

    # Convert to datetime
    start = dataset_start.__class__.fromisoformat(start_str)
    end = dataset_end.__class__.fromisoformat(end_str)

    # =========================
    # DATASET BOUNDARY CHECK
    # =========================
    if start < dataset_start or end > dataset_end:
        return {
            "valid": False,
            "start_date": str(start.date()),
            "end_date": str(end.date()),
            "message": "Requested exact range falls outside dataset boundaries."
        }

    return {
        "valid": True,
        "start_date": str(start.date()),
        "end_date": str(end.date()),
        "message": "Success"
    }
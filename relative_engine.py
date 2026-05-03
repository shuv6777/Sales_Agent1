import calendar
from datetime import timedelta


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


def get_month_start_end(year, month):
    start_date = f"{year}-{month:02d}-01"
    last_day = calendar.monthrange(year, month)[1]
    end_date = f"{year}-{month:02d}-{last_day}"
    return start_date, end_date


def process_relative_query(route_result, dataset_info):
    reference_date = dataset_info["reference_date"]
    dataset_start = dataset_info["dataset_start_date"]
    dataset_end = dataset_info["dataset_end_date"]

    query_class = route_result["query_class"]
    sub_type = route_result["sub_type"]

    # =========================
    # BASIC RELATIVE
    # =========================
    if query_class == "relative":

        if sub_type == "today":
            start = end = reference_date

        elif sub_type == "yesterday":
            start = end = reference_date - timedelta(days=1)

        elif sub_type == "last 3 days":
            start = reference_date - timedelta(days=3)
            end = reference_date

        elif sub_type == "last 7 days":
            start = reference_date - timedelta(days=7)
            end = reference_date

        elif sub_type == "last 15 days":
            start = reference_date - timedelta(days=15)
            end = reference_date

        elif sub_type == "last 30 days":
            start = reference_date - timedelta(days=30)
            end = reference_date

        elif sub_type == "this month":
            start = reference_date.replace(day=1)
            end = reference_date

        elif sub_type == "last month":
            first_day_this_month = reference_date.replace(day=1)
            end = first_day_this_month - timedelta(days=1)
            start = end.replace(day=1)

        else:
            return {
                "valid": False,
                "message": f"Unsupported relative query: {sub_type}"
            }

    # =========================
    # RELATIVE EXACT
    # =========================
    elif query_class == "relative_exact":

        parts = sub_type.split("_")
        context = parts[0]   # last / this
        month_str = parts[1]

        target_month = get_month_number(month_str)

        if not target_month:
            return {
                "valid": False,
                "message": f"Invalid month detected: {month_str}"
            }

        reference_year = reference_date.year
        reference_month = reference_date.month

        if context == "last":
            if target_month < reference_month:
                target_year = reference_year
            else:
                target_year = reference_year - 1

        elif context == "this":
            target_year = reference_year

        else:
            return {
                "valid": False,
                "message": f"Unsupported context: {context}"
            }

        start_str, end_str = get_month_start_end(target_year, target_month)

        start = dataset_info["df"]["order_date"].min().__class__(target_year, target_month, 1)
        end = dataset_info["df"]["order_date"].min().__class__(
            target_year,
            target_month,
            int(end_str.split("-")[2])
        )

    else:
        return {
            "valid": False,
            "message": "Not a relative query"
        }

    # =========================
    # DATASET BOUNDARY CHECK
    # =========================
    if start < dataset_start or end > dataset_end:
        return {
            "valid": False,
            "start_date": str(start.date()),
            "end_date": str(end.date()),
            "message": "Requested range falls outside dataset boundaries."
        }

    return {
        "valid": True,
        "start_date": str(start.date()),
        "end_date": str(end.date()),
        "message": "Success"
    }
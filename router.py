import re


def route_query(cleaned_query):

    # =========================
    # FESTIVAL / OCCASION KEYWORDS
    # =========================
    festival_keywords = [
        "diwali",
        "navratri",
        "dussehra",
        "akshaya tritiya",
        "christmas",
        "eid",
        "valentine",
        "valentines",
        "valentine's day",
        "mother's day",
        "fathers day",
        "father's day",
        "friendship day",
        "women's day",
        "new year",
        "black friday",
        "cyber monday"
    ]

    # =========================
    # FESTIVAL / OCCASION ROUTING
    # =========================
    matched_keyword = next(
        (
            keyword
            for keyword in festival_keywords
            if keyword in cleaned_query
        ),
        None
    )

    if matched_keyword:

        return {
            "query_class": "festival",
            "sub_type": matched_keyword,
            "raw_query": cleaned_query
        }

    # =========================
    # RELATIVE QUERIES
    # =========================
    relative_keywords = [
        "today",
        "yesterday",
        "last week",
        "this week",
        "last month",
        "this month",
        "last year",
        "this year"
    ]

    matched_relative = next(
        (
            keyword
            for keyword in relative_keywords
            if keyword in cleaned_query
        ),
        None
    )

    if matched_relative:

        return {
            "query_class": "relative",
            "sub_type": matched_relative,
            "raw_query": cleaned_query
        }

    # =========================
    # MULTI MONTH EXACT
    # =========================
    month_pattern = (
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
    )

    month_matches = re.findall(
        month_pattern,
        cleaned_query
    )

    year_match = re.search(
        r"\b(20\d{2})\b",
        cleaned_query
    )

    if len(month_matches) >= 2:

        return {
            "query_class": "exact_multi",
            "sub_type": month_matches,
            "year": int(year_match.group(1)) if year_match else None,
            "raw_query": cleaned_query
        }

    # =========================
    # SINGLE MONTH EXACT
    # =========================
    elif len(month_matches) == 1:

        return {
            "query_class": "exact",
            "sub_type": month_matches[0],
            "year": int(year_match.group(1)) if year_match else None,
            "raw_query": cleaned_query
        }

    # =========================
    # FALLBACK
    # =========================
    return {
        "query_class": "unknown",
        "sub_type": None,
        "raw_query": cleaned_query
    }
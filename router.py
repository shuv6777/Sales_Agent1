import re


# =========================
# KEYWORD DICTIONARIES
# =========================

RELATIVE_KEYWORDS = [
    "today",
    "yesterday",
    "recent",
    "last 3 days",
    "last 7 days",
    "last 15 days",
    "last 30 days",
    "last month",
    "this month",
    "last year",
    "this year"
]

FESTIVAL_KEYWORDS = [
    "diwali",
    "navratri",
    "dussehra",
    "akshaya tritiya",
    "karva chauth",
    "onam",
    "pongal",
    "eid",
    "christmas"
]

SEASONAL_KEYWORDS = [
    "wedding season",
    "festive season",
    "payday",
    "salary week",
    "bridal season"
]

MONTHS = [
    "jan", "january",
    "feb", "february",
    "mar", "march",
    "apr", "april",
    "may",
    "jun", "june",
    "jul", "july",
    "aug", "august",
    "sep", "september",
    "oct", "october",
    "nov", "november",
    "dec", "december"
]


# =========================
# MONTH CONTEXT DETECTOR
# =========================

def detect_month_context(query):
    detected_months = []

    for month in MONTHS:
        if re.search(rf"\b{month}\b", query):
            detected_months.append(month)

    # Remove duplicates
    unique_months = []
    for m in detected_months:
        if m not in unique_months:
            unique_months.append(m)

    year_match = re.search(r"\b(20\d{2})\b", query)

    # =========================
    # MULTI MONTH
    # =========================
    if len(unique_months) >= 2:

        if year_match:
            return {
                "query_class": "exact_multi",
                "sub_type": {
                    "start_month": unique_months[0],
                    "end_month": unique_months[1],
                    "year": year_match.group(1)
                },
                "clarification_needed": False
            }

        return {
            "query_class": "exact_multi",
            "sub_type": {
                "start_month": unique_months[0],
                "end_month": unique_months[1]
            },
            "clarification_needed": True,
            "clarification_question": f"Which year do you mean for {unique_months[0]} to {unique_months[1]}?"
        }

    # =========================
    # SINGLE MONTH
    # =========================
    for month in unique_months:

        if year_match:
            return {
                "query_class": "exact",
                "sub_type": f"{month}_{year_match.group(1)}",
                "clarification_needed": False
            }

        if f"last {month}" in query:
            return {
                "query_class": "relative_exact",
                "sub_type": f"last_{month}",
                "clarification_needed": False
            }

        if f"this {month}" in query:
            return {
                "query_class": "relative_exact",
                "sub_type": f"this_{month}",
                "clarification_needed": False
            }

        return {
            "query_class": "exact",
            "sub_type": month,
            "clarification_needed": True,
            "clarification_question": f"Which year do you mean for {month}?"
        }

    return None


# =========================
# MAIN ROUTER
# =========================

def route_query(query):

    # FESTIVAL
    for keyword in FESTIVAL_KEYWORDS:
        if keyword in query:
            return {
                "query_class": "festival",
                "sub_type": keyword,
                "clarification_needed": False
            }

    # SEASONAL
    for keyword in SEASONAL_KEYWORDS:
        if keyword in query:
            return {
                "query_class": "seasonal",
                "sub_type": keyword,
                "clarification_needed": False
            }

    # RELATIVE
    for keyword in RELATIVE_KEYWORDS:
        if keyword in query:

            if keyword == "recent":
                return {
                    "query_class": "relative",
                    "sub_type": "recent",
                    "clarification_needed": True,
                    "clarification_question": "Do you mean last 3 days, last 7 days, or last 30 days?"
                }

            return {
                "query_class": "relative",
                "sub_type": keyword,
                "clarification_needed": False
            }

    # MONTH CONTEXT
    month_result = detect_month_context(query)
    if month_result:
        return month_result

    # QUARTER
    quarter_match = re.search(r"\b(q[1-4]|quarter [1-4])\b", query)

    if quarter_match:
        year_match = re.search(r"\b(20\d{2})\b", query)

        if year_match:
            return {
                "query_class": "exact",
                "sub_type": f"{quarter_match.group(1)}_{year_match.group(1)}",
                "clarification_needed": False
            }

        return {
            "query_class": "exact",
            "sub_type": quarter_match.group(1),
            "clarification_needed": True,
            "clarification_question": f"Which year do you mean for {quarter_match.group(1)}?"
        }

    # YEAR ONLY
    year_match = re.search(r"\b(20\d{2})\b", query)

    if year_match:
        return {
            "query_class": "exact",
            "sub_type": year_match.group(1),
            "clarification_needed": False
        }

    # FALLBACK
    return {
        "query_class": "unknown",
        "sub_type": None,
        "clarification_needed": True,
        "clarification_question": "I couldn’t clearly understand the date intent. Please rephrase."
    }
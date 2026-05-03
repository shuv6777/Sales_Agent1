import re


ALIASES = {
    "deepavali": "diwali",
    "dasara": "dussehra",
    "shaadi": "wedding",
    "qtr": "quarter"
}


def preprocess_query(query):
    # Lowercase
    query = query.lower().strip()

    # Remove punctuation
    query = re.sub(r"[^\w\s]", "", query)

    # Alias replacement
    for old, new in ALIASES.items():
        query = query.replace(old, new)

    # Remove extra spaces
    query = re.sub(r"\s+", " ", query)

    return query
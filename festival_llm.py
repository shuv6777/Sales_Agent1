import requests
import re
import os


def fetch_festival_date_from_llm(festival_name, year):
    """
    Fetches exact festival date using OpenRouter API.
    Returns:
        YYYY-MM-DD string if successful
        None if failed
    """

    try:
        # =========================
        # API KEY FROM ENV VARIABLE
        # =========================
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            print(
                "[ERROR] OPENROUTER_API_KEY not found in environment variables."
            )
            return None

        # =========================
        # PROMPT
        # =========================
        prompt = (
            f"What was the exact date of {festival_name} in India in {year}? "
            f"Reply ONLY in YYYY-MM-DD format."
        )

        # =========================
        # API CALL
        # =========================
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            timeout=30
        )

        # =========================
        # STATUS CHECK
        # =========================
        if response.status_code != 200:
            print(
                f"[ERROR] OpenRouter API failed | Status: {response.status_code}"
            )
            print(
                f"[ERROR] Response: {response.text}"
            )
            return None

        # =========================
        # PARSE RESPONSE
        # =========================
        data = response.json()

        print(
            f"[DEBUG] Raw API Response: {data}"
        )

        answer = (
            data["choices"][0]["message"]["content"]
            .strip()
        )

        print(
            f"[DEBUG] Parsed Answer: {answer}"
        )

        # =========================
        # VALIDATE DATE FORMAT
        # =========================
        if re.match(
            r"^\d{4}-\d{2}-\d{2}$",
            answer
        ):
            return answer

        print(
            "[ERROR] LLM response not in valid YYYY-MM-DD format."
        )

        return None

    # =========================
    # GLOBAL FAILURE
    # =========================
    except Exception as e:

        print(
            f"LLM Fetch Error: {e}"
        )

        return None
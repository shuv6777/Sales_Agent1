import requests
import re


def fetch_festival_date_from_llm(festival_name, year):
    try:
        api_key = "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"

        prompt = (
            f"What was the exact date of {festival_name} in India in {year}? "
            f"Reply ONLY in YYYY-MM-DD format."
        )

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
            }
        )

        data = response.json()

        print(f"[DEBUG] Raw API Response: {data}")

        answer = data["choices"][0]["message"]["content"].strip()

        print(f"[DEBUG] Parsed Answer: {answer}")

        if re.match(r"^\d{4}-\d{2}-\d{2}$", answer):
            return answer

        return None

    except Exception as e:
        print(f"LLM Fetch Error: {e}")
        return None
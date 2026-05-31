"""
Gemini AI service — handles all interaction with Google's Gemini API.

Extracted from main.py's get_summary_from_gemini() function.
"""

import os
import requests


async def get_summary(text):
    """Send text to Gemini API and return the generated response.

    Args:
        text: The prompt text to send to the model.

    Returns:
        The generated text response, or an error message string.
    """
    chat_history = [{"role": "user", "parts": [{"text": text}]}]
    payload = {"contents": chat_history}

    api_key = os.getenv('API_KEY')
    model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    api_url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )

    try:
        response = requests.post(
            api_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
        )
        response.raise_for_status()
        result = response.json()

        if (result.get('candidates')
                and result['candidates'][0].get('content')
                and result['candidates'][0]['content'].get('parts')):
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            print("API Response was not in the expected format:", result)
            return "Could not extract a valid summary from the API response."

    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        return f"Error communicating with the analysis service: {e}"
    except (KeyError, IndexError, TypeError) as e:
        print(f"API Response Parsing Error: {e}")
        return "Error parsing the summary from the API response."

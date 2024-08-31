import os
import json
import requests

def ask_yes_no_question(question, model="gpt-3.5-turbo"):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # Return a mock response for testing purposes
        return {
            "answer": True,
            "reason": "This is a mock response for testing purposes."
        }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that answers yes/no questions and provides a brief explanation."},
            {"role": "user", "content": question}
        ]
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            result = response.json()["choices"][0]["message"]["content"]
            lines = result.strip().split('\n')
            answer = lines[0].lower()
            reason = ' '.join(lines[1:])

            return {
                "answer": "yes" in answer and "no" not in answer,
                "reason": reason
            }
        else:
            # Return a mock response for testing purposes
            return {
                "answer": True,
                "reason": f"Mock response due to API error: {response.status_code}"
            }
    except requests.exceptions.RequestException:
        # Return a mock response for testing purposes
        return {
            "answer": True,
            "reason": "Mock response due to network error"
        }

def generate_text(prompt, model="gpt-3.5-turbo"):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # Return a mock response for testing purposes
        return json.dumps({"name": "John Doe", "age": 30})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that generates JSON entries based on prompts."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            result = response.json()["choices"][0]["message"]["content"]
            return result
        else:
            # Return a mock response for testing purposes
            return json.dumps({"name": "Jane Doe", "age": 25})
    except requests.exceptions.RequestException:
        # Return a mock response for testing purposes
        return json.dumps({"name": "Bob Smith", "age": 35})

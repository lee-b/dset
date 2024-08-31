import os
import json
import requests

def ask_yes_no_question(question, model="gpt-3.5-turbo"):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

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
        raise Exception(f"API call failed with status code {response.status_code}: {response.text}")

def generate_text(prompt, model="gpt-3.5-turbo"):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

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

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        result = response.json()["choices"][0]["message"]["content"]
        return result
    else:
        raise Exception(f"API call failed with status code {response.status_code}: {response.text}")

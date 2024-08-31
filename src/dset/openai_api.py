import requests
import os
import json

def call_openai_api(prompt, model="gpt-3.5-turbo"):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"API call failed with status code {response.status_code}: {response.text}")

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
            {"role": "system", "content": "You are a helpful assistant that answers yes/no questions."},
            {"role": "user", "content": question}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "boolean",
                        "description": "The yes (true) or no (false) answer to the question"
                    },
                    "reason": {
                        "type": "string",
                        "description": "A brief explanation for the answer"
                    }
                },
                "required": ["answer", "reason"]
            }
        }
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        result = response.json()["choices"][0]["message"]["content"]
        return json.loads(result)
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
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"API call failed with status code {response.status_code}: {response.text}")

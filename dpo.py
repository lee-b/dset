import argparse
import json
import os
import sys
from pydantic import BaseModel
import openai

class DatasetItem(BaseModel):
    text: str

def process_dataset(input_file, output_file, model, prompt_file=None, include_prompt=None, exclude_prompt=None):
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    openai.api_base = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')

    def generate_text(prompt, max_tokens=256):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                n=1,
                temperature=0.7,
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"Error in text generation: {e}", file=sys.stderr)
            return ""

    if prompt_file:
        with open(prompt_file, 'r') as f_prompt:
            prompt = f_prompt.read().strip()
    else:
        prompt = None

    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            data = json.loads(line)
            text = data['text']
            if include_prompt:
                response = generate_text(f"{include_prompt} {text}")
            elif exclude_prompt:
                response = generate_text(f"{exclude_prompt} {text}")
            elif prompt:
                response = generate_text(f"{prompt} {text}")
            else:
                response = generate_text(text)
            f_out.write(json.dumps({'text': response}) + '\n')

def generate_synthetic_dataset(input_file, output_file, model):
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    openai.api_base = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')

    def generate_synthetic_item(prompt="Generate a synthetic dataset item", max_tokens=256):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                n=1,
                temperature=0.7,
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"Error in synthetic item generation: {e}", file=sys.stderr)
            return ""

    with open(output_file, 'w') as f_out:
        for _ in range(100):  # generate 100 synthetic dataset items
            response = generate_synthetic_item()
            f_out.write(json.dumps({'text': response}) + '\n')

def generate_dataset_from_prompt_file(prompt_file, output_file, model, num_items=100):
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    openai.api_base = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')

    def generate_item(prompt, max_tokens=256):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                n=1,
                temperature=0.7,
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"Error in item generation: {e}", file=sys.stderr)
            return ""

    with open(prompt_file, 'r') as f_prompt:
        prompt = f_prompt.read().strip()

    with open(output_file, 'w') as f_out:
        for _ in range(num_items):
            response = generate_item(prompt)
            f_out.write(json.dumps({'text': response}) + '\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input file')
    parser.add_argument('-o', '--output', help='output file')
    parser.add_argument('--generate', action='store_true', help='generate synthetic dataset')
    parser.add_argument('--model', default='gpt-4', help='model to use for text generation')
    parser.add_argument('--prompt-file', help='file containing prompt for dataset generation or transformation')
    parser.add_argument('--include-prompt', help='prompt for including items in the dataset')
    parser.add_argument('--exclude-prompt', help='prompt for excluding items from the dataset')
    parser.add_argument('--num-items', type=int, default=100, help='number of items to generate when using a prompt file')
    args = parser.parse_args()

    if args.input and args.output:
        input_file = args.input
        output_file = args.output
    else:
        input_file = sys.stdin
        output_file = sys.stdout

    if args.prompt_file or args.include_prompt or args.exclude_prompt:
        process_dataset(input_file, output_file, model=args.model, prompt_file=args.prompt_file, include_prompt=args.include_prompt, exclude_prompt=args.exclude_prompt)
    elif args.generate:
        generate_synthetic_dataset(input_file, output_file, model=args.model)
    else:
        process_dataset(input_file, output_file, model=args.model)

if __name__ == '__main__':
    main()

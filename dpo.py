import argparse
import json
import os
import sys
from pydantic import BaseModel
import openai

class DatasetItem(BaseModel):
    text: str

def process_dataset(input_file, output_file):
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    openai.api_base = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')

    def generate_text(prompt, max_tokens=256):
        try:
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=max_tokens,
                n=1,
                stop=None,
                temperature=0.7,
            )
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"Error in text generation: {e}", file=sys.stderr)
            return ""

    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            data = json.loads(line)
            text = data['text']
            response = generate_text(text)
            f_out.write(json.dumps({'text': response}) + '\n')

def generate_synthetic_dataset(input_file, output_file):
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    openai.api_base = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')

    def generate_synthetic_item(prompt="Generate a synthetic dataset item", max_tokens=256):
        try:
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=max_tokens,
                n=1,
                stop=None,
                temperature=0.7,
            )
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"Error in synthetic item generation: {e}", file=sys.stderr)
            return ""

    with open(output_file, 'w') as f_out:
        for _ in range(100):  # generate 100 synthetic dataset items
            response = generate_synthetic_item()
            f_out.write(json.dumps({'text': response}) + '\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input file')
    parser.add_argument('-o', '--output', help='output file')
    parser.add_argument('--generate', action='store_true', help='generate synthetic dataset')
    args = parser.parse_args()

    if args.input and args.output:
        input_file = args.input
        output_file = args.output
    else:
        input_file = sys.stdin
        output_file = sys.stdout

    if args.generate:
        generate_synthetic_dataset(input_file, output_file)
    else:
        process_dataset(input_file, output_file)

if __name__ == '__main__':
    main()

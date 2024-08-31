import argparse
import json
import os
import sys
from pydantic import BaseModel
import openai

class DatasetItem(BaseModel):
    text: str

def load_prompt(file_or_string):
    if os.path.isfile(file_or_string):
        with open(file_or_string, 'r') as f:
            return f.read().strip()
    return file_or_string

def generate_text(model, prompt, max_tokens=256):
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

def process_dataset(input_file, output_file, model, prompt):
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            data = json.loads(line)
            text = data['text']
            response = generate_text(model, f"{prompt} {text}")
            f_out.write(json.dumps({'text': response}) + '\n')

def generate_synthetic_dataset(output_file, model, prompt, num_items):
    with open(output_file, 'w') as f_out:
        for _ in range(num_items):
            response = generate_text(model, prompt)
            f_out.write(json.dumps({'text': response}) + '\n')

def filter_dataset(input_file, output_file, model, include_prompt, exclude_prompt):
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            data = json.loads(line)
            text = data['text']
            if include_prompt:
                if generate_text(model, f"{include_prompt}\n\nText: {text}\n\nAnswer (Yes/No):").lower() == "yes":
                    f_out.write(line)
            elif exclude_prompt:
                if generate_text(model, f"{exclude_prompt}\n\nText: {text}\n\nAnswer (Yes/No):").lower() == "no":
                    f_out.write(line)

def ask_dataset_question(input_file, question, model):
    dataset = []
    with open(input_file, 'r') as f:
        for line in f:
            dataset.append(json.loads(line)['text'])

    dataset_str = "\n".join(dataset)
    prompt = f"Given the following dataset:\n\n{dataset_str}\n\nQuestion: {question}\n\nAnswer (Yes/No):"
    
    return generate_text(model, prompt, max_tokens=1)

def check_dataset_assertion(input_file, assertion, model):
    with open(input_file, 'r') as f:
        for i, line in enumerate(f, 1):
            text = json.loads(line)['text']
            prompt = f"Given the following text:\n\n{text}\n\nAssertion: {assertion}\n\nIs this assertion true for the given text? Answer (Yes/No):"
            response = generate_text(model, prompt, max_tokens=1).lower()
            if response != "yes":
                print(f"Assertion failed for item {i}: {text}")
                return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Dataset Processing Operations")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Ask command
    ask_parser = subparsers.add_parser("ask", help="Ask a question about the dataset")
    ask_parser.add_argument("input", help="Input file")
    ask_parser.add_argument("question", help="Question to ask about the dataset")
    ask_parser.add_argument("--model", default="gpt-4", help="Model to use for text generation")

    # Generate command
    gen_parser = subparsers.add_parser("gen", help="Generate a synthetic dataset")
    gen_parser.add_argument("output", help="Output file")
    gen_parser.add_argument("prompt", nargs="?", help="Prompt for dataset generation")
    gen_parser.add_argument("--prompt-file", help="File containing prompt for dataset generation")
    gen_parser.add_argument("--model", default="gpt-4", help="Model to use for text generation")
    gen_parser.add_argument("--num-items", type=int, default=100, help="Number of items to generate")

    # Process command
    process_parser = subparsers.add_parser("process", help="Process an existing dataset")
    process_parser.add_argument("input", help="Input file")
    process_parser.add_argument("output", help="Output file")
    process_parser.add_argument("prompt", nargs="?", help="Prompt for dataset processing")
    process_parser.add_argument("--prompt-file", help="File containing prompt for dataset processing")
    process_parser.add_argument("--model", default="gpt-4", help="Model to use for text generation")

    # Filter command
    filter_parser = subparsers.add_parser("filter", help="Filter an existing dataset")
    filter_parser.add_argument("input", help="Input file")
    filter_parser.add_argument("output", help="Output file")
    filter_parser.add_argument("--include", help="Prompt for including items in the dataset")
    filter_parser.add_argument("--include-file", help="File containing prompt for including items")
    filter_parser.add_argument("--exclude", help="Prompt for excluding items from the dataset")
    filter_parser.add_argument("--exclude-file", help="File containing prompt for excluding items")
    filter_parser.add_argument("--model", default="gpt-4", help="Model to use for text generation")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check an assertion for every item in the dataset")
    check_parser.add_argument("input", help="Input file")
    check_parser.add_argument("assertion", help="Assertion to check for each item in the dataset")
    check_parser.add_argument("--model", default="gpt-4", help="Model to use for text generation")

    args = parser.parse_args()

    openai.api_key = os.environ.get('OPENAI_API_KEY')
    openai.api_base = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')

    if args.command == "ask":
        answer = ask_dataset_question(args.input, args.question, args.model)
        print(f"Answer: {answer}")
    elif args.command == "gen":
        prompt = load_prompt(args.prompt_file) if args.prompt_file else args.prompt
        generate_synthetic_dataset(args.output, args.model, prompt, args.num_items)
    elif args.command == "process":
        prompt = load_prompt(args.prompt_file) if args.prompt_file else args.prompt
        process_dataset(args.input, args.output, args.model, prompt)
    elif args.command == "filter":
        include_prompt = load_prompt(args.include_file) if args.include_file else args.include
        exclude_prompt = load_prompt(args.exclude_file) if args.exclude_file else args.exclude
        filter_dataset(args.input, args.output, args.model, include_prompt, exclude_prompt)
    elif args.command == "check":
        result = check_dataset_assertion(args.input, args.assertion, args.model)
        if not result:
            sys.exit(1)
        print("All items in the dataset satisfy the assertion.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

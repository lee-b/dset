import json
import os
from dset.openai_api import ask_yes_no_question

def process_jsonl(file_path, question):
    results = []
    with open(file_path, 'r') as file:
        for line in file:
            entry = json.loads(line)
            result = ask_yes_no_question(f"{question}\nContext: {json.dumps(entry)}")
            results.append(result)
    return results

def ask_operation(input_file, question):
    results = process_jsonl(input_file, question)
    all_yes = all(result['answer'] for result in results)
    
    if all_yes:
        print("Yes, that is the case for all entries.")
    else:
        print("No, that is not the case for some entries.")
    
    print("\nReasons:")
    for result in results:
        print(f"- {result['reason']}")

def assert_operation(input_file, question):
    results = process_jsonl(input_file, question)
    all_yes = all(result['answer'] for result in results)
    
    if all_yes:
        print("Assertion passed: The condition is true for all entries.")
    else:
        print("Assertion failed: The condition is not true for all entries.")
        print("\nReasons for failures:")
        for result in results:
            if not result['answer']:
                print(f"- {result['reason']}")
        exit(1)

def split_operation(input_file, output_prefix, max_size):
    file_number = 1
    current_size = 0
    current_file = None
    file_sizes = []

    with open(input_file, 'r') as infile:
        for line in infile:
            line_size = len(line.encode('utf-8'))

            if current_file is None or current_size + line_size > max_size:
                if current_file:
                    current_file.close()
                    file_sizes.append(current_size)

                output_file = f"{output_prefix}_{file_number}.jsonl"
                current_file = open(output_file, 'w')
                print(f"Created file: {output_file}")
                current_size = 0
                file_number += 1

            current_file.write(line)
            current_size += line_size

    if current_file:
        current_file.close()
        file_sizes.append(current_size)

    print(f"\nTotal files created: {file_number - 1}")
    print(f"Minimum file size: {min(file_sizes)} bytes")
    print(f"Maximum file size: {max(file_sizes)} bytes")

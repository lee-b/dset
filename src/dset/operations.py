import json
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

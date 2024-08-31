import json
import os
from dset.openai_api import ask_yes_no_question, generate_text
from dset.dataset import DataSet
from dset.models import JsonLEntry

def ask_operation(config):
    dataset = DataSet(config.args.input)
    
    def processor(entry):
        return ask_yes_no_question(f"{config.args.raw_user_prompt}\nContext: {json.dumps(entry)}")
    
    all_yes = True
    reasons = []
    
    for result in dataset.process(processor):
        if not result['answer']:
            all_yes = False
        reasons.append(result['reason'])
    
    if all_yes:
        print("Yes, that is the case for all entries.")
    else:
        print("No, that is not the case for some entries.")
    
    print("\nReasons:")
    for reason in reasons:
        print(f"- {reason}")

def assert_operation(config):
    dataset = DataSet(config.args.input)
    
    def processor(entry):
        return ask_yes_no_question(f"{config.args.raw_user_prompt}\nContext: {json.dumps(entry)}")
    
    all_yes = True
    failure_reasons = []
    
    for result in dataset.process(processor):
        if not result['answer']:
            all_yes = False
            failure_reasons.append(result['reason'])
    
    if all_yes:
        print("Assertion passed: The condition is true for all entries.")
    else:
        print("Assertion failed: The condition is not true for all entries.")
        print("\nReasons for failures:")
        for reason in failure_reasons:
            print(f"- {reason}")
        exit(1)

def split_operation(config):
    dataset = DataSet(config.args.input)
    dataset.split(config.args.output, config.args.max_size)

def filter_operation(config):
    print(f"Filtering data from {config.args.input} to {config.args.output}")
    print(f"Requirement: {config.args.raw_user_prompt}")
    
    dataset = DataSet(config.args.input)
    
    def processor(entry):
        question = f"Does the following entry meet this requirement: '{config.args.raw_user_prompt}'?\nEntry: {json.dumps(entry)}"
        result = ask_yes_no_question(question)
        return result['answer'], entry
    
    os.makedirs(os.path.dirname(config.args.output), exist_ok=True)
    
    filtered_count = 0
    with open(config.args.output, 'w') as outfile:
        for include, entry in dataset.process(processor):
            if include:
                json.dump(entry, outfile)
                outfile.write('\n')
                filtered_count += 1
    
    print(f"Filtered {filtered_count} entries into {config.args.output}")

def merge_operation(config):
    print(f"Merging data from {config.args.input} to {config.args.output}")
    
    os.makedirs(os.path.dirname(config.args.output), exist_ok=True)
    
    merged_count = 0
    seen_entries = set()
    
    with open(config.args.output, 'w') as outfile:
        for input_path in config.args.input.split(','):
            dataset = DataSet(input_path.strip())
            
            for entry in dataset.process(lambda x: x):
                entry_str = json.dumps(entry, sort_keys=True)
                if entry_str not in seen_entries:
                    seen_entries.add(entry_str)
                    outfile.write(entry_str + '\n')
                    merged_count += 1
    
    print(f"Merged {merged_count} unique entries into {config.args.output}")

def generate_operation(config):
    print(f"Generating {config.args.num_entries} entries to {config.args.output}")
    print(f"Prompt: {config.args.raw_user_prompt}")
    
    os.makedirs(os.path.dirname(config.args.output), exist_ok=True)
    
    with open(config.args.output, 'w') as outfile:
        for _ in range(config.args.num_entries):
            entry = generate_entry(config.args.raw_user_prompt)
            json.dump(entry, outfile)
            outfile.write('\n')
    
    print(f"Generated {config.args.num_entries} entries into {config.args.output}")

def generate_entry(prompt):
    return json.loads(generate_text(f"Generate a JSON entry based on this prompt: {prompt}"))

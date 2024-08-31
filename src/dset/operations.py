import json
import os
from dset.openai_api import ask_yes_no_question
from dset.dataset import DataSet

def ask_operation(config):
    dataset = DataSet(config.args.input)
    
    def processor(entry):
        return ask_yes_no_question(f"{config.args.raw_user_prompt}\nContext: {json.dumps(entry)}")
    
    results = dataset.process(processor)
    
    all_yes = all(result['answer'] for result in results)
    
    if all_yes:
        print("Yes, that is the case for all entries.")
    else:
        print("No, that is not the case for some entries.")
    
    print("\nReasons:")
    for result in results:
        print(f"- {result['reason']}")

def assert_operation(config):
    dataset = DataSet(config.args.input)
    
    def processor(entry):
        return ask_yes_no_question(f"{config.args.raw_user_prompt}\nContext: {json.dumps(entry)}")
    
    results = dataset.process(processor)
    
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
        return result['answer']
    
    filtered_entries = []
    results = dataset.process(processor)
    
    for entry, should_include in zip(dataset.get_entries(), results):
        if should_include:
            filtered_entries.append(entry)
    
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(config.args.output), exist_ok=True)
    
    # Write the filtered entries to the output file
    with open(config.args.output, 'w') as outfile:
        for entry in filtered_entries:
            json.dump(entry, outfile)
            outfile.write('\n')
    
    print(f"Filtered {len(filtered_entries)} entries into {config.args.output}")

def merge_operation(config):
    print(f"Merging data from {config.args.input} to {config.args.output}")
    
    # Create a set to store unique entries
    merged_entries = set()

    # Process each input path
    for input_path in config.args.input.split(','):
        dataset = DataSet(input_path.strip())
        
        def processor(entry):
            # Convert the entry to a JSON string for hashing
            entry_str = json.dumps(entry, sort_keys=True)
            merged_entries.add(entry_str)
            return None  # We don't need to return anything for merging
        
        dataset.process(processor)

    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(config.args.output), exist_ok=True)

    # Write the merged entries to the output file
    with open(config.args.output, 'w') as outfile:
        for entry_str in merged_entries:
            outfile.write(entry_str + '\n')

    print(f"Merged {len(merged_entries)} unique entries into {config.args.output}")

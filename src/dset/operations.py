import json
import os
from dset.openai_api import ask_yes_no_question
from dset.dataset import DataSet

def ask_operation(input_path, question):
    dataset = DataSet(input_path)
    
    def processor(entry):
        return ask_yes_no_question(f"{question}\nContext: {json.dumps(entry)}")
    
    results = dataset.process(processor)
    
    all_yes = all(result['answer'] for result in results)
    
    if all_yes:
        print("Yes, that is the case for all entries.")
    else:
        print("No, that is not the case for some entries.")
    
    print("\nReasons:")
    for result in results:
        print(f"- {result['reason']}")

def assert_operation(input_path, question):
    dataset = DataSet(input_path)
    
    def processor(entry):
        return ask_yes_no_question(f"{question}\nContext: {json.dumps(entry)}")
    
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

def split_operation(input_path, output_prefix, max_size):
    dataset = DataSet(input_path)
    dataset.split(output_prefix, max_size)

def filter_operation(input_path, output_path, requirement):
    print(f"Filtering data from {input_path} to {output_path}")
    print(f"Requirement: {requirement}")
    
    dataset = DataSet(input_path)
    
    def processor(entry):
        question = f"Does the following entry meet this requirement: '{requirement}'?\nEntry: {json.dumps(entry)}"
        result = ask_yes_no_question(question)
        return result['answer']
    
    filtered_entries = []
    results = dataset.process(processor)
    
    for entry, should_include in zip(dataset.get_entries(), results):
        if should_include:
            filtered_entries.append(entry)
    
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write the filtered entries to the output file
    with open(output_path, 'w') as outfile:
        for entry in filtered_entries:
            json.dump(entry, outfile)
            outfile.write('\n')
    
    print(f"Filtered {len(filtered_entries)} entries into {output_path}")

def merge_operation(input_paths, output_path):
    print(f"Merging data from {input_paths} to {output_path}")
    
    # Create a set to store unique entries
    merged_entries = set()

    # Process each input path
    for input_path in input_paths.split(','):
        dataset = DataSet(input_path.strip())
        
        def processor(entry):
            # Convert the entry to a JSON string for hashing
            entry_str = json.dumps(entry, sort_keys=True)
            merged_entries.add(entry_str)
            return None  # We don't need to return anything for merging
        
        dataset.process(processor)

    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write the merged entries to the output file
    with open(output_path, 'w') as outfile:
        for entry_str in merged_entries:
            outfile.write(entry_str + '\n')

    print(f"Merged {len(merged_entries)} unique entries into {output_path}")

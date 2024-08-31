import json
import yaml
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Any
from dset.openai_api import ask_yes_no_question, generate_text
from dset.dataset import ReadableDataSet, WriteableDataSet
from dset.models import JsonLEntry

CHUNK_SIZE = 10  # Number of reasons to collect before summarizing

def summarize_reasons(config, reasons: List[str]) -> str:
    prompt = f"Summarize the following reasons:\n\n" + "\n".join(reasons)
    return generate_text(config, prompt)

def update_summary(config, previous_summary: str, chunk_summary: str) -> str:
    prompt = f"Combine and summarize these two summaries:\n\nPrevious summary: {previous_summary}\n\nNew chunk summary: {chunk_summary}"
    return generate_text(config, prompt)

def process_entries(dataset: ReadableDataSet, processor, config) -> Tuple[bool, List[str], str]:
    all_yes = True
    reasons = []
    current_chunk = []
    current_summary = ""
    
    with open(config.args.reasons_output, 'w') as reasons_file:
        for result in dataset.process(processor):
            if not result['answer']:
                all_yes = False
            
            reason_entry = {"answer": result['answer'], "reason": result['reason']}
            json.dump(reason_entry, reasons_file)
            reasons_file.write('\n')
            
            current_chunk.append(result['reason'])
            
            if len(current_chunk) >= CHUNK_SIZE:
                chunk_summary = summarize_reasons(config, current_chunk)
                if current_summary:
                    current_summary = update_summary(config, current_summary, chunk_summary)
                else:
                    current_summary = chunk_summary
                current_chunk.clear()
    
    # Process any remaining reasons in the last chunk
    if current_chunk:
        chunk_summary = summarize_reasons(config, current_chunk)
        if current_summary:
            current_summary = update_summary(config, current_summary, chunk_summary)
        else:
            current_summary = chunk_summary
    
    return all_yes, reasons, current_summary

def ask_operation(config) -> bool:
    dataset = ReadableDataSet(config.args.input_path)
    
    def processor(entry):
        return ask_yes_no_question(config, f"{config.args.raw_user_prompt}\nContext: {json.dumps(entry)}")
    
    all_yes, reasons, summary = process_entries(dataset, processor, config)
    
    if all_yes:
        print("Yes, that is the case for all entries.")
    else:
        print("No, that is not the case for some entries.")
    
    print(f"\nReasons have been saved to: {config.args.reasons_output}")
    print(f"\nSummary of reasons:\n{summary}")
    
    return all_yes

def assert_operation(config) -> bool:
    dataset = ReadableDataSet(config.args.input_path)
    
    def processor(entry):
        return ask_yes_no_question(config, f"{config.args.raw_user_prompt}\nContext: {json.dumps(entry)}")
    
    all_yes, reasons, summary = process_entries(dataset, processor, config)
    
    if all_yes:
        print("Assertion passed: The condition is true for all entries.")
    else:
        print("Assertion failed: The condition is not true for all entries.")
        print(f"\nReasons have been saved to: {config.args.reasons_output}")
        print(f"\nSummary of reasons:\n{summary}")
    
    return all_yes

def split_operation(config) -> bool:
    input_dataset = ReadableDataSet(config.args.input_path)
    output_datasets = []
    current_size = 0
    current_dataset = None
    file_count = 0
    
    for entry in input_dataset.process(lambda x: x):
        if current_size == 0 or current_size >= config.args.max_size:
            if current_dataset:
                current_dataset.__exit__(None, None, None)
                output_datasets.append(current_dataset)
            file_count += 1
            output_path = Path(config.args.output_path) / f"split_{file_count}.jsonl"
            current_dataset = WriteableDataSet(output_path)
            current_dataset.__enter__()
            current_size = 0
        
        current_dataset.write(entry)
        current_size += len(json.dumps(entry)) + 1  # +1 for newline
    
    if current_dataset:
        current_dataset.__exit__(None, None, None)
        output_datasets.append(current_dataset)
    
    print(f"Split into {len(output_datasets)} datasets")
    return True

def filter_operation(config) -> bool:
    print(f"Filtering data from {config.args.input_path} to {config.args.output_path}")
    print(f"Requirement: {config.args.raw_user_prompt}")
    
    input_path = Path(config.args.input_path)
    output_path = Path(config.args.output_path)
    
    if output_path.is_file() and input_path.is_dir():
        raise ValueError("Cannot output to a file when input is a directory")
    
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    
    filtered_count = 0
    if output_path.is_dir():
        output_file = output_path / "filtered.jsonl"
    else:
        output_file = output_path
    
    input_dataset = ReadableDataSet(input_path)
    with WriteableDataSet(output_file) as output_dataset:
        for entry in input_dataset.process(lambda x: x):
            include = ask_yes_no_question(config, f"Does the following entry meet this requirement: '{config.args.raw_user_prompt}'?\nEntry: {json.dumps(entry)}")['answer']
            if include:
                output_dataset.write(entry)
                filtered_count += 1
    
    print(f"Filtered {filtered_count} entries into {output_file}")
    return True

def merge_operation(config) -> bool:
    print(f"Merging data from {config.args.input_path} to {config.args.output_path}")
    
    output_path = Path(config.args.output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if output_path.is_dir():
        output_file = output_path / "merged.jsonl"
    else:
        output_file = output_path
    
    merged_count = 0
    seen_entries = set()
    
    with WriteableDataSet(output_file) as output_dataset:
        input_paths = [Path(p.strip()) for p in config.args.input_path.split(',')]
        for input_path in input_paths:
            input_dataset = ReadableDataSet(input_path)
            for entry in input_dataset.process(lambda x: x):
                entry_str = json.dumps(entry, sort_keys=True)
                if entry_str not in seen_entries:
                    seen_entries.add(entry_str)
                    output_dataset.write(entry)
                    merged_count += 1
    
    print(f"Merged {merged_count} unique entries into {output_file}")
    return True

def generate_operation(config) -> bool:
    print(f"Generating {config.args.num_entries} entries to {config.args.output_path}")
    print(f"Prompt: {config.args.raw_user_prompt}")
    
    output_path = Path(config.args.output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if output_path.is_dir():
        output_file = output_path / "generated.jsonl"
    else:
        output_file = output_path
    
    with WriteableDataSet(output_file) as output_dataset:
        for _ in range(config.args.num_entries):
            entry = generate_entry(config)
            output_dataset.write(entry)
    
    print(f"Generated {config.args.num_entries} entries into {output_file}")
    return True

def generate_entry(config):
    return json.loads(generate_text(config, f"Generate a JSON entry based on this prompt: {config.args.raw_user_prompt}"))

def batch_operation(config) -> bool:
    print(f"Executing batch operations from {config.args.yaml_file}")
    
    try:
        with open(config.args.yaml_file, 'r') as yaml_file:
            batch_config = yaml.safe_load(yaml_file)
    except Exception as e:
        print(f"Error reading YAML file: {e}")
        return False

    if 'steps' not in batch_config or not isinstance(batch_config['steps'], list):
        print("Invalid YAML structure: 'steps' field must be a list")
        return False

    for step in batch_config['steps']:
        if 'operation' not in step:
            print(f"Invalid step: {step}")
            return False

        operation = step['operation']
        args = argparse.Namespace(**step)
        args.func = globals().get(f"{operation}_operation")

        if not args.func:
            print(f"Unknown operation: {operation}")
            return False

        print(f"Executing {operation} operation")
        success = args.func(argparse.Namespace(**step))
        if not success:
            print(f"Operation {operation} failed")
            return False

    print("Batch operations completed successfully")
    return True

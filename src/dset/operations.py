import json
from pathlib import Path
from typing import List, Tuple
from dset.openai_api import ask_yes_no_question, generate_text
from dset.dataset import ReadableDataSet, WriteableDataSet
from dset.models import JsonLEntry

CHUNK_SIZE = 10  # Number of reasons to collect before summarizing

class AssertionFailedException(Exception):
    pass

def summarize_reasons(reasons: List[str]) -> str:
    prompt = f"Summarize the following reasons:\n\n" + "\n".join(reasons)
    return generate_text(prompt)

def update_summary(previous_summary: str, chunk_summary: str) -> str:
    prompt = f"Combine and summarize these two summaries:\n\nPrevious summary: {previous_summary}\n\nNew chunk summary: {chunk_summary}"
    return generate_text(prompt)

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
                chunk_summary = summarize_reasons(current_chunk)
                if current_summary:
                    current_summary = update_summary(current_summary, chunk_summary)
                else:
                    current_summary = chunk_summary
                current_chunk.clear()
    
    # Process any remaining reasons in the last chunk
    if current_chunk:
        chunk_summary = summarize_reasons(current_chunk)
        if current_summary:
            current_summary = update_summary(current_summary, chunk_summary)
        else:
            current_summary = chunk_summary
    
    return all_yes, reasons, current_summary

def ask_operation(config):
    dataset = ReadableDataSet(config.args.input_path)
    
    def processor(entry):
        return ask_yes_no_question(f"{config.args.raw_user_prompt}\nContext: {json.dumps(entry)}")
    
    all_yes, reasons, summary = process_entries(dataset, processor, config)
    
    if all_yes:
        print("Yes, that is the case for all entries.")
    else:
        print("No, that is not the case for some entries.")
    
    print(f"\nReasons have been saved to: {config.args.reasons_output}")
    print(f"\nSummary of reasons:\n{summary}")
    
    return all_yes, config.args.reasons_output, summary

def assert_operation(config):
    dataset = ReadableDataSet(config.args.input_path)
    
    def processor(entry):
        return ask_yes_no_question(f"{config.args.raw_user_prompt}\nContext: {json.dumps(entry)}")
    
    all_yes, reasons, summary = process_entries(dataset, processor, config)
    
    if all_yes:
        print("Assertion passed: The condition is true for all entries.")
    else:
        print("Assertion failed: The condition is not true for all entries.")
        print(f"\nReasons have been saved to: {config.args.reasons_output}")
        print(f"\nSummary of reasons:\n{summary}")
        raise AssertionFailedException("Assertion failed for some entries")
    
    return all_yes, config.args.reasons_output, summary

def split_operation(config):
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
    return output_datasets

def filter_operation(config):
    print(f"Filtering data from {config.args.input_path} to {config.args.output_path}")
    print(f"Requirement: {config.args.raw_user_prompt}")
    
    input_path = Path(config.args.input_path)
    output_path = Path(config.args.output_path)
    
    if output_path.is_file() and input_path.is_dir():
        raise ValueError("Cannot output to a file when input is a directory")
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    filtered_count = 0
    if output_path.is_dir():
        output_file = output_path / "filtered.jsonl"
    else:
        output_file = output_path
    
    input_dataset = ReadableDataSet(input_path)
    with WriteableDataSet(output_file) as output_dataset:
        for entry in input_dataset.process(lambda x: x):
            include = ask_yes_no_question(f"Does the following entry meet this requirement: '{config.args.raw_user_prompt}'?\nEntry: {json.dumps(entry)}")['answer']
            if include:
                output_dataset.write(entry)
                filtered_count += 1
    
    print(f"Filtered {filtered_count} entries into {output_file}")

def merge_operation(config):
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

def generate_operation(config):
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
            entry = generate_entry(config.args.raw_user_prompt)
            output_dataset.write(entry)
    
    print(f"Generated {config.args.num_entries} entries into {output_file}")

def generate_entry(prompt):
    return json.loads(generate_text(f"Generate a JSON entry based on this prompt: {prompt}"))

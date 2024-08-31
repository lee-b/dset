import json
import os
import sys
from typing import List, Tuple
from dset.openai_api import ask_yes_no_question, generate_text
from dset.dataset import DataSet
from dset.models import JsonLEntry

CHUNK_SIZE = 10  # Number of reasons to collect before summarizing

def summarize_reasons(reasons: List[str]) -> str:
    prompt = f"Summarize the following reasons:\n\n" + "\n".join(reasons)
    return generate_text(prompt)

def update_summary(previous_summary: str, chunk_summary: str) -> str:
    prompt = f"Combine and summarize these two summaries:\n\nPrevious summary: {previous_summary}\n\nNew chunk summary: {chunk_summary}"
    return generate_text(prompt)

def process_entries(dataset: DataSet, processor, config) -> Tuple[bool, List[str], str]:
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
    dataset = DataSet(config.args.input)
    
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
    dataset = DataSet(config.args.input)
    
    def processor(entry):
        return ask_yes_no_question(f"{config.args.raw_user_prompt}\nContext: {json.dumps(entry)}")
    
    all_yes, reasons, summary = process_entries(dataset, processor, config)
    
    if all_yes:
        print("Assertion passed: The condition is true for all entries.")
    else:
        print("Assertion failed: The condition is not true for all entries.")
        print(f"\nReasons have been saved to: {config.args.reasons_output}")
        print(f"\nSummary of reasons:\n{summary}")
        sys.exit(1)
    
    return all_yes, config.args.reasons_output, summary

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

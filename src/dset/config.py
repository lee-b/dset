import argparse
import sys
import os
from dataclasses import dataclass
from typing import Tuple, Optional
from dset.operations import filter_operation, merge_operation, split_operation, ask_operation, assert_operation, generate_operation, batch_operation

@dataclass
class Config:
    args: argparse.Namespace
    smart_model: str
    fast_model: str

def build_config() -> Tuple[bool, Optional[Config]]:
    parser = argparse.ArgumentParser(description="DSET: Dataset Processing Operations")
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')

    subparsers = parser.add_subparsers(dest='operation', help='Operation to perform on the dataset', required=True)

    # Filter subcommand
    filter_parser = subparsers.add_parser('filter', help='Filter the dataset and create a new dataset')
    filter_parser.add_argument('input', help='Input dataset file or directory')
    filter_parser.add_argument('output', help='Output dataset file or directory')
    filter_parser.add_argument('raw_user_prompt', help='Raw user prompt for filtering entries')
    filter_parser.set_defaults(func=filter_operation)

    # Merge subcommand
    merge_parser = subparsers.add_parser('merge', help='Merge datasets into a new dataset')
    merge_parser.add_argument('input', help='Input dataset files or directories (comma-separated)')
    merge_parser.add_argument('output', help='Output dataset file or directory')
    merge_parser.set_defaults(func=merge_operation)

    # Split subcommand
    split_parser = subparsers.add_parser('split', help='Split a dataset into multiple new datasets based on maximum size')
    split_parser.add_argument('input', help='Input dataset file or directory')
    split_parser.add_argument('output', help='Output dataset files or directory prefix')
    split_parser.add_argument('max_size', type=int, help='Maximum size of each split file in bytes')
    split_parser.set_defaults(func=split_operation)

    # Ask subcommand
    ask_parser = subparsers.add_parser('ask', help='Ask a question about the dataset')
    ask_parser.add_argument('input', help='Input dataset file or directory')
    ask_parser.add_argument('raw_user_prompt', metavar='user_prompt', help='Question to ask about the dataset')
    ask_parser.set_defaults(func=ask_operation)

    # Assert subcommand
    assert_parser = subparsers.add_parser('assert', help='Assert a condition about the dataset')
    assert_parser.add_argument('input', help='Input dataset file or directory')
    assert_parser.add_argument('raw_user_prompt', metavar='user_prompt', help='Condition to assert about the dataset')
    assert_parser.set_defaults(func=assert_operation)

    # Generate subcommand
    gen_parser = subparsers.add_parser('gen', help='Generate a dataset of jsonl entries')
    gen_parser.add_argument('output', help='Output dataset file')
    gen_parser.add_argument('raw_user_prompt', metavar='user_prompt', help='Prompt for generating entries')
    gen_parser.add_argument('num_entries', type=int, help='Number of entries to generate')
    gen_parser.set_defaults(func=generate_operation)

    # Batch subcommand
    batch_parser = subparsers.add_parser('batch', help='Execute a batch of operations from a YAML file')
    batch_parser.add_argument('yaml_file', help='YAML file containing batch operations')
    batch_parser.set_defaults(func=batch_operation)

    # Check if no arguments were provided
    if len(sys.argv) == 1:
        parser.print_help()
        return False, None

    try:
        args = parser.parse_args()
        smart_model = os.environ.get("OPENAI_SMART_MODEL", "gpt-4")
        fast_model = os.environ.get("OPENAI_FAST_MODEL", "gpt-3.5-turbo")
        return True, Config(args=args, smart_model=smart_model, fast_model=fast_model)
    except SystemExit:
        # This catches the SystemExit raised by argparse when --help or --version is used
        return False, None

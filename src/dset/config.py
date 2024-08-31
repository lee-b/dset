import argparse
import sys
from dataclasses import dataclass
from typing import Callable

@dataclass
class Config:
    input: str
    output: str
    operation: Callable
    question: str = None
    max_size: int = None

def filter_handler(args):
    print(f"Filtering data from {args.input} to {args.output}")

def merge_handler(args):
    print(f"Merging data from {args.input} to {args.output}")

def split_handler(args):
    from dset.operations import split_operation
    split_operation(args.input, args.output, args.max_size)

def ask_handler(args):
    from dset.operations import ask_operation
    ask_operation(args.input, args.question)

def assert_handler(args):
    from dset.operations import assert_operation
    assert_operation(args.input, args.question)

def build_config() -> Config:
    parser = argparse.ArgumentParser(description="DSET: Dataset Processing Operations")
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')

    subparsers = parser.add_subparsers(dest='operation', required=True, help='Operation to perform on the dataset')

    # Filter subcommand
    filter_parser = subparsers.add_parser('filter', help='Filter the dataset and create a new dataset')
    filter_parser.add_argument('--input', required=True, help='Input dataset file')
    filter_parser.add_argument('--output', required=True, help='Output dataset file')
    filter_parser.set_defaults(func=filter_handler)

    # Merge subcommand
    merge_parser = subparsers.add_parser('merge', help='Merge datasets into a new dataset')
    merge_parser.add_argument('--input', required=True, help='Input dataset files (comma-separated)')
    merge_parser.add_argument('--output', required=True, help='Output dataset file')
    merge_parser.set_defaults(func=merge_handler)

    # Split subcommand
    split_parser = subparsers.add_parser('split', help='Split a dataset into multiple new datasets based on maximum size')
    split_parser.add_argument('--input', required=True, help='Input dataset file')
    split_parser.add_argument('--output', required=True, help='Output dataset files prefix')
    split_parser.add_argument('--max-size', type=int, required=True, help='Maximum size of each split file in bytes')
    split_parser.set_defaults(func=split_handler)

    # Ask subcommand
    ask_parser = subparsers.add_parser('ask', help='Ask a yes/no question about the dataset')
    ask_parser.add_argument('--input', required=True, help='Input dataset file')
    ask_parser.add_argument('--question', required=True, help='Question to ask about the dataset')
    ask_parser.set_defaults(func=ask_handler)

    # Assert subcommand
    assert_parser = subparsers.add_parser('assert', help='Assert a condition about the dataset')
    assert_parser.add_argument('--input', required=True, help='Input dataset file')
    assert_parser.add_argument('--question', required=True, help='Condition to assert about the dataset')
    assert_parser.set_defaults(func=assert_handler)

    args = parser.parse_args()

    return Config(
        input=args.input,
        output=args.output,
        operation=args.func,
        question=getattr(args, 'question', None),
        max_size=getattr(args, 'max_size', None)
    )

import argparse
from dataclasses import dataclass
from typing import Callable

@dataclass
class Config:
    args: argparse.Namespace
    operation: Callable

def filter_handler(config):
    from dset.operations import filter_operation
    filter_operation(config.args.input, config.args.output, config.args.raw_user_prompt)

def merge_handler(config):
    from dset.operations import merge_operation
    merge_operation(config.args.input, config.args.output)

def split_handler(config):
    from dset.operations import split_operation
    split_operation(config.args.input, config.args.output, config.args.max_size)

def ask_handler(config):
    from dset.operations import ask_operation
    ask_operation(config.args.input, config.args.raw_user_prompt)

def assert_handler(config):
    from dset.operations import assert_operation
    assert_operation(config.args.input, config.args.raw_user_prompt)

def build_config() -> Config:
    parser = argparse.ArgumentParser(description="DSET: Dataset Processing Operations")
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')

    subparsers = parser.add_subparsers(dest='operation', required=True, help='Operation to perform on the dataset')

    # Filter subcommand
    filter_parser = subparsers.add_parser('filter', help='Filter the dataset and create a new dataset')
    filter_parser.add_argument('--input', required=True, help='Input dataset file or directory')
    filter_parser.add_argument('--output', required=True, help='Output dataset file or directory')
    filter_parser.add_argument('--raw-user-prompt', required=True, help='Raw user prompt for filtering entries')
    filter_parser.set_defaults(func=filter_handler)

    # Merge subcommand
    merge_parser = subparsers.add_parser('merge', help='Merge datasets into a new dataset')
    merge_parser.add_argument('--input', required=True, help='Input dataset files or directories (comma-separated)')
    merge_parser.add_argument('--output', required=True, help='Output dataset file or directory')
    merge_parser.set_defaults(func=merge_handler)

    # Split subcommand
    split_parser = subparsers.add_parser('split', help='Split a dataset into multiple new datasets based on maximum size')
    split_parser.add_argument('--input', required=True, help='Input dataset file or directory')
    split_parser.add_argument('--output', required=True, help='Output dataset files or directory prefix')
    split_parser.add_argument('--max-size', type=int, required=True, help='Maximum size of each split file in bytes')
    split_parser.set_defaults(func=split_handler)

    # Ask subcommand
    ask_parser = subparsers.add_parser('ask', help='Ask a question about the dataset')
    ask_parser.add_argument('--input', required=True, help='Input dataset file or directory')
    ask_parser.add_argument('--raw-user-prompt', required=True, help='Question to ask about the dataset')
    ask_parser.set_defaults(func=ask_handler)

    # Assert subcommand
    assert_parser = subparsers.add_parser('assert', help='Assert a condition about the dataset')
    assert_parser.add_argument('--input', required=True, help='Input dataset file or directory')
    assert_parser.add_argument('--raw-user-prompt', required=True, help='Condition to assert about the dataset')
    assert_parser.set_defaults(func=assert_handler)

    args = parser.parse_args()

    return Config(
        args=args,
        operation=args.func
    )

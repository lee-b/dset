import argparse
import sys
from dataclasses import dataclass
from typing import Tuple, Optional
from dset.operations import filter_operation, merge_operation, split_operation, ask_operation, assert_operation

@dataclass
class Config:
    args: argparse.Namespace

def build_config() -> Tuple[bool, Optional[Config]]:
    parser = argparse.ArgumentParser(description="DSET: Dataset Processing Operations")
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')

    subparsers = parser.add_subparsers(dest='operation', help='Operation to perform on the dataset')

    # Filter subcommand
    filter_parser = subparsers.add_parser('filter', help='Filter the dataset and create a new dataset')
    filter_parser.add_argument('--input', required=True, help='Input dataset file or directory')
    filter_parser.add_argument('--output', required=True, help='Output dataset file or directory')
    filter_parser.add_argument('--raw-user-prompt', required=True, help='Raw user prompt for filtering entries')
    filter_parser.set_defaults(func=filter_operation)

    # Merge subcommand
    merge_parser = subparsers.add_parser('merge', help='Merge datasets into a new dataset')
    merge_parser.add_argument('--input', required=True, help='Input dataset files or directories (comma-separated)')
    merge_parser.add_argument('--output', required=True, help='Output dataset file or directory')
    merge_parser.set_defaults(func=merge_operation)

    # Split subcommand
    split_parser = subparsers.add_parser('split', help='Split a dataset into multiple new datasets based on maximum size')
    split_parser.add_argument('--input', required=True, help='Input dataset file or directory')
    split_parser.add_argument('--output', required=True, help='Output dataset files or directory prefix')
    split_parser.add_argument('--max-size', type=int, required=True, help='Maximum size of each split file in bytes')
    split_parser.set_defaults(func=split_operation)

    # Ask subcommand
    ask_parser = subparsers.add_parser('ask', help='Ask a question about the dataset')
    ask_parser.add_argument('--input', required=True, help='Input dataset file or directory')
    ask_parser.add_argument('--raw-user-prompt', required=True, help='Question to ask about the dataset')
    ask_parser.set_defaults(func=ask_operation)

    # Assert subcommand
    assert_parser = subparsers.add_parser('assert', help='Assert a condition about the dataset')
    assert_parser.add_argument('--input', required=True, help='Input dataset file or directory')
    assert_parser.add_argument('--raw-user-prompt', required=True, help='Condition to assert about the dataset')
    assert_parser.set_defaults(func=assert_operation)

    if len(sys.argv) == 1:
        parser.print_help()
        return False, None

    # Note: We're not catching SystemExit here. This allows argparse to handle --help and --version
    # flags naturally, exiting the program after displaying the appropriate information.
    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.print_help()
        return False, None

    return True, Config(args=args)

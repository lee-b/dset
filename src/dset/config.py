import argparse
import sys
from dataclasses import dataclass
from typing import Callable

@dataclass
class Config:
    input: str
    output: str
    operation: Callable

def filter_handler(args):
    print(f"Filtering data from {args.input} to {args.output}")

def sort_handler(args):
    print(f"Sorting data from {args.input} to {args.output}")

def merge_handler(args):
    print(f"Merging data from {args.input} to {args.output}")

def build_config() -> Config:
    parser = argparse.ArgumentParser(description="DSET: Dataset Processing Operations")
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')

    subparsers = parser.add_subparsers(dest='operation', required=True, help='Operation to perform on the dataset')

    # Filter subcommand
    filter_parser = subparsers.add_parser('filter', help='Filter the dataset')
    filter_parser.add_argument('--input', required=True, help='Input dataset file')
    filter_parser.add_argument('--output', required=True, help='Output dataset file')
    filter_parser.set_defaults(func=filter_handler)

    # Sort subcommand
    sort_parser = subparsers.add_parser('sort', help='Sort the dataset')
    sort_parser.add_argument('--input', required=True, help='Input dataset file')
    sort_parser.add_argument('--output', required=True, help='Output dataset file')
    sort_parser.set_defaults(func=sort_handler)

    # Merge subcommand
    merge_parser = subparsers.add_parser('merge', help='Merge datasets')
    merge_parser.add_argument('--input', required=True, help='Input dataset files (comma-separated)')
    merge_parser.add_argument('--output', required=True, help='Output dataset file')
    merge_parser.set_defaults(func=merge_handler)

    args = parser.parse_args()

    return Config(
        input=args.input,
        output=args.output,
        operation=args.func
    )

if __name__ == "__main__":
    config = build_config()
    config.operation(config)

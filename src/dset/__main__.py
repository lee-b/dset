from dset.config import build_config
from dset.operations import filter_operation, merge_operation, split_operation, ask_operation, assert_operation

def main():
    config = build_config()
    
    operations = {
        'filter': filter_operation,
        'merge': merge_operation,
        'split': split_operation,
        'ask': ask_operation,
        'assert': assert_operation
    }
    
    operation = operations.get(config.args.operation)
    if operation:
        operation(config)
    else:
        print(f"Unknown operation: {config.args.operation}")

if __name__ == "__main__":
    main()

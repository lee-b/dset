import os
import tempfile
import yaml
from unittest.mock import patch
from dset.operations import batch_operation
from dset.config import Config
import argparse

def test_batch_operation():
    # Create a temporary YAML file with batch operations
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
        yaml_content = """
        steps:
          - operation: generate
            output: generated_data.jsonl
            raw_user_prompt: "Generate a simple profile with name, age (over 30), and favorite color"
            num_entries: 5
          - operation: filter
            input: generated_data.jsonl
            output: verified_data.jsonl
            raw_user_prompt: "Verify that all fields (name, age, favorite color) are populated, the entry looks correct according to the prompt, and the age is over 30"
        """
        temp_file.write(yaml_content)
        temp_file_path = temp_file.name

    try:
        # Create a mock Config object
        args = argparse.Namespace(yaml_file=temp_file_path)
        config = Config(args=args)

        # Mock the generate_operation and filter_operation functions
        with patch('dset.operations.generate_operation', return_value=True) as mock_generate, \
             patch('dset.operations.filter_operation', return_value=True) as mock_filter:

            # Run the batch operation
            result = batch_operation(config)

            # Assert that the batch operation was successful
            assert result == True

            # Assert that both operations were called
            mock_generate.assert_called_once()
            mock_filter.assert_called_once()

            # Check the arguments passed to generate_operation
            generate_args = mock_generate.call_args[0][0]
            assert generate_args.output == "generated_data.jsonl"
            assert generate_args.raw_user_prompt == "Generate a simple profile with name, age (over 30), and favorite color"
            assert generate_args.num_entries == 5

            # Check the arguments passed to filter_operation
            filter_args = mock_filter.call_args[0][0]
            assert filter_args.input_path == "generated_data.jsonl"
            assert filter_args.output_path == "verified_data.jsonl"
            assert filter_args.raw_user_prompt == "Verify that all fields (name, age, favorite color) are populated, the entry looks correct according to the prompt, and the age is over 30"

    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)

if __name__ == "__main__":
    test_batch_operation()
    print("All tests passed!")

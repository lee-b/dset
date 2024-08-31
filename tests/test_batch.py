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
            raw_user_prompt: "Generate a person's name and age"
            num_entries: 5
          - operation: filter
            input: generated_data.jsonl
            output: filtered_data.jsonl
            raw_user_prompt: "Is the person's age over 30?"
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

    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)

if __name__ == "__main__":
    test_batch_operation()
    print("All tests passed!")

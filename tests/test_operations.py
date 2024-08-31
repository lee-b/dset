import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from argparse import Namespace
from dset.config import Config
from dset.operations import filter_operation, merge_operation, split_operation, ask_operation, generate_operation

def create_test_data(data, is_dir=False):
    if is_dir:
        temp_dir = tempfile.mkdtemp()
        file_path = Path(temp_dir) / "test_data.jsonl"
    else:
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl')
        file_path = temp_file.name

    with open(file_path, 'w') as f:
        for item in data:
            json.dump(item, f)
            f.write('\n')

    return str(file_path)

def mock_ask_yes_no_question(question):
    return {"answer": True, "reason": "Mock reason"}

def mock_generate_text(prompt):
    return json.dumps({"name": "John Doe", "age": 30})

@patch('dset.openai_api.ask_yes_no_question', side_effect=mock_ask_yes_no_question)
@patch('dset.openai_api.generate_text', side_effect=mock_generate_text)
def test_filter_operation(mock_generate_text, mock_ask_yes_no_question):
    test_data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35}
    ]
    input_file = create_test_data(test_data)
    output_dir = tempfile.mkdtemp()

    args = Namespace(input_path=Path(input_file), output_path=Path(output_dir), raw_user_prompt="age greater than 28")
    config = Config(args=args, smart_model="gpt-4", fast_model="gpt-3.5-turbo")
    
    assert filter_operation(config)

def test_merge_operation():
    test_data1 = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    test_data2 = [{"id": 2, "name": "Bob"}, {"id": 3, "name": "Charlie"}]

    input_file1 = create_test_data(test_data1)
    input_file2 = create_test_data(test_data2)
    output_dir = tempfile.mkdtemp()

    args = Namespace(input_path=f"{input_file1},{input_file2}", output_path=Path(output_dir))
    config = Config(args=args, smart_model="gpt-4", fast_model="gpt-3.5-turbo")
    
    assert merge_operation(config)

def test_split_operation():
    test_data = [{"id": i} for i in range(100)]
    input_file = create_test_data(test_data)
    output_dir = tempfile.mkdtemp()

    args = Namespace(input_path=Path(input_file), output_path=Path(output_dir), max_size=1000)
    config = Config(args=args, smart_model="gpt-4", fast_model="gpt-3.5-turbo")
    
    assert split_operation(config)

@patch('dset.openai_api.ask_yes_no_question', side_effect=mock_ask_yes_no_question)
def test_ask_operation(mock_ask_yes_no_question, capsys):
    test_data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35}
    ]
    input_file = create_test_data(test_data)

    args = Namespace(input_path=Path(input_file), raw_user_prompt="Are all people older than 20?", reasons_output=Path(tempfile.mktemp()))
    config = Config(args=args, smart_model="gpt-4", fast_model="gpt-3.5-turbo")
    
    assert ask_operation(config)

@patch('dset.openai_api.generate_text', side_effect=mock_generate_text)
def test_generate_operation(mock_generate_text):
    output_dir = tempfile.mkdtemp()

    args = Namespace(output_path=Path(output_dir), raw_user_prompt="Generate a person with name and age", num_entries=5)
    config = Config(args=args, smart_model="gpt-4", fast_model="gpt-3.5-turbo")
    
    assert generate_operation(config)

def test_merge_operation_with_empty_file():
    test_data1 = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    test_data2 = []

    input_file1 = create_test_data(test_data1)
    input_file2 = create_test_data(test_data2)
    output_dir = tempfile.mkdtemp()

    args = Namespace(input_path=f"{input_file1},{input_file2}", output_path=Path(output_dir))
    config = Config(args=args, smart_model="gpt-4", fast_model="gpt-3.5-turbo")
    
    assert merge_operation(config)

def test_split_operation_with_small_file():
    test_data = [{"id": i} for i in range(5)]
    input_file = create_test_data(test_data)
    output_dir = tempfile.mkdtemp()

    args = Namespace(input_path=Path(input_file), output_path=Path(output_dir), max_size=1000)
    config = Config(args=args, smart_model="gpt-4", fast_model="gpt-3.5-turbo")
    
    assert split_operation(config)

def test_filter_operation_error_with_file_output_for_directory_input():
    test_data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    input_dir = create_test_data(test_data, is_dir=True)
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jsonl').name

    args = Namespace(input_path=Path(input_dir), output_path=Path(output_file), raw_user_prompt="age greater than 28")
    config = Config(args=args, smart_model="gpt-4", fast_model="gpt-3.5-turbo")
    
    try:
        filter_operation(config)
    except ValueError as e:
        assert str(e) == "Cannot output to a file when input is a directory"
    else:
        assert False, "Expected ValueError was not raised"

if __name__ == "__main__":
    test_filter_operation()
    test_merge_operation()
    test_split_operation()
    test_ask_operation()
    test_generate_operation()
    test_merge_operation_with_empty_file()
    test_split_operation_with_small_file()
    test_filter_operation_error_with_file_output_for_directory_input()
    print("All tests passed!")

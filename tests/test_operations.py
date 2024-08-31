import json
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from dset.config import Config
from dset.operations import filter_operation, merge_operation, split_operation, ask_operation, assert_operation, generate_operation
from argparse import Namespace

def create_test_data(data, is_dir=False):
    if is_dir:
        temp_dir = tempfile.mkdtemp()
        temp_file = Path(temp_dir) / "test_data.jsonl"
    else:
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl').name
    
    with open(temp_file, 'w') as f:
        for entry in data:
            json.dump(entry, f)
            f.write('\n')
    return temp_file if not is_dir else temp_dir

# Mock responses for openai_api functions
def mock_ask_yes_no_question(question, model="gpt-3.5-turbo"):
    return {
        "answer": True,
        "reason": "This is a mock response for testing purposes."
    }

def mock_generate_text(prompt, model="gpt-3.5-turbo"):
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
    config = Config(args)

    filter_operation(config)

    output_file = Path(output_dir) / "filtered.jsonl"
    assert output_file.exists()

    with open(output_file, 'r') as f:
        filtered_data = [json.loads(line) for line in f]

    assert len(filtered_data) == 3  # All entries pass due to mocked response
    
    os.unlink(input_file)
    os.unlink(output_file)
    os.rmdir(output_dir)

def test_merge_operation():
    test_data1 = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    test_data2 = [{"id": 2, "name": "Bob"}, {"id": 3, "name": "Charlie"}]
    
    input_file1 = create_test_data(test_data1)
    input_file2 = create_test_data(test_data2)
    output_dir = tempfile.mkdtemp()

    args = Namespace(input_path=f"{input_file1},{input_file2}", output_path=Path(output_dir))
    config = Config(args)

    merge_operation(config)

    output_file = Path(output_dir) / "merged.jsonl"
    assert output_file.exists()

    with open(output_file, 'r') as f:
        merged_data = [json.loads(line) for line in f]

    assert len(merged_data) == 3
    assert set(entry['name'] for entry in merged_data) == {"Alice", "Bob", "Charlie"}

    os.unlink(input_file1)
    os.unlink(input_file2)
    os.unlink(output_file)
    os.rmdir(output_dir)

@patch('dset.dataset.DataSet.split')
def test_split_operation(mock_split):
    test_data = [{"id": i} for i in range(100)]
    input_file = create_test_data(test_data)
    output_dir = tempfile.mkdtemp()

    args = Namespace(input_path=Path(input_file), output_path=Path(output_dir), max_size=1000)
    config = Config(args)

    split_operation(config)

    mock_split.assert_called_once_with(Path(output_dir), 1000)

    os.unlink(input_file)
    os.rmdir(output_dir)

@patch('dset.openai_api.ask_yes_no_question', side_effect=mock_ask_yes_no_question)
def test_ask_operation(mock_ask_yes_no_question, capsys):
    test_data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35}
    ]
    input_file = create_test_data(test_data)

    args = Namespace(input_path=Path(input_file), raw_user_prompt="Are all people older than 20?", reasons_output=Path(tempfile.mktemp()))
    config = Config(args)

    ask_operation(config)

    captured = capsys.readouterr()
    assert "Yes, that is the case for all entries." in captured.out

    os.unlink(input_file)
    os.unlink(args.reasons_output)

@patch('dset.openai_api.ask_yes_no_question', side_effect=lambda q, m: {"answer": False, "reason": "Mock negative response"})
def test_assert_operation_failure(mock_ask_yes_no_question):
    test_data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35}
    ]
    input_file = create_test_data(test_data)

    args = Namespace(input_path=Path(input_file), raw_user_prompt="All ages are greater than 40", reasons_output=Path(tempfile.mktemp()))
    config = Config(args)

    with pytest.raises(SystemExit) as excinfo:
        assert_operation(config)
    
    assert excinfo.value.code == 1  # Assert operation should fail

    os.unlink(input_file)
    os.unlink(args.reasons_output)

@patch('dset.openai_api.generate_text', side_effect=mock_generate_text)
def test_generate_operation(mock_generate_text):
    output_dir = tempfile.mkdtemp()

    args = Namespace(output_path=Path(output_dir), raw_user_prompt="Generate a person with name and age", num_entries=5)
    config = Config(args)

    generate_operation(config)

    output_file = Path(output_dir) / "generated.jsonl"
    assert output_file.exists()

    with open(output_file, 'r') as f:
        generated_data = [json.loads(line) for line in f]

    assert len(generated_data) == 5
    assert all('name' in entry and 'age' in entry for entry in generated_data)

    os.unlink(output_file)
    os.rmdir(output_dir)

def test_merge_operation_with_empty_file():
    test_data1 = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    test_data2 = []
    
    input_file1 = create_test_data(test_data1)
    input_file2 = create_test_data(test_data2)
    output_dir = tempfile.mkdtemp()

    args = Namespace(input_path=f"{input_file1},{input_file2}", output_path=Path(output_dir))
    config = Config(args)

    merge_operation(config)

    output_file = Path(output_dir) / "merged.jsonl"
    assert output_file.exists()

    with open(output_file, 'r') as f:
        merged_data = [json.loads(line) for line in f]

    assert len(merged_data) == 2
    assert set(entry['name'] for entry in merged_data) == {"Alice", "Bob"}

    os.unlink(input_file1)
    os.unlink(input_file2)
    os.unlink(output_file)
    os.rmdir(output_dir)

@patch('dset.dataset.DataSet.split')
def test_split_operation_with_small_file(mock_split):
    test_data = [{"id": i} for i in range(5)]
    input_file = create_test_data(test_data)
    output_dir = tempfile.mkdtemp()

    args = Namespace(input_path=Path(input_file), output_path=Path(output_dir), max_size=1000)
    config = Config(args)

    split_operation(config)

    mock_split.assert_called_once_with(Path(output_dir), 1000)

    os.unlink(input_file)
    os.rmdir(output_dir)

@patch('dset.openai_api.ask_yes_no_question', side_effect=mock_ask_yes_no_question)
def test_filter_operation_with_directory_input(mock_ask_yes_no_question):
    test_data1 = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    test_data2 = [{"name": "Charlie", "age": 35}, {"name": "David", "age": 40}]
    
    input_dir = tempfile.mkdtemp()
    create_test_data(test_data1, is_dir=True)
    create_test_data(test_data2, is_dir=True)
    
    output_dir = tempfile.mkdtemp()

    args = Namespace(input_path=Path(input_dir), output_path=Path(output_dir), raw_user_prompt="age greater than 28")
    config = Config(args)

    filter_operation(config)

    output_file = Path(output_dir) / "filtered.jsonl"
    assert output_file.exists()

    with open(output_file, 'r') as f:
        filtered_data = [json.loads(line) for line in f]

    assert len(filtered_data) == 4  # All entries pass due to mocked response

    for file in Path(input_dir).glob("*.jsonl"):
        os.unlink(file)
    os.rmdir(input_dir)
    os.unlink(output_file)
    os.rmdir(output_dir)

def test_filter_operation_error_with_file_output_for_directory_input():
    test_data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    input_dir = create_test_data(test_data, is_dir=True)
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jsonl').name

    args = Namespace(input_path=Path(input_dir), output_path=Path(output_file), raw_user_prompt="age greater than 28")
    config = Config(args)

    with pytest.raises(ValueError, match="Cannot output to a file when input is a directory"):
        filter_operation(config)

    for file in Path(input_dir).glob("*.jsonl"):
        os.unlink(file)
    os.rmdir(input_dir)
    os.unlink(output_file)

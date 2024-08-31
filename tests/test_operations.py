import json
import os
import tempfile
from unittest.mock import patch
from dset.config import Config
from dset.operations import filter_operation, merge_operation, split_operation, ask_operation, assert_operation, generate_operation
from argparse import Namespace

def create_test_data(data):
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as temp:
        for entry in data:
            json.dump(entry, temp)
            temp.write('\n')
    return temp.name

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
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jsonl').name

    args = Namespace(input=input_file, output=output_file, raw_user_prompt="age greater than 28")
    config = Config(args)

    filter_operation(config)

    with open(output_file, 'r') as f:
        filtered_data = [json.loads(line) for line in f]

    assert len(filtered_data) == 3  # All entries pass due to mocked response
    
    os.unlink(input_file)
    os.unlink(output_file)

def test_merge_operation():
    test_data1 = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    test_data2 = [{"id": 2, "name": "Bob"}, {"id": 3, "name": "Charlie"}]
    
    input_file1 = create_test_data(test_data1)
    input_file2 = create_test_data(test_data2)
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jsonl').name

    args = Namespace(input=f"{input_file1},{input_file2}", output=output_file)
    config = Config(args)

    merge_operation(config)

    with open(output_file, 'r') as f:
        merged_data = [json.loads(line) for line in f]

    assert len(merged_data) == 3
    assert set(entry['name'] for entry in merged_data) == {"Alice", "Bob", "Charlie"}

    os.unlink(input_file1)
    os.unlink(input_file2)
    os.unlink(output_file)

def test_split_operation():
    test_data = [{"id": i} for i in range(100)]
    input_file = create_test_data(test_data)
    output_prefix = tempfile.mkdtemp()

    args = Namespace(input=input_file, output=f"{output_prefix}/split", max_size=1000)
    config = Config(args)

    split_operation(config)

    split_files = [f for f in os.listdir(output_prefix) if f.startswith("split")]
    assert len(split_files) > 1

    total_entries = 0
    for split_file in split_files:
        with open(os.path.join(output_prefix, split_file), 'r') as f:
            total_entries += sum(1 for _ in f)

    assert total_entries == 100

    os.unlink(input_file)
    for split_file in split_files:
        os.unlink(os.path.join(output_prefix, split_file))
    os.rmdir(output_prefix)

@patch('dset.openai_api.ask_yes_no_question', side_effect=mock_ask_yes_no_question)
def test_ask_operation(mock_ask_yes_no_question, capsys):
    test_data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35}
    ]
    input_file = create_test_data(test_data)

    args = Namespace(input=input_file, raw_user_prompt="Are all people older than 20?")
    config = Config(args)

    ask_operation(config)

    captured = capsys.readouterr()
    assert "Yes, that is the case for all entries." in captured.out

    os.unlink(input_file)

@patch('dset.openai_api.ask_yes_no_question', side_effect=mock_ask_yes_no_question)
def test_assert_operation(mock_ask_yes_no_question):
    test_data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35}
    ]
    input_file = create_test_data(test_data)

    args = Namespace(input=input_file, raw_user_prompt="All ages are greater than 20")
    config = Config(args)

    try:
        assert_operation(config)
    except SystemExit as e:
        assert e.code == 0  # Assert operation should pass

    os.unlink(input_file)

@patch('dset.openai_api.generate_text', side_effect=mock_generate_text)
def test_generate_operation(mock_generate_text):
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jsonl').name

    args = Namespace(output=output_file, raw_user_prompt="Generate a person with name and age", num_entries=5)
    config = Config(args)

    generate_operation(config)

    with open(output_file, 'r') as f:
        generated_data = [json.loads(line) for line in f]

    assert len(generated_data) == 5
    assert all('name' in entry and 'age' in entry for entry in generated_data)

    os.unlink(output_file)

# New test cases

def test_merge_operation_with_empty_file():
    test_data1 = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    test_data2 = []
    
    input_file1 = create_test_data(test_data1)
    input_file2 = create_test_data(test_data2)
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jsonl').name

    args = Namespace(input=f"{input_file1},{input_file2}", output=output_file)
    config = Config(args)

    merge_operation(config)

    with open(output_file, 'r') as f:
        merged_data = [json.loads(line) for line in f]

    assert len(merged_data) == 2
    assert set(entry['name'] for entry in merged_data) == {"Alice", "Bob"}

    os.unlink(input_file1)
    os.unlink(input_file2)
    os.unlink(output_file)

def test_split_operation_with_small_file():
    test_data = [{"id": i} for i in range(5)]
    input_file = create_test_data(test_data)
    output_prefix = tempfile.mkdtemp()

    args = Namespace(input=input_file, output=f"{output_prefix}/split", max_size=1000)
    config = Config(args)

    split_operation(config)

    split_files = [f for f in os.listdir(output_prefix) if f.startswith("split")]
    assert len(split_files) == 1

    with open(os.path.join(output_prefix, split_files[0]), 'r') as f:
        split_data = [json.loads(line) for line in f]

    assert len(split_data) == 5

    os.unlink(input_file)
    os.unlink(os.path.join(output_prefix, split_files[0]))
    os.rmdir(output_prefix)

@patch('dset.openai_api.ask_yes_no_question', side_effect=lambda q, m: {"answer": False, "reason": "Mock negative response"})
def test_assert_operation_failure(mock_ask_yes_no_question):
    test_data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35}
    ]
    input_file = create_test_data(test_data)

    args = Namespace(input=input_file, raw_user_prompt="All ages are greater than 40")
    config = Config(args)

    with pytest.raises(SystemExit) as excinfo:
        assert_operation(config)
    
    assert excinfo.value.code == 1  # Assert operation should fail

    os.unlink(input_file)

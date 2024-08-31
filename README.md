# 🚀 DSET: Dataset Processing Operations

Hey there, data wranglers! 👋 Welcome to DSET, your new best friend for AI-powered dataset processing. Whether you're a lone wolf or running with a pack, DSET's got your back for all your dataset needs.

## 🎭 What's the Deal?

DSET is like your Swiss Army knife for datasets. It's an AI-based tool that lets you:

- Generate synthetic datasets 🧪
- Process existing datasets 🔄
- Filter datasets based on custom criteria 🕵️
- Run sanity checks on your data 🧠
- Ask questions about your dataset 🤔
- Apply a whole pipeline of operations in one go 🏗️

## 🛠️ Features

### Manual Operations

Got a specific task in mind? We've got you covered with these individual commands:

- `gen`: Whip up a synthetic dataset
- `process`: Give your existing dataset a makeover
- `filter`: Separate the wheat from the chaff in your data
- `check`: Make sure your dataset is behaving itself
- `ask`: Interrogate your dataset (it won't bite, promise!)

### Pipeline Mode

Feeling lazy? (We don't judge.) Use the `apply` command to run a whole series of operations defined in a YAML file. It's like meal prep, but for data!

## 🏃‍♂️ Quick Start

1. Clone this bad boy:
   ```
   git clone https://github.com/your-username/dset.git
   ```

2. Install Poetry (if you haven't already):
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install the project dependencies:
   ```
   poetry install
   ```

4. Set up your OpenAI API key:
   ```
   export OPENAI_API_KEY='your-api-key-here'
   ```

5. Start processing like a boss:
   ```
   poetry run dset gen output.jsonl "Generate 10 random jokes"
   ```

## 🎛️ Usage

Here are some examples to get you started:

## 🧪 Running Tests

To run the tests for DSET, follow these steps:

1. Make sure you have installed the project dependencies using Poetry:
   ```
   poetry install
   ```

2. Run the tests using Poetry:
   ```
   poetry run pytest
   ```

This will execute all the tests in the `tests` directory.

## 📜 License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0-only). See the [LICENSE](LICENSE) file for details.

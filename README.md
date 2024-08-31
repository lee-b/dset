# `dset`: Automatic Dataset Processing using an LLM

**`dset` is a command-line tool for processing and manipulating datasets in JSONL format. It provides various operations to filter, merge, split, analyze, and generate datasets.**

## NOTE WELL: This is currently PRE-ALPHA, mostly "written" with aider in a few hours, and has NOT been tested at all yet, save for a pytests, which I don't know are correct, becuase they too were written by aider and I've barely skimmed the code as yet.

## Features

- **Filter**: Create a new dataset by filtering entries based on a natural-language condition.
- **Merge**: Combine multiple datasets into a single dataset, removing duplicates.
- **Split**: Divide a large dataset into smaller files based on a maximum size.
- **Ask**: Get a yes/no answer to a natural-language question for each entry in a dataset, and a summary of the reasons why not, if any.
- **Assert**: Like ask, but for pipelines. Confirms that a natural language condition is true for all entries in the dataset. Exits with the appropriate exit code (1 if any of the exceptions failed), plus a summary of the problem.
- **Generate**: Create a new synthetic dataset based on a given prompt.

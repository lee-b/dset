import json
import os

class DataSet:
    def __init__(self, path):
        self.path = path

    def process(self, processor):
        if os.path.isdir(self.path):
            return self._process_directory(processor)
        else:
            return self._process_file(processor)

    def _process_directory(self, processor):
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.endswith('.jsonl'):
                    yield from self._process_file(processor, os.path.join(root, file))

    def _process_file(self, processor, file_path=None):
        file_path = file_path or self.path
        with open(file_path, 'r') as f:
            for line in f:
                entry = json.loads(line.strip())
                yield processor(entry)

    def split(self, output_prefix, max_size):
        if os.path.isdir(self.path):
            for root, _, files in os.walk(self.path):
                for file in files:
                    if file.endswith('.jsonl'):
                        self._split_file(os.path.join(root, file), output_prefix, max_size)
        else:
            self._split_file(self.path, output_prefix, max_size)

    def _split_file(self, file_path, output_prefix, max_size):
        file_number = 1
        current_size = 0
        current_file = None

        with open(file_path, 'r') as input_file:
            for line in input_file:
                if current_file is None or current_size >= max_size:
                    if current_file:
                        current_file.close()
                    output_file = f"{output_prefix}_{file_number}.jsonl"
                    current_file = open(output_file, 'w')
                    current_size = 0
                    file_number += 1

                current_file.write(line)
                current_size += len(line)

        if current_file:
            current_file.close()

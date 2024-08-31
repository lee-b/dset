import os
import json

class DataSet:
    def __init__(self, path):
        self.path = path
        self.is_directory = os.path.isdir(path)

    def process(self, processor):
        if self.is_directory:
            return self._process_directory(processor)
        else:
            return self._process_file(processor)

    def _process_directory(self, processor):
        results = []
        for filename in os.listdir(self.path):
            if filename.endswith('.jsonl'):
                file_path = os.path.join(self.path, filename)
                results.extend(self._process_file(processor, file_path))
        return results

    def _process_file(self, processor, file_path=None):
        file_path = file_path or self.path
        results = []
        with open(file_path, 'r') as file:
            for line in file:
                entry = json.loads(line)
                result = processor(entry)
                results.append(result)
        return results

    def split(self, output_prefix, max_size):
        if self.is_directory:
            for filename in os.listdir(self.path):
                if filename.endswith('.jsonl'):
                    file_path = os.path.join(self.path, filename)
                    file_output_prefix = os.path.join(output_prefix, os.path.splitext(filename)[0])
                    self._split_file(file_path, file_output_prefix, max_size)
        else:
            self._split_file(self.path, output_prefix, max_size)

    def _split_file(self, file_path, output_prefix, max_size):
        file_number = 1
        current_size = 0
        current_file = None
        file_sizes = []

        with open(file_path, 'r') as infile:
            for line in infile:
                line_size = len(line.encode('utf-8'))

                if current_file is None or current_size + line_size > max_size:
                    if current_file:
                        current_file.close()
                        file_sizes.append(current_size)

                    output_file = f"{output_prefix}_{file_number}.jsonl"
                    current_file = open(output_file, 'w')
                    print(f"Created file: {output_file}")
                    current_size = 0
                    file_number += 1

                current_file.write(line)
                current_size += line_size

        if current_file:
            current_file.close()
            file_sizes.append(current_size)

        print(f"\nProcessed {os.path.basename(file_path)}:")
        print(f"Total files created: {len(file_sizes)}")
        print(f"Minimum file size: {min(file_sizes)} bytes")
        print(f"Maximum file size: {max(file_sizes)} bytes")

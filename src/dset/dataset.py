import json
from pathlib import Path
from typing import Any, Dict, Iterator, Callable

class ReadableDataSet:
    def __init__(self, path):
        self.path = Path(path)

    def process(self, processor: Callable[[Dict[str, Any]], Any]) -> Iterator[Any]:
        if self.path.is_dir():
            yield from self._process_directory(processor)
        else:
            yield from self._process_file(processor)

    def _process_directory(self, processor: Callable[[Dict[str, Any]], Any]) -> Iterator[Any]:
        for file_path in self.path.glob('*.jsonl'):
            yield from self._process_file(processor, file_path)

    def _process_file(self, processor: Callable[[Dict[str, Any]], Any], file_path=None) -> Iterator[Any]:
        path = file_path or self.path
        with open(path, 'r') as f:
            for line in f:
                entry = json.loads(line)
                yield processor(entry)

class WriteableDataSet(ReadableDataSet):
    def __init__(self, path):
        super().__init__(path)
        self.file = None

    def __enter__(self):
        self.file = open(self.path, 'w')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

    def write(self, entry: Dict[str, Any]):
        if not self.file:
            raise RuntimeError("WriteableDataSet must be used as a context manager")
        json.dump(entry, self.file)
        self.file.write('\n')

    def split(self, output_prefix, max_size):
        if self.path.is_dir():
            for file_path in self.path.glob('*.jsonl'):
                self._split_file(file_path, output_prefix, max_size)
        else:
            self._split_file(self.path, output_prefix, max_size)

    def _split_file(self, file_path, output_prefix, max_size):
        file_size = 0
        file_count = 1
        current_output = None

        with open(file_path, 'r') as input_file:
            for line in input_file:
                if file_size == 0 or file_size >= max_size:
                    if current_output:
                        current_output.close()
                    output_path = f"{output_prefix}_{file_count}.jsonl"
                    current_output = open(output_path, 'w')
                    file_size = 0
                    file_count += 1

                current_output.write(line)
                file_size += len(line)

        if current_output:
            current_output.close()

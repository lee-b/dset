from pydantic import BaseModel
from typing import Any, Dict

class JsonLEntry(BaseModel):
    data: Dict[str, Any]

    def __init__(self, **data):
        super().__init__(data=data)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, key):
        return key in self.data

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    def to_dict(self):
        return self.data

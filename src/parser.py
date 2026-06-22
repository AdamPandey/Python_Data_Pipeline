from typing import Dict, Any

class RecursiveNestedParser:
    @staticmethod
    def flatten_nested_structure(data: Any, prefix: str = "") -> Dict[str, Any]:
        flat_dict = {}
        if isinstance(data, dict):
            for key, value in data.items():
                nested_prefix = f"{prefix}_{key}" if prefix else key
                flat_dict.update(RecursiveNestedParser.flatten_nested_structure(value, nested_prefix))
        elif isinstance(data, list):
            for index, item in enumerate(data):
                nested_prefix = f"{prefix}_{index}" if prefix else str(index)
                flat_dict.update(RecursiveNestedParser.flatten_nested_structure(item, nested_prefix))
        else:
            flat_dict[prefix] = data
        return flat_dict
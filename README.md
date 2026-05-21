# vischema

vischema is a lightweight, interactive schema visualizer and editor widget for Jupyter, VS Code interactive notebooks, and Marimo. It validates Python dictionaries in real time against LinkML schemas using Pydantic, displays error pointers inline, and synchronizes edits back to the input dictionary in-place.

The library is production-ready for interactive schema validation and editing inside notebook environments.

## Installation

Install the package directly from the Git repository:

```bash
pip install git+https://github.com/rzlim08/vischema.git
```

## Quickstart

### 1. Using a File-based Schema

Pass the file path or URL to the schema and an initial dictionary of data:

```python
from vischema import SchemaEditor

initial_data = {
    "zarr_format": 3,
    "node_type": "array",
    "shape": [100, 100],
    "data_type": "int8"
}

# The editor will render a UI matching the schema definition
editor = SchemaEditor(
    initial_data=initial_data,
    schema="path/to/zarr_v3_schema.yaml"
)
editor
```

### 2. Using an Inline YAML Schema

Define a schema directly inside the notebook as a YAML string:

```python
from vischema import SchemaEditor

yaml_schema = """
id: user_schema
name: user_schema
imports:
  - linkml:types
classes:
  User:
    tree_root: true
    attributes:
      username:
        range: string
        required: true
        pattern: "^[a-zA-Z0-9]+$"
      email:
        range: string
        required: true
"""

user_data = {
    "username": "coder123",
    "email": "coder@example.com"
}

editor = SchemaEditor(
    initial_data=user_data,
    schema=yaml_schema
)
editor
```

### 3. Using an Inline Dictionary Schema

Pass a Python dictionary structure directly to the `schema` argument:

```python
from vischema import SchemaEditor

dict_schema = {
    "id": "product_schema",
    "name": "product_schema",
    "imports": ["linkml:types"],
    "classes": {
        "Product": {
            "tree_root": True,
            "attributes": {
                "product_id": {"range": "string", "required": True},
                "price": {"range": "float", "required": True}
            }
        }
    }
}

product_data = {
    "product_id": "P-100",
    "price": 29.99
}

editor = SchemaEditor(
    initial_data=product_data,
    schema=dict_schema
)
editor
```

## Features

- **Live UI Generation**: Auto-generates UI fields based on the provided LinkML schema classes.
- **In-Place Mutation**: Modifying UI inputs automatically updates the original input dictionary in Python in-place.
- **Pydantic Validation**: Uses LinkML's `PydanticValidationPlugin` for precise type validation.
- **JSON Pointer Errors**: Directs validation errors to the matching input fields on the UI.
- **Inline Schema Definitions**: Directly supports dict schemas, YAML string schemas, and file paths.

## Development

Run tests with `uv`:

```bash
uv run pytest
```

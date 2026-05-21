import pytest
from vischema.widget import SchemaEditor

def test_widget_initialization():
    initial_data = {
        "zarr_format": 3,
        "node_type": "array",
        "shape": [100, 100],
        "data_type": "int8",
        "chunk_grid": {"name": "regular"},
        "chunk_key_encoding": {"name": "default"},
        "fill_value": "0"
    }
    editor = SchemaEditor(initial_data=initial_data, schema_path="tests/test_schemas/zarr_v3_schema.yaml")
    assert editor.json_data == initial_data
    assert editor.schema_errors == {}

def test_widget_validation_errors():
    initial_data = {
        "zarr_format": 2, # error: must be 3
        "node_type": "array",
        "shape": [100, 100],
        "data_type": "int8",
        "chunk_grid": {"name": "regular"},
        "chunk_key_encoding": {"name": "default"},
        "fill_value": "0"
    }
    editor = SchemaEditor(initial_data=initial_data, schema_path="tests/test_schemas/zarr_v3_schema.yaml")
    # Format error should be detected
    assert "/zarr_format" in editor.schema_errors
    assert "greater than or equal to 3" in editor.schema_errors["/zarr_format"]

def test_widget_update_triggers_validation():
    initial_data = {
        "zarr_format": 3,
        "node_type": "array",
        "shape": [100, 100],
        "data_type": "int8",
        "chunk_grid": {"name": "regular"},
        "chunk_key_encoding": {"name": "default"},
        "fill_value": "0"
    }
    editor = SchemaEditor(initial_data=initial_data, schema_path="tests/test_schemas/zarr_v3_schema.yaml")
    assert editor.schema_errors == {}
    
    # Update via setting json_data (simulating a save_changes call from JS)
    new_data = dict(initial_data)
    new_data["zarr_format"] = 2
    editor.json_data = new_data
    
    # The observe callback should have triggered validation
    assert "/zarr_format" in editor.schema_errors

def test_widget_missing_required_fields():
    initial_data = {
        "zarr_format": 3,
        "node_type": "array",
        # "shape": [100, 100],  # Missing required field
        "data_type": "int8",
        "chunk_grid": {"name": "regular"},
        "chunk_key_encoding": {"name": "default"},
        "fill_value": "0"
    }
    editor = SchemaEditor(initial_data=initial_data, schema_path="tests/test_schemas/zarr_v3_schema.yaml")
    assert "/shape" in editor.schema_errors
    assert "Field required" in editor.schema_errors["/shape"]

def test_widget_initial_data_inplace_update():
    initial_data = {
        "zarr_format": 3,
        "node_type": "array",
        "shape": [100, 100],
        "data_type": "int8",
        "chunk_grid": {"name": "regular"},
        "chunk_key_encoding": {"name": "default"},
        "fill_value": "0"
    }
    editor = SchemaEditor(initial_data=initial_data, schema_path="tests/test_schemas/zarr_v3_schema.yaml")
    
    # Check that initial_data is initially unmodified
    assert initial_data["zarr_format"] == 3
    
    # Now simulate a UI update (which replaces json_data with a new dict)
    new_data = dict(initial_data)
    new_data["zarr_format"] = 2
    new_data["shape"] = [200, 200]
    
    editor.json_data = new_data
    
    # Verify that initial_data was mutated in-place
    assert initial_data["zarr_format"] == 2
    assert initial_data["shape"] == [200, 200]
    assert id(initial_data) != id(editor.json_data)

def test_widget_inline_dict_schema():
    schema_dict = {
        "id": "test_schema",
        "name": "test_schema",
        "imports": ["linkml:types"],
        "classes": {
            "Person": {
                "tree_root": True,
                "attributes": {
                    "name": {"range": "string", "required": True},
                    "age": {"range": "integer"}
                }
            }
        }
    }
    
    initial_data = {"name": "Alice", "age": 30}
    editor = SchemaEditor(initial_data=initial_data, schema=schema_dict)
    assert editor.schema_errors == {}
    
    # Trigger a validation error
    editor.json_data = {"age": 30} # Missing name
    assert "/name" in editor.schema_errors

def test_widget_inline_yaml_schema():
    schema_yaml = """
id: test_schema
name: test_schema
imports:
  - linkml:types
classes:
  Person:
    tree_root: true
    attributes:
      name:
        range: string
        required: true
      age:
        range: integer
"""
    
    initial_data = {"name": "Alice", "age": 30}
    editor = SchemaEditor(initial_data=initial_data, schema=schema_yaml)
    assert editor.schema_errors == {}
    
    # Trigger a validation error
    editor.json_data = {"age": 30} # Missing name
    assert "/name" in editor.schema_errors
import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import vischema
    return mo, vischema


@app.cell
def _(mo, vischema):
    mo.md(
        """
        # Dynamic Inline Schema Editor
        This notebook showcases the ability of `SchemaEditor` to accept schemas defined directly inline as **YAML strings** or **Python dictionaries**.
        It also demonstrates how the original input dictionary gets **updated in-place** reactively as you edit the UI fields.
        """
    )
    return


@app.cell
def _(mo, vischema):
    mo.md("## Demo 1: Inline YAML Schema")
    
    # Defining schema as an inline YAML string
    yaml_schema = """
id: inline_yaml_schema
name: inline_yaml_schema
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
      age:
        range: integer
"""

    user_payload = {
        "username": "coder123",
        "email": "coder@example.com",
        "age": 25
    }

    yaml_editor = mo.ui.anywidget(
        vischema.SchemaEditor(
            initial_data=user_payload,
            schema=yaml_schema
        )
    )
    
    return yaml_editor, yaml_schema, user_payload


@app.cell
def _(yaml_editor):
    yaml_editor
    return


@app.cell
def _(mo, user_payload, yaml_editor):
    # This cell updates reactively when the widget changes
    current_data = yaml_editor.value.get("json_data", {})
    schema_errors = yaml_editor.value.get("schema_errors", {})

    mo.vstack([
        mo.md("### Live Verification (In-Place Mutation)"),
        mo.md(f"**Original Dict Object ID:** `{id(user_payload)}`"),
        mo.md(f"**Current Widget Object ID:** `{id(yaml_editor.value.get('json_data'))}` (Should be different)"),
        mo.md(f"**Original `user_payload` values (Updated In-Place!):**"),
        user_payload,
        mo.md(f"**Active Validation Errors:**"),
        schema_errors if schema_errors else "None (Valid!)"
    ])
    return current_data, schema_errors


@app.cell
def _(mo, vischema):
    mo.md("## Demo 2: Inline Dictionary Schema")
    
    # Defining schema as a Python dictionary
    dict_schema = {
        "id": "inline_dict_schema",
        "name": "inline_dict_schema",
        "imports": ["linkml:types"],
        "classes": {
            "Product": {
                "tree_root": True,
                "attributes": {
                    "product_id": {"range": "string", "required": True},
                    "price": {"range": "float", "required": True},
                    "instock": {"range": "boolean"}
                }
            }
        }
    }

    product_payload = {
        "product_id": "P-100",
        "price": 49.99,
        "instock": True
    }

    dict_editor = mo.ui.anywidget(
        vischema.SchemaEditor(
            initial_data=product_payload,
            schema=dict_schema
        )
    )
    
    return dict_editor, dict_schema, product_payload


@app.cell
def _(dict_editor):
    dict_editor
    return


@app.cell
def _(mo, product_payload, dict_editor):
    current_product_data = dict_editor.value.get("json_data", {})
    product_errors = dict_editor.value.get("schema_errors", {})

    mo.vstack([
        mo.md("### Live Verification (In-Place Mutation)"),
        mo.md(f"**Original Dict Object ID:** `{id(product_payload)}`"),
        mo.md(f"**Original `product_payload` values (Updated In-Place!):**"),
        product_payload,
        mo.md(f"**Active Validation Errors:**"),
        product_errors if product_errors else "None (Valid!)"
    ])
    return current_product_data, product_errors


if __name__ == "__main__":
    app.run()

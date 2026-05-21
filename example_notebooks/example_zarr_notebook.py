import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import vischema

    # This configuration purposefully triggers an error to verify validation tracking:
    # 1. 'zarr_format' is wrong (must be 3).
    invalid_zarr_v3_payload = {
        "zarr_format": 2, 
        "node_type": "array",
        "shape": [10000, 10000],
        "data_type": "float64",
        "chunk_grid": {
            "name": "irregular-grid-test", 
            "configuration": {
                "chunk_shape": [1000, 1000]
            }
        },
        "chunk_key_encoding": {
            "name": "default",
            "configuration": {
                "separator": "/"
            }
        },
        "fill_value": 0,
        "codecs": [
            {"name": "bytes", "configuration": {"endian": "little"}},
            {"name": "gzip", "configuration": {"level": 5}}
        ]
    }

    # Bootstrapping your dynamic LinkML component
    editor = mo.ui.anywidget(
        vischema.SchemaEditor(
            initial_data=invalid_zarr_v3_payload, 
            schema_path="tests/test_schemas/zarr_v3_schema.yaml"
        )
    )

    editor
    return editor, invalid_zarr_v3_payload, mo


@app.cell
def _(editor, invalid_zarr_v3_payload, mo):
    # Destructure the widget value
    current_data = editor.value.get("json_data", {})
    schema_errors = editor.value.get("schema_errors", {})

    # Display proof of the live in-place update
    proof_ui = mo.vstack([
        mo.md("### Live Notebook Reactivity"),
        mo.md(f"**Original Dict Updated In-Place?** `{invalid_zarr_v3_payload == current_data}`"),
        mo.md(f"**Original Dict `zarr_format`:** `{invalid_zarr_v3_payload.get('zarr_format')}`"),
        mo.md("**Current Data:**"),
        current_data
    ])

    proof_ui
    return


@app.cell
def _(invalid_zarr_v3_payload):
    invalid_zarr_v3_payload
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()

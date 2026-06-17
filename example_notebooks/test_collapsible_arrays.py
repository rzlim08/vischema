import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import vischema

    return mo, vischema


@app.cell
def _(mo):
    mo.md("""
    # Collapsible Array / Object Sections

    Manual test for the collapsible-sections feature.

    The payload below has a long `channels` **array of objects**, each
    channel carrying a nested `biological_annotation` **object**. Every
    complex section header renders a `▾` toggle:

    - Click **CHANNELS** to fold the whole array (header shows the count,
      e.g. `CHANNELS (4)`).
    - Click an individual `[0]`, `[1]`, … to fold a single channel.
    - Click `biological_annotation` to fold just the nested object.

    Primitive arrays (`shard_shape`, `chunk_shape`) stay as plain inputs —
    no toggle, since they aren't tall.
    """)
    return


@app.cell
def _():
    # Schema defined as a dict (not an inline YAML string) so marimo's
    # auto-formatter can't mangle the significant indentation. It has an
    # array-of-objects (channels) and a nested object (biological_annotation)
    # so every kind of collapsible section is exercised.
    image_schema = {
        "id": "image_metadata_schema",
        "name": "image_metadata_schema",
        "imports": ["linkml:types"],
        "classes": {
            "ImageMetadata": {
                "tree_root": True,
                "attributes": {
                    "version": {"range": "string"},
                    "url": {"range": "string"},
                    "shard_shape": {"range": "integer", "multivalued": True},
                    "chunk_shape": {"range": "integer", "multivalued": True},
                    "channels": {
                        "range": "Channel",
                        "multivalued": True,
                        "inlined_as_list": True,
                    },
                },
            },
            "Channel": {
                "attributes": {
                    "name": {"range": "string", "required": True},
                    "index": {"range": "integer"},
                    "channel_type": {"range": "string"},
                    "description": {"range": "string"},
                    "biological_annotation": {
                        "range": "BiologicalAnnotation",
                        "inlined": True,
                    },
                },
            },
            "BiologicalAnnotation": {
                "attributes": {
                    "cell_type": {"range": "string"},
                    "marker": {"range": "string"},
                },
            },
        },
    }
    return (image_schema,)


@app.cell
def _():
    def _channel(idx, name, ctype, desc, cell_type, marker):
        return {
            "name": name,
            "index": idx,
            "channel_type": ctype,
            "description": desc,
            "biological_annotation": {"cell_type": cell_type, "marker": marker},
        }

    image_payload = {
        "version": "0.2",
        "url": "https://raw.githubusercontent.com/chanzuckerberg/dynamic/main/schema.yaml",
        "shard_shape": [13, 1, 1, 2048, 1920],
        "chunk_shape": [13, 1, 1, 256, 128],
        "channels": [
            _channel(0, "Hoechst", "fluorescence", "Nuclear DNA stained with Hoechst 33342 (Ex 405 nm)", "all", "DNA"),
            _channel(1, "CD3", "fluorescence", "T-cell co-receptor", "T cell", "CD3"),
            _channel(2, "CD20", "fluorescence", "B-cell marker", "B cell", "CD20"),
            _channel(3, "PanCK", "fluorescence", "Epithelial cytokeratin", "epithelial", "PanCK"),
        ],
    }
    return (image_payload,)


@app.cell
def _(image_payload, image_schema, mo, vischema):
    editor = mo.ui.anywidget(
        vischema.SchemaEditor(
            initial_data=image_payload,
            schema=image_schema,
        )
    )

    editor
    return (editor,)


@app.cell
def _(editor, image_payload, mo):
    current_data = editor.value.get("json_data", {})
    schema_errors = editor.value.get("schema_errors", {})

    mo.vstack([
        mo.md("### Live State"),
        mo.md(f"**Channel count:** `{len(current_data.get('channels', []))}`"),
        mo.md(f"**Updated in-place?** `{image_payload == current_data}`"),
        mo.md("**Active validation errors:**"),
        schema_errors if schema_errors else "None (Valid!)",
    ])
    return


if __name__ == "__main__":
    app.run()

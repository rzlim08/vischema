# src/vischema/widget.py
import json
from pathlib import Path
import anywidget
import traitlets
from linkml.validator import Validator
from linkml.validator.plugins import PydanticValidationPlugin  # Switch to Pydantic
from linkml_runtime.utils.schemaview import SchemaView
from linkml_runtime.linkml_model import SchemaDefinition
from linkml_runtime.loaders import yaml_loader, json_loader

ASSETS_DIR = Path(__file__).parent / "assets"

class SchemaEditor(anywidget.AnyWidget):
    _esm = ASSETS_DIR / "index.js"
    _css = ASSETS_DIR / "index.css"
    
    # Dual-channel traitlets mapped live to the browser UI
    json_data = traitlets.Dict({}).tag(sync=True)
    schema_errors = traitlets.Dict({}).tag(sync=True)
    # Initial collapse state for complex sections: "none", "all", or "arrays".
    collapsed = traitlets.Unicode("none").tag(sync=True)

    def __init__(
        self,
        initial_data: dict,
        schema_path: str | dict | SchemaDefinition = None,
        target_class: str = None,
        schema: str | dict | SchemaDefinition = None,
        collapsed: bool | str = False,
        **kwargs
    ):
        super().__init__(**kwargs)

        self._initial_data = initial_data
        self._target_class = target_class

        # Normalize the collapse parameter into the trait's string mode.
        # True -> collapse every complex section; False -> none; or pass
        # "arrays"/"all"/"none" explicitly to collapse only arrays, etc.
        if isinstance(collapsed, bool):
            self.collapsed = "all" if collapsed else "none"
        elif collapsed in ("none", "all", "arrays"):
            self.collapsed = collapsed
        else:
            raise ValueError(
                "collapsed must be a bool or one of 'none', 'all', 'arrays'; "
                f"got {collapsed!r}"
            )

        # Determine and normalize schema input
        schema_input = schema if schema is not None else schema_path
        if schema_input is None:
            raise ValueError("Either 'schema' or 'schema_path' must be provided.")

        self._schema = schema_input
        if isinstance(self._schema, dict):
            # Parse dict schema to SchemaDefinition
            self._schema = json_loader.loads(json.dumps(self._schema), SchemaDefinition)
        elif isinstance(self._schema, str):
            # Resolve if it is a file path on disk or a URL; otherwise parse as YAML string
            if "\n" not in self._schema and (Path(self._schema).exists() or self._schema.startswith(("http://", "https://"))):
                if Path(self._schema).exists():
                    self._schema = str(Path(self._schema).resolve())
            else:
                self._schema = yaml_loader.loads(self._schema, SchemaDefinition)
        
        # 1. Initialize the Validator with Pydantic - gives exact, reliable dictionary paths
        self._validator = Validator(
            schema=self._schema,
            validation_plugins=[PydanticValidationPlugin()]
        )
        
        # 2. Automated type inference fallback if tree_root is missing
        if not self._target_class:
            sv = SchemaView(self._schema)
            roots = [k for k, v in sv.all_classes().items() if v.tree_root]
            self._target_class = roots[0] if roots else list(sv.all_classes().keys())[0]

        # 3. Synchronize initial state payload and kick off live observation loop
        self.json_data = initial_data
        self.observe(self._validate_schema, names=["json_data"])
        
        # Immediate validation pass on widget bootup
        self._validate_schema(None)

    def _validate_schema(self, change):
        # Update the original dict in-place if it exists and is a different object
        if hasattr(self, "_initial_data") and isinstance(self._initial_data, dict) and self._initial_data is not self.json_data:
            self._initial_data.clear()
            self._initial_data.update(self.json_data)

        report = self._validator.validate(self.json_data, target_class=self._target_class)
        errors = {}
        
        for result in report.results:
            msg = result.message
            if not msg:
                continue
                
            # Keep raw lines (including indentation) to parse Pydantic errors structurally
            raw_lines = [line for line in msg.split("\n") if line.strip()]
            current_field = None
            
            for line in raw_lines:
                stripped = line.lstrip()
                indent = len(line) - len(stripped)
                
                # Skip Pydantic summary headers
                if "validation errors for" in line or "validation error for" in line:
                    continue
                
                if indent == 0:
                    current_field = stripped
                elif indent == 2 and current_field:
                    # Clean up the trailing Pydantic URL string and type metadata brackets
                    clean_msg = stripped.split(" [type=")[0]
                    # Map nested field paths (e.g. 'chunk_grid.name' or 'chunk_grid -> name') to '/chunk_grid/name' JSON Pointer format
                    field_path = current_field.replace(" -> ", "/").replace(".", "/")
                    pointer = f"/{field_path}"
                    errors[pointer] = clean_msg
                    
        # Synchronize back to the JS UI components over the traitlet sync loop
        self.schema_errors = errors
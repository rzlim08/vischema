// src/vischema/assets/index.js
export default {
    render({ model, el }) {
        // Deep helper to extract flattening and depth paths for rendering.
        // Recurses into objects and into arrays whose items are themselves
        // complex (objects/arrays). Arrays of primitives stay as a single
        // leaf rendered as a JSON-encoded value, e.g. `[1,1,1,1024,1024]`.
        function flattenJson(obj, prefix = '', depth = 0) {
            let paths = {};
            const parentIsArray = Array.isArray(obj);
            for (let key in obj) {
                const pointerPath = `${prefix}/${key}`;
                const val = obj[key];
                const isObject = val !== null && typeof val === 'object';
                const hasComplexItems = Array.isArray(val)
                    && val.some(x => x !== null && typeof x === 'object');
                const isComplex = isObject && (!Array.isArray(val) || hasComplexItems);
                const displayKey = parentIsArray ? `[${key}]` : key;

                paths[pointerPath] = { key: displayKey, value: val, isComplex, depth };
                if (isComplex) {
                    Object.assign(paths, flattenJson(val, pointerPath, depth + 1));
                }
            }
            return paths;
        }

        // Initialize Base Container
        const container = document.createElement("div");
        container.className = "schema-editor-container";
        el.appendChild(container);

        // Tracks which complex sections (objects/arrays) are collapsed.
        // Persists across re-renders triggered by model changes.
        const collapsed = new Set();

        const renderRows = () => {
            const data = model.get("json_data") || {};
            const errors = model.get("schema_errors") || {};
            const flatPaths = flattenJson(data);

            container.innerHTML = `<div class="schema-editor-fields"></div>`;
            const fieldsWrapper = container.querySelector(".schema-editor-fields");

            Object.keys(flatPaths).forEach(pointerPath => {
                const node = flatPaths[pointerPath];

                // Hide any row that lives under a collapsed ancestor section.
                const isHidden = [...collapsed].some(c => pointerPath.startsWith(c + '/'));
                if (isHidden) return;

                if (node.isComplex) {
                    const isCollapsed = collapsed.has(pointerPath);
                    const isArray = Array.isArray(node.value);
                    const count = isArray ? ` (${node.value.length})` : '';

                    const sectionHeader = document.createElement("div");
                    sectionHeader.className = "schema-section-header";
                    sectionHeader.style.paddingLeft = `${node.depth * 16}px`;
                    sectionHeader.innerHTML = `
                        <span class="schema-section-toggle ${isCollapsed ? 'collapsed' : ''}">▾</span>
                        <span>${node.key}${count}</span>
                    `;
                    sectionHeader.addEventListener("click", () => {
                        if (collapsed.has(pointerPath)) collapsed.delete(pointerPath);
                        else collapsed.add(pointerPath);
                        renderRows();
                    });
                    fieldsWrapper.appendChild(sectionHeader);
                    return;
                }

                const fieldRow = document.createElement("div");
                fieldRow.className = "schema-field-row";
                fieldRow.style.paddingLeft = `${node.depth * 16}px`;

                const hasError = errors.hasOwnProperty(pointerPath);
                const displayValue = typeof node.value === 'object' ? JSON.stringify(node.value) : node.value;
                const dotPath = pointerPath.slice(1).replace(/\//g, '.');

                fieldRow.innerHTML = `
                    <div class="schema-field-meta">
                        <span class="schema-field-name">${node.key}</span>
                        <span class="schema-field-path">${dotPath}</span>
                    </div>
                    <div class="schema-input-wrapper">
                        <input 
                            data-pointer="${pointerPath}" 
                            class="schema-input ${hasError ? 'has-error' : ''}"
                        />
                        ${hasError ? `<p class="schema-error-text">⚠️ ${errors[pointerPath]}</p>` : ''}
                    </div>
                `;

                // Set value safely via property assignment to avoid HTML quote escaping issues
                const inputEl = fieldRow.querySelector("input");
                inputEl.value = displayValue ?? '';

                inputEl.addEventListener("change", (e) => {
                    let rawValue = e.target.value;
                    let parsedValue = rawValue;

                    // Implicit Type Coercion Utility
                    if (rawValue === "true") parsedValue = true;
                    else if (rawValue === "false") parsedValue = false;
                    else if (rawValue === "null") parsedValue = null;
                    else if (!isNaN(rawValue) && rawValue.trim() !== "") {
                        parsedValue = Number(rawValue);
                    } else {
                        try {
                            if (rawValue.startsWith("[") || rawValue.startsWith("{")) {
                                parsedValue = JSON.parse(rawValue);
                            }
                        } catch (err) { /* Keep as string fallback if parsing fails */ }
                    }

                    // Mutate deep reference data
                    const updatedData = JSON.parse(JSON.stringify(model.get("json_data")));
                    const segments = pointerPath.split("/").slice(1);
                    
                    let target = updatedData;
                    for (let i = 0; i < segments.length - 1; i++) {
                        target = target[segments[i]];
                    }
                    target[segments[segments.length - 1]] = parsedValue;

                    model.set("json_data", updatedData);
                    model.save_changes();
                });

                fieldsWrapper.appendChild(fieldRow);
            });
        };

        model.on("change:json_data", renderRows);
        model.on("change:schema_errors", renderRows);
        renderRows();
    }
};
import os


class DocstringInjector:
    def inject_docstring(self, file_path: str, metadata: dict, docstring: str):
        ext = os.path.splitext(file_path)[1].lower()

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        target_line_idx = metadata["lineno"] - 1

        if target_line_idx >= len(lines):
            return

        if ext == ".py":
            self._inject_python(lines, target_line_idx, docstring)
        else:
            self._inject_js(lines, target_line_idx, docstring)

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"✅ Injected into {os.path.basename(file_path)} ({metadata['name']})")

    # ===============================
    # PYTHON INJECTION (CORRECT)
    # ===============================
    def _inject_python(self, lines, target_line_idx, docstring):
        def_line = lines[target_line_idx]
        indentation = len(def_line) - len(def_line.lstrip())
        indent_str = " " * indentation
        body_indent = " " * (indentation + 4)

        # Prevent double injection
        if target_line_idx + 1 < len(lines):
            next_line = lines[target_line_idx + 1].strip()
            if next_line.startswith('"""'):
                print("⚠ Existing docstring detected. Skipping.")
                return

        formatted_doc = f'{body_indent}"""\n'

        for line in docstring.split("\n"):
            if line.strip():
                formatted_doc += f"{body_indent}{line.strip()}\n"

        formatted_doc += f'{body_indent}"""\n'

        lines.insert(target_line_idx + 1, formatted_doc)

    # ===============================
    # JS / TS INJECTION
    # ===============================
    def _inject_js(self, lines, target_line_idx, docstring):
        indentation = len(lines[target_line_idx]) - len(lines[target_line_idx].lstrip())
        indent_str = " " * indentation

        formatted_doc = f"{indent_str}/**\n"

        for line in docstring.split("\n"):
            if line.strip():
                formatted_doc += f"{indent_str} * {line.strip()}\n"

        formatted_doc += f"{indent_str} */\n"

        lines.insert(target_line_idx, formatted_doc)

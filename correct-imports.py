import ast
import re
import subprocess
from pathlib import Path


ROOT = Path(".")


def find_util_imports(tree):
    usages = set()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue

        parts = []
        current = node

        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value

        if isinstance(current, ast.Name):
            parts.append(current.id)

        parts.reverse()

        if len(parts) >= 4 and parts[0] == "util":
            usages.add(tuple(parts[:3]))

    return usages


def sort_imports(path):
    """Run isort on the modified file."""
    subprocess.run(
        ["isort", str(path)],
        check=True,
    )


def process_file(path):
    source = path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        print(f"Skipping {path}: {exc}")
        return

    usages = find_util_imports(tree)

    if not usages:
        return

    replacements = {}

    for _, library, module in usages:
        old_prefix = f"util.{library}.{module}"
        new_prefix = module

        replacements[old_prefix] = new_prefix

    new_source = source

    for old_prefix, new_prefix in sorted(
        replacements.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        new_source = re.sub(
            rf"\b{re.escape(old_prefix)}\b",
            new_prefix,
            new_source,
        )

    imports = [
        f"from {library} import {module}"
        for _, library, module in sorted(usages)
    ]

    import_block = "\n".join(imports) + "\n"

    lines = new_source.splitlines(keepends=True)

    insert_at = 0

    if lines and lines[0].startswith("#!"):
        insert_at = 1

    while (
        insert_at < len(lines)
        and "coding" in lines[insert_at]
        and lines[insert_at].lstrip().startswith("#")
    ):
        insert_at += 1

    lines.insert(insert_at, import_block)

    path.write_text("".join(lines), encoding="utf-8")

    # Let isort fix the imports.
    sort_imports(path)

    print(f"Updated: {path}")


def main():
    for path in ROOT.rglob("*.py"):
        if any(
            part in {
                "venv",
                ".venv",
                "__pycache__",
                ".git",
                "node_modules",
            }
            for part in path.parts
        ):
            continue

        process_file(path)


if __name__ == "__main__":
    main()
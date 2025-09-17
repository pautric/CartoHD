import ast
import os
import sys
import toml
import sysconfig

def get_stdlib_modules():
    """Return a set of Python standard library module names."""
    stdlib_path = sysconfig.get_paths()["stdlib"]
    stdlib_modules = set(sys.builtin_module_names)  # built-in modules

    for root, _, files in os.walk(stdlib_path):
        for f in files:
            if f.endswith(".py") and f != "__init__.py":
                mod = os.path.splitext(f)[0]
                stdlib_modules.add(mod)
        for d in _:
            stdlib_modules.add(d)

    return stdlib_modules


def get_imports_from_file(filepath):
    """Parse a Python file and extract top-level imports."""
    imports = set()
    with open(filepath, "r", encoding="utf-8") as file:
        node = ast.parse(file.read(), filename=filepath)
        for n in ast.walk(node):
            if isinstance(n, ast.Import):
                for alias in n.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(n, ast.ImportFrom):
                if n.module:
                    imports.add(n.module.split(".")[0])
    return imports


def get_all_imports(folder):
    """Scan all .py files in a folder and collect unique imports."""
    all_imports = set()
    for root, _, files in os.walk(folder):
        for f in files:
            if f.endswith(".py"):
                file_path = os.path.join(root, f)
                all_imports |= get_imports_from_file(file_path)
    return all_imports


def update_pyproject(pyproject_path, imports):
    """Update pyproject.toml dependencies with discovered imports."""
    if not os.path.exists(pyproject_path):
        raise FileNotFoundError(f"{pyproject_path} not found")

    stdlib_modules = get_stdlib_modules()
    filtered_imports = {pkg for pkg in imports if pkg not in stdlib_modules}

    print("📦 Third-party imports (to be added):", filtered_imports)

    data = toml.load(pyproject_path)

    # Handle both Poetry-style and PEP 621
    if "tool" in data and "poetry" in data["tool"]:
        deps = data["tool"]["poetry"].get("dependencies", {})
        for pkg in filtered_imports:
            if pkg not in deps:
                deps[pkg] = "*"
        data["tool"]["poetry"]["dependencies"] = deps
    elif "project" in data:
        deps = data["project"].get("dependencies", [])
        dep_names = {d.split(" ")[0] for d in deps}  # handle version specifiers
        for pkg in filtered_imports:
            if pkg not in dep_names:
                deps.append(pkg)
        data["project"]["dependencies"] = deps
    else:
        raise ValueError("Unsupported pyproject.toml structure")

    with open(pyproject_path, "w", encoding="utf-8") as f:
        toml.dump(data, f)

    print("✅ pyproject.toml updated successfully!")


if __name__ == "__main__":
    folder = "./"  # your Python files folder
    pyproject_path = "pyproject.toml"

    imports = get_all_imports(folder)
    update_pyproject(pyproject_path, imports)
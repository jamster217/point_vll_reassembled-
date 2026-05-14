from __future__ import annotations

DIRECT_ANSWER_TEMPLATES = {
    "python_import_error": "Check the module name, confirm the package is installed in the active environment, and verify you are running the same Python interpreter where it was installed.",
    "flask_termux_module": "In Termux, make sure Flask is installed in the same Python environment you are running, then verify your working directory and import path from the project root.",
    "flask_module": "Check that Flask is installed in the active environment and that your entrypoint imports resolve from the project root.",
    "termux_path": "Check the package path, confirm storage permissions, and verify the working directory before running the script.",
    "venv_package": "Activate the intended virtual environment first, then reinstall the package there and print sys.executable to confirm the interpreter path.",
    "generic_error": "Read the exact error line, identify the failing import or call, then verify path, package install, and interpreter alignment.",
    "default_direct": "Follow the failing path, verify the active environment, and correct the first concrete mismatch.",
}

def practical_frame(text: str) -> dict:
    lower = (text or "").lower()

    if "flask" in lower and "termux" in lower:
        return {"template": "flask_termux_module", "slots": {}}
    if "import error" in lower or ("python" in lower and "module" in lower):
        return {"template": "python_import_error", "slots": {}}
    if "flask" in lower:
        return {"template": "flask_module", "slots": {}}
    if "termux" in lower:
        return {"template": "termux_path", "slots": {}}
    if "pip" in lower or "venv" in lower:
        return {"template": "venv_package", "slots": {}}
    if "error" in lower or "module" in lower:
        return {"template": "generic_error", "slots": {}}
    return {"template": "default_direct", "slots": {}}

def render_direct_answer(frame: dict) -> str:
    key = frame.get("template", "default_direct")
    slots = frame.get("slots", {})
    template = DIRECT_ANSWER_TEMPLATES.get(key, DIRECT_ANSWER_TEMPLATES["default_direct"])
    try:
        return template.format(**slots)
    except Exception:
        return template


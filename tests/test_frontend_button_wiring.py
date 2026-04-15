import re
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"


def _frontend_sources():
    html_files = sorted(FRONTEND_DIR.glob("*.html"))
    js_files = sorted(FRONTEND_DIR.glob("*.js")) + sorted((FRONTEND_DIR / "js").rglob("*.js"))
    return html_files, js_files


def _collect_defined_function_names():
    html_files, js_files = _frontend_sources()
    names = set()

    definition_patterns = (
        re.compile(r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("),
        re.compile(r"\bwindow\.([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:async\s+)?function\b"),
        re.compile(r"\bwindow\.([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>"),
        re.compile(r"\b(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:async\s+)?function\b"),
        re.compile(r"\b(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>"),
    )

    for source_file in [*html_files, *js_files]:
        content = source_file.read_text(encoding="utf-8", errors="ignore")
        for pattern in definition_patterns:
            names.update(pattern.findall(content))

    return names


def test_inline_onclick_handlers_are_defined():
    html_files, _ = _frontend_sources()
    defined_names = _collect_defined_function_names()
    missing = []

    onclick_pattern = re.compile(r'onclick\s*=\s*"([A-Za-z_][A-Za-z0-9_]*)\s*\(')
    for html_file in html_files:
        content = html_file.read_text(encoding="utf-8", errors="ignore")
        for function_name in onclick_pattern.findall(content):
            if function_name not in defined_names:
                missing.append((html_file.name, function_name))

    assert not missing, f"Missing onclick handlers: {missing}"


def test_button_ids_are_unique_per_page():
    html_files, _ = _frontend_sources()
    button_id_pattern = re.compile(r"<button[^>]*\sid=\"([^\"]+)\"[^>]*>", flags=re.IGNORECASE)

    duplicates = []
    for html_file in html_files:
        ids = button_id_pattern.findall(html_file.read_text(encoding="utf-8", errors="ignore"))
        seen = set()
        for button_id in ids:
            if button_id in seen:
                duplicates.append((html_file.name, button_id))
            seen.add(button_id)

    assert not duplicates, f"Duplicate button IDs found: {duplicates}"

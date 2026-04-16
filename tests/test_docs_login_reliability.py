from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DOCS_LOGIN = ROOT_DIR / "docs" / "login.html"


def test_docs_login_has_recoverable_lockout_controls():
    content = DOCS_LOGIN.read_text(encoding="utf-8", errors="ignore")

    assert "function clearDemoLockout" in content
    assert "Reset demo lockout" in content


def test_docs_login_uses_safe_failed_attempts_parsing():
    content = DOCS_LOGIN.read_text(encoding="utf-8", errors="ignore")

    get_failed_attempts_block_start = content.index("function getFailedAttempts()")
    get_failed_attempts_block_end = content.index("function setFailedAttempts")
    get_failed_attempts_block = content[get_failed_attempts_block_start:get_failed_attempts_block_end]

    assert "try {" in get_failed_attempts_block
    assert "JSON.parse" in get_failed_attempts_block
    assert "localStorage.removeItem('failedLoginAttempts')" in get_failed_attempts_block


def test_docs_login_does_not_permanently_disable_button_on_load():
    content = DOCS_LOGIN.read_text(encoding="utf-8", errors="ignore")

    dom_loaded_block_start = content.index("window.addEventListener('DOMContentLoaded'")
    dom_loaded_block = content[dom_loaded_block_start:]

    assert "setLoginButtonState({ loading: false, disabled: false });" in dom_loaded_block
    assert "document.getElementById('loginBtn').disabled = true;" not in dom_loaded_block


def test_docs_login_disables_lockout_for_static_demo_mode():
    content = DOCS_LOGIN.read_text(encoding="utf-8", errors="ignore")

    assert "const ENABLE_DEMO_LOCKOUT = false;" in content
    assert "if (!ENABLE_DEMO_LOCKOUT) {" in content
    assert "resetFailedAttempts();" in content

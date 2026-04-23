"""Pytest config for MultiverseMA.

All test_*.py files are Selenium E2E suites requiring Chrome/chromedriver
+ local HTTP server on port 8780. Skip collection unless RUN_BROWSER_TESTS=1.

Rationale: these Selenium files also reassign sys.stdout at module level,
which breaks pytest's terminal writer at session-finish. Excluding them
avoids the teardown crash entirely.

To run browser tests manually:
    $Env:RUN_BROWSER_TESTS = "1"
    python -m pytest tests/test_multiversema.py -v
"""
import os

if not os.environ.get("RUN_BROWSER_TESTS"):
    collect_ignore_glob = [
        "test_multiverse.py",
        "tests/test_multiversema.py",
        "tests/test_ui.py",
    ]

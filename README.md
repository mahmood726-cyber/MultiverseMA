# MultiverseMA

MultiverseMA: Browser-Based Multiverse Meta-Analysis Engine.

A single-file, offline HTML tool that runs a meta-analysis across a "multiverse"
of analytic specifications (heterogeneity estimators, CI methods, publication-bias
adjustments) so you can see how robust a pooled estimate is to defensible choices.

- Interactive app: `multiverse-ma.html` (open directly in a browser).
- E156 submission bundle: `e156-submission/` (page + engine asset + paper).

## Running the tests

Install dev dependencies:

```
pip install -r requirements.txt
```

Default suite (fast, no browser required) — HTML smoke checks plus headless
numerical regression tests that execute the JS estimator functions under Node.js
(Node must be on `PATH`; the numeric tests skip automatically if it is not):

```
python -m pytest
```

Optional browser end-to-end suites (Selenium) — require a local Chrome +
matching chromedriver and are skipped unless `RUN_BROWSER_TESTS` is set:

```
# PowerShell
$Env:RUN_BROWSER_TESTS = "1"; python -m pytest tests/test_multiversema.py tests/test_ui.py -v

# bash
RUN_BROWSER_TESTS=1 python -m pytest tests/test_multiversema.py tests/test_ui.py -v
```

`tests/test_multiversema.py` loads the app from a `file://` URL;
`tests/test_ui.py` serves it over a local HTTP server on an ephemeral port.

_Status: Needs triage (portfolio registry)._

"""Headless numerical regression tests for the MultiverseMA JS engine.

These run in the DEFAULT `python -m pytest` path (no browser, no Selenium).
They extract the pure JS estimator functions out of the HTML files and execute
them under Node.js, then assert the returned tau2/theta/se.

Motivation: the Sidik-Jonkman (SJ) tau2 iteration in the shipped submission
asset once weighted squared residuals by the variance (v_i + tau2) instead of
the precision w_i = 1/(v_i + tau2), which made the fixed-point iteration DIVERGE
(tau2 climbed ~1/iter to the 100-iteration cap, returning tau2=101, se=5.83 for
yi=[1,2,3], vi=[1,1,1]). The correct precision-weighted form converges to
tau2=0.618, se=0.734. Only file-existence smoke tests existed before, so the
bug shipped undetected. This module pins the SJ estimator so it cannot recur.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ENGINE_FILES = [
    ROOT / "multiverse-ma.html",
    ROOT / "e156-submission" / "assets" / "multiverse-ma.html",
]

NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="node.js not available on PATH")


def _extract_function(source: str, name: str) -> str:
    """Return the source text of a top-level `function name(...) { ... }` block
    using brace matching (regex can't balance braces reliably)."""
    marker = f"function {name}("
    start = source.find(marker)
    assert start != -1, f"function {name} not found"
    brace = source.find("{", start)
    assert brace != -1
    depth = 0
    i = brace
    while i < len(source):
        c = source[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return source[start : i + 1]
        i += 1
    raise AssertionError(f"unbalanced braces extracting {name}")


def _run_sj(engine_path: Path, yi, vi):
    src = engine_path.read_text(encoding="utf-8")
    # sjEstimator depends only on fixedEffectMA (used solely for the k<2 branch
    # and for Q/I2); both are pure numeric functions with no DOM references.
    snippet = (
        _extract_function(src, "fixedEffectMA")
        + "\n"
        + _extract_function(src, "sjEstimator")
        + "\n"
        + f"const __r = sjEstimator({json.dumps(yi)}, {json.dumps(vi)});\n"
        + "console.log(JSON.stringify(__r));\n"
    )
    out = subprocess.run(
        [NODE, "-e", snippet],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert out.returncode == 0, f"node failed: {out.stderr}"
    return json.loads(out.stdout.strip())


@pytest.mark.parametrize("engine_path", ENGINE_FILES, ids=lambda p: p.parent.name)
def test_sj_estimator_converges_not_diverges(engine_path):
    """SJ must converge for yi=[1,2,3], vi=[1,1,1].

    Divergent (buggy) form returns tau2=101, se=5.83. Correct form: ~0.618/0.734.
    """
    r = _run_sj(engine_path, [1, 2, 3], [1, 1, 1])
    assert r["tau2"] == pytest.approx(0.6180339887, abs=1e-6)
    assert r["se"] == pytest.approx(0.7344008871, abs=1e-6)
    assert r["theta"] == pytest.approx(2.0, abs=1e-9)


@pytest.mark.parametrize("engine_path", ENGINE_FILES, ids=lambda p: p.parent.name)
def test_sj_estimator_stays_bounded(engine_path):
    """A second dataset: tau2 must stay finite and small, not blow up to the cap."""
    r = _run_sj(engine_path, [0.1, 0.3, 0.5, 0.2], [0.05, 0.02, 0.08, 0.03])
    assert r["tau2"] < 1.0
    assert r["se"] < 0.5
    assert r["theta"] == pytest.approx(0.2666961393, abs=1e-6)


@pytest.mark.parametrize("engine_path", ENGINE_FILES, ids=lambda p: p.parent.name)
def test_sj_estimator_k1_degrades_to_fixed_effect(engine_path):
    """k=1 edge case: falls back to fixed-effect (tau2=0)."""
    r = _run_sj(engine_path, [1.5], [0.25])
    assert r["tau2"] == 0
    assert r["theta"] == pytest.approx(1.5, abs=1e-9)
    assert r["se"] == pytest.approx(0.5, abs=1e-9)

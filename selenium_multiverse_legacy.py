"""
Comprehensive Selenium test suite for MultiverseMA
(multiverse-ma.html) — 45 tests across 8 categories.

Tests: Page Load, Data Input, Core Engine, Decision Panel,
Stability Dashboard, Visualizations, Accessibility, Export.
"""

import sys
import io
import time
import traceback

# UTF-8 encoding for Windows (skip under pytest so terminal capture isn't broken)
if "pytest" not in sys.modules:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ---- Configuration ----
BASE_URL = "http://localhost:8780/multiverse-ma.html"
TIMEOUT = 20  # seconds for WebDriverWait


def create_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1400,900")
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(2)
    return driver


# ---- Helpers ----

def load_page(driver):
    """Load the page fresh."""
    driver.get(BASE_URL)
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.ID, "dataCard"))
    )
    # Wait for auto-load and auto-run to complete
    time.sleep(3)


def load_page_no_wait(driver):
    """Load page with minimal wait (for tests that manipulate before auto-run)."""
    driver.get(BASE_URL)
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.ID, "dataCard"))
    )
    time.sleep(0.5)


def load_bcg(driver):
    """Load BCG dataset via JS."""
    driver.execute_script("loadDataset('bcg')")
    time.sleep(0.3)


def load_aspirin(driver):
    driver.execute_script("loadDataset('aspirin')")
    time.sleep(0.3)


def load_omega3(driver):
    driver.execute_script("loadDataset('omega3')")
    time.sleep(0.3)


def run_analysis(driver, wait_secs=5):
    """Click Run Multiverse Analysis and wait for results."""
    driver.execute_script("""
        document.getElementById('runBtn').disabled = false;
        document.getElementById('runBtn').click();
    """)
    time.sleep(0.3)
    WebDriverWait(driver, TIMEOUT).until(
        lambda d: d.execute_script(
            "return document.getElementById('resultsSection').style.display !== 'none'"
        )
    )
    time.sleep(wait_secs)


def get_spec_count(driver):
    """Return the spec count shown in the banner."""
    txt = driver.find_element(By.ID, "specCountNum").text
    return int(txt.replace(",", ""))


def get_console_errors(driver):
    """Return SEVERE console log entries."""
    logs = driver.get_log("browser")
    return [l for l in logs if l["level"] == "SEVERE"]


def ensure_results(driver):
    """Make sure we have results (page auto-loads BCG and runs)."""
    n = driver.execute_script("return specResults.length")
    if not n or n == 0:
        load_bcg(driver)
        run_analysis(driver, wait_secs=4)


# ---- Test Runner ----

results = []


def record(name, passed, detail=""):
    status = "PASSED" if passed else "FAILED"
    results.append((name, passed, detail))
    print(f"  [{status}] {name}" + (f" -- {detail}" if detail else ""))


# ============================================================
# CATEGORY 1: Page Load & UI (6 tests)
# ============================================================

def test_cat1(driver):
    print("\n=== Category 1: Page Load & UI ===")

    # Test 1: Page loads with correct title
    load_page(driver)
    title = driver.title
    record("1. Page title", "Multiverse" in title and "Meta" in title,
           f"title='{title}'")

    # Test 2: Auto-loaded BCG dataset on page load
    badge = driver.find_element(By.ID, "studyCountBadge").text
    record("2. Auto-loads BCG dataset on startup", "13" in badge,
           f"badge='{badge}'")

    # Test 3: Auto-runs analysis on page load (results visible)
    results_section = driver.find_element(By.ID, "resultsSection")
    is_visible = results_section.value_of_css_property("display") != "none"
    record("3. Auto-runs analysis on load", is_visible,
           f"resultsVisible={is_visible}")

    # Test 4: Decision space shows 8 dimensions (including Effect Measure)
    dims = driver.find_elements(By.CSS_SELECTOR, ".decision-dim")
    record("4. Decision space: 8 dimensions",
           len(dims) == 8,
           f"found {len(dims)} dims")

    # Test 5: Spec count banner displays a positive number
    count = get_spec_count(driver)
    record("5. Spec count > 0", count > 0, f"specCount={count}")

    # Test 6: Dark mode toggle works
    body_cls_before = driver.find_element(By.TAG_NAME, "body").get_attribute("class") or ""
    driver.execute_script("toggleTheme()")
    time.sleep(0.3)
    body_cls_after = driver.find_element(By.TAG_NAME, "body").get_attribute("class") or ""
    dark_toggled = ("dark" in body_cls_after) != ("dark" in body_cls_before)
    record("6. Dark mode toggle works", dark_toggled,
           f"before='{body_cls_before}' after='{body_cls_after}'")
    driver.execute_script("toggleTheme()")  # toggle back


# ============================================================
# CATEGORY 2: Data Input (5 tests)
# ============================================================

def test_cat2(driver):
    print("\n=== Category 2: Data Input ===")

    # Test 7: Load BCG -> 13 studies
    load_page_no_wait(driver)
    load_bcg(driver)
    badge = driver.find_element(By.ID, "studyCountBadge").text
    rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
    record("7. Load BCG: 13 studies", "13" in badge and len(rows) == 13,
           f"badge='{badge}', rows={len(rows)}")

    # Test 8: Load Aspirin -> 8 studies
    load_aspirin(driver)
    badge = driver.find_element(By.ID, "studyCountBadge").text
    record("8. Load Aspirin: 8 studies", "8" in badge,
           f"badge='{badge}'")

    # Test 9: Load Omega-3 -> 7 studies
    load_omega3(driver)
    badge = driver.find_element(By.ID, "studyCountBadge").text
    record("9. Load Omega-3: 7 studies", "7" in badge,
           f"badge='{badge}'")

    # Test 10: Add/remove study rows
    load_page_no_wait(driver)
    load_bcg(driver)
    initial_rows = len(driver.find_elements(By.CSS_SELECTOR, "#dataBody tr"))
    driver.execute_script("addRow()")
    time.sleep(0.2)
    after_add = len(driver.find_elements(By.CSS_SELECTOR, "#dataBody tr"))
    driver.execute_script(
        "document.querySelector('#dataBody tr:last-child button').click()"
    )
    time.sleep(0.2)
    after_remove = len(driver.find_elements(By.CSS_SELECTOR, "#dataBody tr"))
    record("10. Add/remove study rows",
           after_add == initial_rows + 1 and after_remove == initial_rows,
           f"initial={initial_rows}, add={after_add}, remove={after_remove}")

    # Test 11: Clear All empties table
    driver.execute_script("clearAllData()")
    time.sleep(0.2)
    rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
    badge = driver.find_element(By.ID, "studyCountBadge").text
    record("11. Clear All empties table",
           len(rows) == 0 and "0" in badge,
           f"rows={len(rows)}, badge='{badge}'")


# ============================================================
# CATEGORY 3: Core Engine (7 tests)
# ============================================================

def test_cat3(driver):
    print("\n=== Category 3: Core Engine ===")

    load_page(driver)
    ensure_results(driver)

    # Test 12: Results produced
    n_results = driver.execute_script("return specResults.length")
    record("12. Specifications produced", n_results > 0,
           f"specResults.length={n_results}")

    # Test 13: Median effect is negative (BCG protective)
    median_effect = driver.execute_script("""
        const eff = specResults.map(r => r.theta).sort((a,b) => a-b);
        return eff[Math.floor(eff.length/2)];
    """)
    record("13. Median effect is negative (BCG protective)",
           median_effect is not None and median_effect < 0,
           f"median={median_effect}")

    # Test 14: All effects have finite values
    has_nan = driver.execute_script("""
        return specResults.some(r => !isFinite(r.theta) || !isFinite(r.lower) || !isFinite(r.upper) || !isFinite(r.pval));
    """)
    record("14. All effects are finite", has_nan is False,
           f"hasNaN={has_nan}")

    # Test 15: p-values are in [0, 1]
    bad_pvals = driver.execute_script("""
        return specResults.filter(r => r.pval < 0 || r.pval > 1).length;
    """)
    record("15. All p-values in [0, 1]", bad_pvals == 0,
           f"badPvals={bad_pvals}")

    # Test 16: tau2 >= 0 for all specs
    neg_tau2 = driver.execute_script("""
        return specResults.filter(r => r.tau2 < 0).length;
    """)
    record("16. tau2 >= 0 for all specs", neg_tau2 == 0,
           f"negTau2={neg_tau2}")

    # Test 17: I2 in [0, 100] for all specs
    bad_i2 = driver.execute_script("""
        return specResults.filter(r => r.I2 < 0 || r.I2 > 100).length;
    """)
    record("17. I2 in [0, 100]", bad_i2 == 0, f"badI2={bad_i2}")

    # Test 18: Each spec has effect_measure field
    has_em = driver.execute_script("""
        return specResults.every(r => r.effect_measure !== undefined && r.effect_measure !== null);
    """)
    record("18. All specs have effect_measure field", has_em is True,
           f"allHaveEffectMeasure={has_em}")


# ============================================================
# CATEGORY 4: Decision Panel (7 tests)
# ============================================================

def test_cat4(driver):
    print("\n=== Category 4: Decision Panel ===")

    load_page_no_wait(driver)
    load_bcg(driver)

    # Test 19: 8 estimators available (FE, DL, REML, PM, ML, SJ, HO, HS)
    est_options = driver.execute_script("""
        const dim = decisionDimensions.find(d => d.id === 'estimator');
        return dim ? dim.options.map(o => o.id) : [];
    """)
    record("19. 8 estimators available",
           len(est_options) == 8 and 'HO' in est_options and 'HS' in est_options,
           f"estimators={est_options}")

    # Test 20: Effect Measure dimension exists with 3 options
    em_options = driver.execute_script("""
        const dim = decisionDimensions.find(d => d.id === 'effect_measure');
        return dim ? dim.options.map(o => o.id) : [];
    """)
    record("20. Effect Measure dimension exists (3 options)",
           len(em_options) == 3 and 'original' in em_options,
           f"options={em_options}")

    # Test 21: Select All / None buttons exist for each dimension
    all_btns = driver.find_elements(By.XPATH,
        "//div[contains(@class,'decision-dim')]//button[text()='All']"
    )
    none_btns = driver.find_elements(By.XPATH,
        "//div[contains(@class,'decision-dim')]//button[text()='None']"
    )
    record("21. Select All/None buttons exist",
           len(all_btns) == 8 and len(none_btns) == 8,
           f"allBtns={len(all_btns)}, noneBtns={len(none_btns)}")

    # Test 22: Checking all options increases spec count
    default_count = get_spec_count(driver)
    driver.execute_script("""
        for (const dim of decisionDimensions) {
            for (const opt of dim.options) {
                opt.checked = true;
            }
        }
        renderDecisionGrid();
    """)
    time.sleep(0.3)
    all_count = get_spec_count(driver)
    record("22. All options increases spec count",
           all_count > default_count * 2,
           f"default={default_count}, all={all_count}")

    # Test 23: Publication bias options (trim-fill, PET-PEESE)
    pub_bias_opts = driver.execute_script("""
        const dim = decisionDimensions.find(d => d.id === 'pub_bias');
        return dim ? dim.options.map(o => o.id) : [];
    """)
    record("23. Pub bias: none, trimfill, petpeese",
           set(pub_bias_opts) == {'none', 'trimfill', 'petpeese'},
           f"options={pub_bias_opts}")

    # Test 24: Conf level has 90/95/99
    conf_opts = driver.execute_script("""
        const dim = decisionDimensions.find(d => d.id === 'conf_level');
        return dim ? dim.options.map(o => o.id) : [];
    """)
    record("24. Conf level: 90/95/99",
           set(conf_opts) == {'0.90', '0.95', '0.99'},
           f"options={conf_opts}")

    # Test 25: LOO has none and loo options
    loo_opts = driver.execute_script("""
        const dim = decisionDimensions.find(d => d.id === 'loo');
        return dim ? dim.options.map(o => o.id) : [];
    """)
    record("25. LOO: none and loo",
           set(loo_opts) == {'none', 'loo'},
           f"options={loo_opts}")


# ============================================================
# CATEGORY 5: Stability Dashboard (5 tests)
# ============================================================

def test_cat5(driver):
    print("\n=== Category 5: Stability Dashboard ===")

    load_page(driver)
    ensure_results(driver)

    # Test 26: Stability dashboard renders with content
    dashboard = driver.find_element(By.ID, "stabilityDashboard")
    html = dashboard.get_attribute("innerHTML")
    record("26. Stability dashboard renders",
           len(html) > 100 and "stability-card" in html,
           f"htmlLen={len(html)}")

    # Test 27: Overall robustness verdict present (ROBUST/MODERATE/FRAGILE)
    verdict = driver.find_elements(By.CSS_SELECTOR, "#stabilityDashboard .verdict")
    verdict_text = verdict[0].text if verdict else ""
    record("27. Robustness verdict present",
           verdict_text in ['ROBUST', 'MODERATE', 'FRAGILE'],
           f"verdict='{verdict_text}'")

    # Test 28: BCG should show ROBUST verdict (high concordance)
    record("28. BCG shows ROBUST verdict",
           verdict_text == 'ROBUST',
           f"verdict='{verdict_text}'")

    # Test 29: Concordance table renders with alpha levels
    tbody = driver.find_element(By.ID, "concordanceTableBody")
    rows = tbody.find_elements(By.TAG_NAME, "tr")
    record("29. Concordance table has 5 alpha levels",
           len(rows) == 5,
           f"rows={len(rows)}")

    # Test 30: P-curve histogram renders
    pcurve = driver.find_element(By.ID, "pcurveContainer")
    pcurve_html = pcurve.get_attribute("innerHTML")
    has_svg = "<svg" in pcurve_html.lower()
    has_rect = "<rect" in pcurve_html.lower()
    record("30. P-curve histogram renders",
           has_svg and has_rect,
           f"hasSVG={has_svg}, hasRect={has_rect}")


# ============================================================
# CATEGORY 6: Visualizations (6 tests)
# ============================================================

def test_cat6(driver):
    print("\n=== Category 6: Visualizations ===")

    load_page(driver)
    ensure_results(driver)

    # Test 31: Spec curve SVG renders with circles
    spec_svg = driver.find_element(By.ID, "specCurveContainer")
    svg_content = spec_svg.get_attribute("innerHTML")
    record("31. Spec curve SVG renders",
           "<svg" in svg_content.lower() and "circle" in svg_content.lower(),
           f"hasSVG={'<svg' in svg_content.lower()}")

    # Test 32: Decision matrix (bottom panel) renders within spec curve
    has_matrix_labels = any(label in svg_content for label in ['Estimator', 'CI Method', 'Inclusion'])
    record("32. Decision matrix labels present",
           has_matrix_labels,
           f"hasMatrixLabels={has_matrix_labels}")

    # Test 33: Janus plot SVG renders
    janus = driver.find_element(By.ID, "janusPlotContainer")
    janus_html = janus.get_attribute("innerHTML")
    record("33. Janus plot renders",
           "<svg" in janus_html.lower() and "circle" in janus_html.lower(),
           f"hasSVG={'<svg' in janus_html.lower()}")

    # Test 34: Effect histogram renders
    hist = driver.find_element(By.ID, "specHistContainer")
    hist_html = hist.get_attribute("innerHTML")
    record("34. Effect histogram renders",
           "<svg" in hist_html.lower() and "rect" in hist_html.lower(),
           f"hasSVG={'<svg' in hist_html.lower()}")

    # Test 35: Tornado chart renders
    tornado = driver.find_element(By.ID, "tornadoContainer")
    tornado_html = tornado.get_attribute("innerHTML")
    record("35. Tornado chart renders",
           "<svg" in tornado_html.lower() and "rect" in tornado_html.lower(),
           f"hasSVG={'<svg' in tornado_html.lower()}")

    # Test 36: Influence decomposition bars render
    influence_bars = driver.find_elements(By.CSS_SELECTOR, "#influenceChart .influence-bar")
    record("36. Influence decomposition renders",
           len(influence_bars) >= 1,
           f"bars={len(influence_bars)}")


# ============================================================
# CATEGORY 7: Accessibility (5 tests)
# ============================================================

def test_cat7(driver):
    print("\n=== Category 7: Accessibility ===")

    load_page(driver)
    ensure_results(driver)

    # Test 37: Skip link exists
    skip_link = driver.find_elements(By.CSS_SELECTOR, ".skip-link")
    record("37. Skip link exists",
           len(skip_link) >= 1,
           f"found={len(skip_link)}")

    # Test 38: Decision dims have role="group" and aria-label
    dims_with_role = driver.find_elements(By.CSS_SELECTOR,
        ".decision-dim[role='group']"
    )
    record("38. Decision dims have ARIA roles",
           len(dims_with_role) == 8,
           f"withRole={len(dims_with_role)}")

    # Test 39: Spec detail panel has role="dialog"
    dialog = driver.find_elements(By.CSS_SELECTOR,
        "#specDetailPanel[role='dialog']"
    )
    record("39. Spec detail panel has role=dialog",
           len(dialog) == 1,
           f"found={len(dialog)}")

    # Test 40: Results section has aria-label
    results_section = driver.find_element(By.ID, "resultsSection")
    aria_label = results_section.get_attribute("aria-label")
    record("40. Results section has aria-label",
           aria_label is not None and len(aria_label) > 0,
           f"ariaLabel='{aria_label}'")

    # Test 41: Input fields have aria-labels
    data_inputs = driver.find_elements(By.CSS_SELECTOR, "#dataBody input[aria-label]")
    record("41. Data inputs have aria-labels",
           len(data_inputs) >= 5,  # at least 5 per row, 13 rows = 65+
           f"inputsWithAriaLabel={len(data_inputs)}")


# ============================================================
# CATEGORY 8: Export & Report (4 tests)
# ============================================================

def test_cat8(driver):
    print("\n=== Category 8: Export & Report ===")

    load_page(driver)
    ensure_results(driver)

    # Test 42: Methods text card is visible with content
    methods_card = driver.find_element(By.ID, "methodsTextCard")
    card_display = methods_card.value_of_css_property("display")
    methods_text = driver.find_element(By.ID, "methodsTextContent").text
    record("42. Methods text is visible with content",
           card_display != "none" and len(methods_text) > 50,
           f"display={card_display}, textLen={len(methods_text)}")

    # Test 43: Methods text mentions key terms
    has_multiverse = "multiverse" in methods_text.lower()
    has_median = "median" in methods_text.lower()
    record("43. Methods text has key terms",
           has_multiverse and has_median,
           f"multiverse={has_multiverse}, median={has_median}")

    # Test 44: CSV export doesn't throw errors
    driver.get_log("browser")  # clear
    driver.execute_script("""
        try { exportCSV(); } catch(e) { console.error('CSV_EXPORT_ERROR: ' + e.message); }
    """)
    time.sleep(0.5)
    errors = get_console_errors(driver)
    csv_errors = [e for e in errors if "CSV_EXPORT_ERROR" in e.get("message", "")]
    record("44. CSV export no errors",
           len(csv_errors) == 0,
           f"errors={len(csv_errors)}")

    # Test 45: Results table has rows
    table_rows = driver.find_elements(By.CSS_SELECTOR, "#resultsBody tr")
    record("45. Results table has data rows",
           len(table_rows) > 0,
           f"rows={len(table_rows)}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("Multiverse Meta-Analysis Engine - Selenium Test Suite")
    print(f"Target: {BASE_URL}")
    print("=" * 60)

    driver = None
    try:
        driver = create_driver()
        print(f"Chrome driver created.")

        test_cat1(driver)
        test_cat2(driver)
        test_cat3(driver)
        test_cat4(driver)
        test_cat5(driver)
        test_cat6(driver)
        test_cat7(driver)
        test_cat8(driver)

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        traceback.print_exc()
    finally:
        if driver:
            try:
                final_errors = get_console_errors(driver)
                if final_errors:
                    print(f"\n[INFO] {len(final_errors)} SEVERE console error(s) at end of run")
            except Exception:
                pass
            driver.quit()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, p, _ in results if p)
    failed = sum(1 for _, p, _ in results if not p)
    total = len(results)
    print(f"  PASSED: {passed}/{total}")
    print(f"  FAILED: {failed}/{total}")

    if failed > 0:
        print("\nFailed tests:")
        for name, p, detail in results:
            if not p:
                print(f"  - {name}: {detail}")

    print()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

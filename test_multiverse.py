"""
Comprehensive Selenium test suite for MultiverseMA
(multiverse-ma.html) — 32 tests across 6 categories.
"""

import sys
import io
import time
import traceback

# UTF-8 encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
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
    time.sleep(0.5)


def load_bcg(driver):
    """Load BCG dataset by clicking the dropdown, then BCG button."""
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
    # Wait for results section to become visible
    time.sleep(0.3)
    WebDriverWait(driver, TIMEOUT).until(
        lambda d: d.execute_script(
            "return document.getElementById('resultsSection').style.display !== 'none'"
        )
    )
    time.sleep(wait_secs)  # Let rendering complete


def get_spec_count(driver):
    """Return the spec count shown in the banner."""
    txt = driver.find_element(By.ID, "specCountNum").text
    return int(txt.replace(",", ""))


def get_console_errors(driver):
    """Return SEVERE console log entries."""
    logs = driver.get_log("browser")
    return [l for l in logs if l["level"] == "SEVERE"]


# ---- Test Runner ----

results = []


def record(name, passed, detail=""):
    status = "PASSED" if passed else "FAILED"
    results.append((name, passed, detail))
    print(f"  [{status}] {name}" + (f" -- {detail}" if detail else ""))


# ============================================================
# CATEGORY 1: Page Load & UI (5 tests)
# ============================================================

def test_cat1(driver):
    print("\n=== Category 1: Page Load & UI ===")

    # Test 1: Page loads with correct title
    load_page(driver)
    title = driver.title
    record("1. Page title", "Multiverse" in title and "Meta" in title,
           f"title='{title}'")

    # Test 2: Study data table renders with 5 empty rows
    rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
    record("2. Data table has 5 empty rows", len(rows) == 5,
           f"found {len(rows)} rows")

    # Test 3: Decision space shows 7 dimensions with checkboxes
    dims = driver.find_elements(By.CSS_SELECTOR, ".decision-dim")
    has_checkboxes = all(
        len(d.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")) > 0
        for d in dims
    )
    record("3. Decision space: 7 dimensions with checkboxes",
           len(dims) == 7 and has_checkboxes,
           f"found {len(dims)} dims, checkboxes={'yes' if has_checkboxes else 'no'}")

    # Test 4: Spec count banner displays
    banner = driver.find_element(By.ID, "specBanner")
    count_el = driver.find_element(By.ID, "specCountNum")
    record("4. Spec count banner displays",
           banner.is_displayed() and count_el.text != "",
           f"specCount='{count_el.text}'")

    # Test 5: Dark mode toggle works
    body_cls_before = driver.find_element(By.TAG_NAME, "body").get_attribute("class") or ""
    driver.execute_script("toggleTheme()")
    time.sleep(0.3)
    body_cls_after = driver.find_element(By.TAG_NAME, "body").get_attribute("class") or ""
    btn_text = driver.find_element(By.ID, "themeBtn").text
    dark_toggled = ("dark" in body_cls_after) != ("dark" in body_cls_before)
    record("5. Dark mode toggle works",
           dark_toggled and "Light" in btn_text,
           f"before='{body_cls_before}' after='{body_cls_after}' btn='{btn_text}'")
    # Toggle back
    driver.execute_script("toggleTheme()")


# ============================================================
# CATEGORY 2: Data Input (5 tests)
# ============================================================

def test_cat2(driver):
    print("\n=== Category 2: Data Input ===")

    # Test 6: Load BCG example -> 13 studies
    load_page(driver)
    load_bcg(driver)
    badge = driver.find_element(By.ID, "studyCountBadge").text
    rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
    record("6. Load BCG: 13 studies", "13" in badge and len(rows) == 13,
           f"badge='{badge}', rows={len(rows)}")

    # Test 7: Load Aspirin example -> 8 studies
    load_page(driver)
    load_aspirin(driver)
    badge = driver.find_element(By.ID, "studyCountBadge").text
    rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
    record("7. Load Aspirin: 8 studies", "8" in badge and len(rows) == 8,
           f"badge='{badge}', rows={len(rows)}")

    # Test 8: Load Omega-3 example -> 7 studies
    load_page(driver)
    load_omega3(driver)
    badge = driver.find_element(By.ID, "studyCountBadge").text
    rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
    record("8. Load Omega-3: 7 studies", "7" in badge and len(rows) == 7,
           f"badge='{badge}', rows={len(rows)}")

    # Test 9: Add/remove study rows work
    load_page(driver)
    initial_rows = len(driver.find_elements(By.CSS_SELECTOR, "#dataBody tr"))
    driver.execute_script("addRow()")
    time.sleep(0.2)
    after_add = len(driver.find_elements(By.CSS_SELECTOR, "#dataBody tr"))
    # Remove the last row
    driver.execute_script(
        "document.querySelector('#dataBody tr:last-child button').click()"
    )
    time.sleep(0.2)
    after_remove = len(driver.find_elements(By.CSS_SELECTOR, "#dataBody tr"))
    record("9. Add/remove study rows",
           after_add == initial_rows + 1 and after_remove == initial_rows,
           f"initial={initial_rows}, afterAdd={after_add}, afterRemove={after_remove}")

    # Test 10: Clear All empties table
    load_page(driver)
    load_bcg(driver)
    driver.execute_script("clearAllData()")
    time.sleep(0.2)
    rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
    badge = driver.find_element(By.ID, "studyCountBadge").text
    record("10. Clear All empties table",
           len(rows) == 0 and "0" in badge,
           f"rows={len(rows)}, badge='{badge}'")


# ============================================================
# CATEGORY 3: Core Engine (8 tests)
# ============================================================

def test_cat3(driver):
    print("\n=== Category 3: Core Engine ===")

    # Load BCG and run with default settings
    load_page(driver)
    load_bcg(driver)
    spec_count_before = get_spec_count(driver)
    record("11. BCG default spec count >= 24",
           spec_count_before >= 24,
           f"specCount={spec_count_before}")

    run_analysis(driver, wait_secs=4)

    # Get results from JS
    n_results = driver.execute_script("return specResults.length")
    record("11b. BCG specs actually ran",
           n_results >= 24,
           f"specResults.length={n_results}")

    # Test 12: Median effect is negative (BCG protective)
    median_effect = driver.execute_script("""
        const eff = specResults.map(r => r.theta).sort((a,b) => a-b);
        return eff[Math.floor(eff.length/2)];
    """)
    record("12. Median effect is negative (BCG protective)",
           median_effect is not None and median_effect < 0,
           f"median={median_effect}")

    # Test 13: Direction concordance = 100% (all negative for BCG)
    concordance = driver.execute_script("""
        const eff = specResults.map(r => r.theta);
        const neg = eff.filter(e => e < 0).length;
        const pos = eff.filter(e => e > 0).length;
        return Math.max(neg, pos) / eff.length * 100;
    """)
    record("13. Direction concordance = 100%",
           concordance is not None and concordance >= 99.9,
           f"concordance={concordance}%")

    # Test 14: VoE is small (< 0.5 for BCG default settings)
    voe = driver.execute_script("""
        const eff = specResults.map(r => r.theta);
        return Math.max(...eff) - Math.min(...eff);
    """)
    record("14. VoE is small for BCG",
           voe is not None and voe < 0.5,
           f"VoE={voe}")

    # Test 15: Influence chart renders (estimator bar visible)
    influence_bars = driver.find_elements(By.CSS_SELECTOR, "#influenceChart .influence-bar")
    record("15. Influence chart renders",
           len(influence_bars) >= 1,
           f"found {len(influence_bars)} influence bars")

    # Test 16: Results table has rows matching spec count
    table_rows = driver.find_elements(By.CSS_SELECTOR, "#resultsBody tr")
    # Results table caps at 500 rows
    expected_rows = min(n_results, 500)
    # If there are more than 500, there will be an extra "showing X of Y" row
    actual_data_rows = len(table_rows)
    if n_results > 500:
        actual_data_rows -= 1  # subtract the info row
    record("16. Results table has rows matching spec count",
           actual_data_rows == expected_rows,
           f"tableRows={actual_data_rows}, expected={expected_rows}")

    # Test 17: Spec curve SVG renders
    spec_svg = driver.find_element(By.ID, "specCurveContainer")
    svg_content = spec_svg.get_attribute("innerHTML")
    has_svg = "<svg" in svg_content.lower()
    has_circles = "circle" in svg_content.lower()
    record("17. Spec curve SVG renders",
           has_svg and has_circles,
           f"hasSVG={has_svg}, hasCircles={has_circles}")

    # Test 18: Janus plot SVG renders
    janus_container = driver.find_element(By.ID, "janusPlotContainer")
    janus_content = janus_container.get_attribute("innerHTML")
    has_svg_j = "<svg" in janus_content.lower()
    has_circles_j = "circle" in janus_content.lower()
    record("18. Janus plot SVG renders",
           has_svg_j and has_circles_j,
           f"hasSVG={has_svg_j}, hasCircles={has_circles_j}")


# ============================================================
# CATEGORY 4: Phase 2 Features (5 tests)
# ============================================================

def test_cat4(driver):
    print("\n=== Category 4: Phase 2 Features ===")

    # Test 19: Select all estimators + all options -> spec count increases substantially
    load_page(driver)
    load_bcg(driver)
    default_count = get_spec_count(driver)

    # Check ALL estimators (FE, ML, SJ are unchecked by default)
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
    record("19. Select all options -> spec count increases",
           all_count > default_count * 2,
           f"default={default_count}, all={all_count}")

    # Reset to defaults for remaining tests
    load_page(driver)
    load_bcg(driver)

    # Test 20: Publication bias options appear (trim-fill, PET-PEESE)
    pub_bias_labels = driver.execute_script("""
        const dim = decisionDimensions.find(d => d.id === 'pub_bias');
        return dim ? dim.options.map(o => o.label) : [];
    """)
    has_trimfill = any("trim" in l.lower() or "fill" in l.lower() for l in pub_bias_labels)
    has_petpeese = any("pet" in l.lower() for l in pub_bias_labels)
    record("20. Publication bias options (trim-fill, PET-PEESE)",
           has_trimfill and has_petpeese,
           f"labels={pub_bias_labels}")

    # Test 21: Confidence level dimension has 3 options (90/95/99)
    conf_options = driver.execute_script("""
        const dim = decisionDimensions.find(d => d.id === 'conf_level');
        return dim ? dim.options.map(o => o.id) : [];
    """)
    record("21. Confidence level has 3 options (90/95/99)",
           set(conf_options) == {"0.90", "0.95", "0.99"},
           f"options={conf_options}")

    # Test 22: Trim-and-fill changes results when selected
    # Run with ONLY no-adjustment vs ONLY trim-fill, compare median
    load_page(driver)
    load_bcg(driver)
    # Set only DL + Wald + all studies + no outlier + no pub bias + 95% + no LOO
    driver.execute_script("""
        for (const dim of decisionDimensions) {
            for (const opt of dim.options) {
                opt.checked = false;
            }
        }
        // DL only
        decisionDimensions.find(d=>d.id==='estimator').options.find(o=>o.id==='DL').checked = true;
        // Wald only
        decisionDimensions.find(d=>d.id==='ci_method').options.find(o=>o.id==='Wald').checked = true;
        // All studies
        decisionDimensions.find(d=>d.id==='inclusion').options.find(o=>o.id==='all').checked = true;
        // No outlier
        decisionDimensions.find(d=>d.id==='outlier').options.find(o=>o.id==='none').checked = true;
        // No pub bias
        decisionDimensions.find(d=>d.id==='pub_bias').options.find(o=>o.id==='none').checked = true;
        // 95% conf
        decisionDimensions.find(d=>d.id==='conf_level').options.find(o=>o.id==='0.95').checked = true;
        // No LOO
        decisionDimensions.find(d=>d.id==='loo').options.find(o=>o.id==='none').checked = true;
        renderDecisionGrid();
    """)
    time.sleep(0.2)
    run_analysis(driver, wait_secs=2)
    no_adj_effect = driver.execute_script("return specResults[0] ? specResults[0].theta : null")

    # Now switch to trim-fill only
    load_page(driver)
    load_bcg(driver)
    driver.execute_script("""
        for (const dim of decisionDimensions) {
            for (const opt of dim.options) {
                opt.checked = false;
            }
        }
        decisionDimensions.find(d=>d.id==='estimator').options.find(o=>o.id==='DL').checked = true;
        decisionDimensions.find(d=>d.id==='ci_method').options.find(o=>o.id==='Wald').checked = true;
        decisionDimensions.find(d=>d.id==='inclusion').options.find(o=>o.id==='all').checked = true;
        decisionDimensions.find(d=>d.id==='outlier').options.find(o=>o.id==='none').checked = true;
        decisionDimensions.find(d=>d.id==='pub_bias').options.find(o=>o.id==='trimfill').checked = true;
        decisionDimensions.find(d=>d.id==='conf_level').options.find(o=>o.id==='0.95').checked = true;
        decisionDimensions.find(d=>d.id==='loo').options.find(o=>o.id==='none').checked = true;
        renderDecisionGrid();
    """)
    time.sleep(0.2)
    run_analysis(driver, wait_secs=2)
    tf_effect = driver.execute_script("return specResults[0] ? specResults[0].theta : null")

    changed = (no_adj_effect is not None and tf_effect is not None and
               abs(no_adj_effect - tf_effect) > 0.0001)
    record("22. Trim-and-fill changes results",
           changed,
           f"noAdj={no_adj_effect}, trimFill={tf_effect}")

    # Test 23: PET-PEESE specification produces different effect than standard
    load_page(driver)
    load_bcg(driver)
    driver.execute_script("""
        for (const dim of decisionDimensions) {
            for (const opt of dim.options) {
                opt.checked = false;
            }
        }
        decisionDimensions.find(d=>d.id==='estimator').options.find(o=>o.id==='DL').checked = true;
        decisionDimensions.find(d=>d.id==='ci_method').options.find(o=>o.id==='Wald').checked = true;
        decisionDimensions.find(d=>d.id==='inclusion').options.find(o=>o.id==='all').checked = true;
        decisionDimensions.find(d=>d.id==='outlier').options.find(o=>o.id==='none').checked = true;
        decisionDimensions.find(d=>d.id==='pub_bias').options.find(o=>o.id==='petpeese').checked = true;
        decisionDimensions.find(d=>d.id==='conf_level').options.find(o=>o.id==='0.95').checked = true;
        decisionDimensions.find(d=>d.id==='loo').options.find(o=>o.id==='none').checked = true;
        renderDecisionGrid();
    """)
    time.sleep(0.2)
    run_analysis(driver, wait_secs=2)
    pp_effect = driver.execute_script("return specResults[0] ? specResults[0].theta : null")
    pp_changed = (no_adj_effect is not None and pp_effect is not None and
                  abs(no_adj_effect - pp_effect) > 0.0001)
    record("23. PET-PEESE produces different effect",
           pp_changed,
           f"noAdj={no_adj_effect}, petpeese={pp_effect}")


# ============================================================
# CATEGORY 5: Phase 3 Features (7 tests)
# ============================================================

def test_cat5(driver):
    print("\n=== Category 5: Phase 3 Features ===")

    # Test 24: Leave-one-out dimension exists with 2 options
    load_page(driver)
    loo_dim = driver.execute_script("""
        const dim = decisionDimensions.find(d => d.id === 'loo');
        return dim ? dim.options.map(o => o.id) : [];
    """)
    record("24. LOO dimension exists with 2 options",
           len(loo_dim) == 2 and "none" in loo_dim and "loo" in loo_dim,
           f"options={loo_dim}")

    # Test 25: Enabling LOO multiplies spec count by k
    load_page(driver)
    load_bcg(driver)
    # Set minimal config with LOO off
    driver.execute_script("""
        for (const dim of decisionDimensions) {
            for (const opt of dim.options) {
                opt.checked = false;
            }
        }
        decisionDimensions.find(d=>d.id==='estimator').options.find(o=>o.id==='DL').checked = true;
        decisionDimensions.find(d=>d.id==='ci_method').options.find(o=>o.id==='Wald').checked = true;
        decisionDimensions.find(d=>d.id==='inclusion').options.find(o=>o.id==='all').checked = true;
        decisionDimensions.find(d=>d.id==='outlier').options.find(o=>o.id==='none').checked = true;
        decisionDimensions.find(d=>d.id==='pub_bias').options.find(o=>o.id==='none').checked = true;
        decisionDimensions.find(d=>d.id==='conf_level').options.find(o=>o.id==='0.95').checked = true;
        decisionDimensions.find(d=>d.id==='loo').options.find(o=>o.id==='none').checked = true;
        renderDecisionGrid();
    """)
    time.sleep(0.2)
    count_no_loo = get_spec_count(driver)

    # Now enable LOO (both 'none' and 'loo')
    driver.execute_script("""
        decisionDimensions.find(d=>d.id==='loo').options.find(o=>o.id==='loo').checked = true;
        renderDecisionGrid();
    """)
    time.sleep(0.2)
    count_with_loo = get_spec_count(driver)
    # With 13 BCG studies, LOO 'loo' adds k=13 sub-specs, plus LOO 'none' adds 1
    # So count_with_loo should be count_no_loo * (1 + 13) = 14
    expected = count_no_loo * 14  # none(1) + loo(13)
    record("25. LOO multiplies spec count by k",
           count_with_loo == expected,
           f"noLOO={count_no_loo}, withLOO={count_with_loo}, expected={expected}")

    # Test 26: Cumulative concordance plot renders (SVG present)
    load_page(driver)
    load_bcg(driver)
    run_analysis(driver, wait_secs=4)
    conc_container = driver.find_element(By.ID, "concordanceContainer")
    conc_html = conc_container.get_attribute("innerHTML")
    has_conc_svg = "<svg" in conc_html.lower()
    record("26. Cumulative concordance plot renders",
           has_conc_svg,
           f"hasSVG={has_conc_svg}")

    # Test 27: Auto-generated methods text contains key phrases
    methods_card = driver.find_element(By.ID, "methodsTextCard")
    methods_visible = methods_card.get_attribute("style")
    methods_text = driver.find_element(By.ID, "methodsTextContent").text
    has_multiverse = "multiverse" in methods_text.lower()
    has_median = "median" in methods_text.lower()
    has_specs = "specification" in methods_text.lower()
    record("27. Methods text contains key phrases",
           has_multiverse and has_median and has_specs,
           f"multiverse={has_multiverse}, median={has_median}, specs={has_specs}, len={len(methods_text)}")

    # Test 28: Methods text "Copy" button exists
    copy_btn = driver.find_elements(By.XPATH,
        "//div[@id='methodsTextCard']//button[contains(text(),'Copy')]"
    )
    record("28. Methods text Copy button exists",
           len(copy_btn) >= 1,
           f"found {len(copy_btn)} copy button(s)")

    # Test 29: Report button exists in header
    report_btn = driver.find_elements(By.XPATH,
        "//header//button[contains(@onclick,'generateReport')]"
    )
    record("29. Report button exists in header",
           len(report_btn) >= 1,
           f"found {len(report_btn)} report button(s)")

    # Test 30: Dataset dropdown has 3 options
    dropdown_buttons = driver.find_elements(By.CSS_SELECTOR,
        "#datasetDropdown button"
    )
    record("30. Dataset dropdown has 3 options",
           len(dropdown_buttons) == 3,
           f"found {len(dropdown_buttons)} dataset options")


# ============================================================
# CATEGORY 6: Export (2 tests)
# ============================================================

def test_cat6(driver):
    print("\n=== Category 6: Export ===")

    # Test 31: Export CSV button exists
    load_page(driver)
    csv_btn = driver.find_elements(By.XPATH,
        "//header//button[contains(@onclick,'exportCSV')]"
    )
    record("31. Export CSV button exists",
           len(csv_btn) >= 1,
           f"found {len(csv_btn)} export CSV button(s)")

    # Test 32: CSV export doesn't error
    # Load data and run analysis first
    load_bcg(driver)
    run_analysis(driver, wait_secs=3)

    # Clear any previous console errors
    driver.get_log("browser")

    # Attempt CSV export (won't actually download in headless, but shouldn't throw)
    driver.execute_script("""
        try {
            exportCSV();
        } catch(e) {
            console.error('CSV_EXPORT_ERROR: ' + e.message);
        }
    """)
    time.sleep(0.5)
    errors = get_console_errors(driver)
    csv_errors = [e for e in errors if "CSV_EXPORT_ERROR" in e.get("message", "")]
    record("32. CSV export doesn't error",
           len(csv_errors) == 0,
           f"consoleErrors={len(csv_errors)}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("Multiverse Meta-Analysis Engine - Selenium Test Suite")
    print("=" * 60)

    driver = None
    try:
        driver = create_driver()
        print(f"Chrome driver created. Target: {BASE_URL}")

        test_cat1(driver)
        test_cat2(driver)
        test_cat3(driver)
        test_cat4(driver)
        test_cat5(driver)
        test_cat6(driver)

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        traceback.print_exc()
    finally:
        if driver:
            # Capture any remaining console errors
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

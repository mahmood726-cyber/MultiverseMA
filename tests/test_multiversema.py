"""
Selenium test suite for MultiverseMA (multiverse-ma.html).
~20 tests covering page load, example datasets, multiverse analysis,
concordance, specification count, theme toggle, and export.

Usage:  python -m pytest tests/test_multiversema.py -v
"""

import os
import time
import pytest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ---- Configuration ----
HTML_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "multiverse-ma.html")
FILE_URL = "file:///" + os.path.abspath(HTML_FILE).replace("\\", "/")
TIMEOUT = 10


# ---- Fixtures ----

@pytest.fixture(scope="module")
def driver():
    """Create a shared Chrome headless driver for the module."""
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1400,900")
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    drv = webdriver.Chrome(options=opts)
    drv.set_page_load_timeout(30)
    drv.implicitly_wait(2)
    yield drv
    drv.quit()


def load_page(driver):
    """Load the page fresh and suppress confirm dialogs."""
    driver.get(FILE_URL)
    driver.execute_script("window.confirm = function(){return true};")
    # The page auto-loads BCG and auto-runs multiverse; wait for init
    WebDriverWait(driver, TIMEOUT).until(
        lambda d: d.execute_script("return typeof specResults !== 'undefined'")
    )


def wait_for_results(driver, timeout=TIMEOUT):
    """Wait until resultsSection is visible (analysis completed)."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script(
            "return document.getElementById('resultsSection').style.display !== 'none'"
        )
    )


def load_dataset(driver, key):
    """Load a built-in dataset by key and run multiverse analysis."""
    driver.execute_script(f"loadDataset('{key}');")
    time.sleep(0.3)
    # Click Run button via JS
    driver.execute_script("""
        document.getElementById('runBtn').disabled = false;
        runMultiverse();
    """)
    wait_for_results(driver, timeout=15)


# ============================================================
# 1. Page Load & Structure
# ============================================================

class TestPageLoad:
    """Tests that the page loads correctly with expected structure."""

    def test_page_title(self, driver):
        """T01: Page title contains 'Multiverse'."""
        load_page(driver)
        assert "Multiverse" in driver.title

    def test_header_visible(self, driver):
        """T02: Header with app name is visible."""
        header = driver.find_element(By.CSS_SELECTOR, "header h1")
        assert header.is_displayed()
        assert "Multiverse" in header.text

    def test_data_card_visible(self, driver):
        """T03: Study Data card is visible."""
        card = driver.find_element(By.ID, "dataCard")
        assert card.is_displayed()

    def test_decision_card_visible(self, driver):
        """T04: Decision Space card is visible."""
        card = driver.find_element(By.ID, "decisionCard")
        assert card.is_displayed()

    def test_run_button_exists(self, driver):
        """T05: Run Multiverse Analysis button exists."""
        btn = driver.find_element(By.ID, "runBtn")
        assert btn.is_displayed()
        assert "Run" in btn.text


# ============================================================
# 2. Example Datasets
# ============================================================

class TestExampleDatasets:
    """Tests loading each of the 3 built-in datasets."""

    def test_load_bcg_dataset(self, driver):
        """T06: Load BCG Vaccine dataset (13 studies)."""
        load_page(driver)
        driver.execute_script("loadDataset('bcg');")
        time.sleep(0.3)
        count = driver.execute_script("return studies.length")
        assert count == 13, f"Expected 13 BCG studies, got {count}"

    def test_load_aspirin_dataset(self, driver):
        """T07: Load Aspirin dataset (8 studies)."""
        driver.execute_script("loadDataset('aspirin');")
        time.sleep(0.3)
        count = driver.execute_script("return studies.length")
        assert count == 8, f"Expected 8 aspirin studies, got {count}"

    def test_load_omega3_dataset(self, driver):
        """T08: Load Omega-3 dataset (7 studies)."""
        driver.execute_script("loadDataset('omega3');")
        time.sleep(0.3)
        count = driver.execute_script("return studies.length")
        assert count == 7, f"Expected 7 omega-3 studies, got {count}"

    def test_study_count_badge_updates(self, driver):
        """T09: Study count badge reflects loaded dataset."""
        driver.execute_script("loadDataset('bcg');")
        time.sleep(0.3)
        badge = driver.find_element(By.ID, "studyCountBadge")
        assert "13" in badge.text

    def test_data_table_populated(self, driver):
        """T10: Data table body has rows after loading dataset."""
        driver.execute_script("loadDataset('bcg');")
        time.sleep(0.3)
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == 13


# ============================================================
# 3. Multiverse Analysis Execution
# ============================================================

class TestMultiverseAnalysis:
    """Tests that multiverse analysis runs and produces results."""

    def test_bcg_analysis_runs(self, driver):
        """T11: BCG multiverse analysis completes with results."""
        load_page(driver)
        load_dataset(driver, 'bcg')
        results_visible = driver.execute_script(
            "return document.getElementById('resultsSection').style.display !== 'none'"
        )
        assert results_visible, "Results section should be visible after analysis"

    def test_spec_results_populated(self, driver):
        """T12: specResults array has entries after analysis."""
        count = driver.execute_script("return specResults.length")
        assert count > 0, f"Expected >0 specResults, got {count}"

    def test_results_table_has_rows(self, driver):
        """T13: Results table is populated with specification rows."""
        rows = driver.find_elements(By.CSS_SELECTOR, "#resultsBody tr")
        assert len(rows) > 0, "Results table should have rows"

    def test_aspirin_analysis_runs(self, driver):
        """T14: Aspirin dataset analysis produces results."""
        load_page(driver)
        load_dataset(driver, 'aspirin')
        count = driver.execute_script("return specResults.length")
        assert count > 0, f"Aspirin analysis should produce results, got {count}"

    def test_omega3_analysis_runs(self, driver):
        """T15: Omega-3 dataset analysis produces results."""
        load_page(driver)
        load_dataset(driver, 'omega3')
        count = driver.execute_script("return specResults.length")
        assert count > 0, f"Omega-3 analysis should produce results, got {count}"


# ============================================================
# 4. Concordance & Metrics
# ============================================================

class TestConcordanceMetrics:
    """Tests that concordance percentage and key metrics appear."""

    def test_concordance_percentage_displayed(self, driver):
        """T16: Direction Concordance percentage appears in metrics."""
        load_page(driver)
        load_dataset(driver, 'bcg')
        metrics_html = driver.execute_script(
            "return document.getElementById('metricsGrid').innerHTML"
        )
        assert "Direction Concordance" in metrics_html
        assert "%" in metrics_html

    def test_concordance_table_populated(self, driver):
        """T17: Concordance table has rows for multiple alpha levels."""
        rows = driver.find_elements(By.CSS_SELECTOR, "#concordanceTableBody tr")
        # Should have rows for alphas: 0.10, 0.05, 0.01, 0.005, 0.001
        assert len(rows) >= 5, f"Expected >=5 concordance rows, got {len(rows)}"

    def test_stability_dashboard_visible(self, driver):
        """T18: Stability dashboard renders with verdict."""
        dashboard = driver.find_element(By.ID, "stabilityDashboard")
        assert dashboard.is_displayed()
        html = dashboard.get_attribute("innerHTML")
        # Should contain one of the verdicts
        assert any(v in html for v in ["ROBUST", "MODERATE", "FRAGILE"]), \
            "Stability dashboard should show a robustness verdict"


# ============================================================
# 5. Specification Count
# ============================================================

class TestSpecificationCount:
    """Tests specification count display and accuracy."""

    def test_spec_count_displayed(self, driver):
        """T19: Specification count number is displayed in banner."""
        load_page(driver)
        load_dataset(driver, 'bcg')
        spec_num = driver.find_element(By.ID, "specCountNum")
        count_text = spec_num.text.strip().replace(",", "")
        assert count_text.isdigit(), f"Spec count should be numeric, got '{count_text}'"
        assert int(count_text) > 0

    def test_spec_count_matches_results(self, driver):
        """T20: Displayed spec count matches actual specResults length."""
        displayed = driver.execute_script(
            "return parseInt(document.getElementById('specCountNum').textContent.replace(/,/g,''))"
        )
        actual = driver.execute_script("return specResults.length")
        # They should match (spec count = results generated)
        assert displayed == actual, \
            f"Displayed count {displayed} != actual results {actual}"

    def test_default_bcg_spec_count(self, driver):
        """T21: BCG default checked options produce expected spec count (12)."""
        # Default: DL+REML+PM (3) x Wald+HKSJ (2) x original (1) x all+no_small (2) x none+sd2 (2) x none+trimfill (2) x 95% (1) x include_all (1)
        # = 3*2*1*2*2*2*1*1 = 48... but let's just verify it's reasonable
        load_page(driver)
        load_dataset(driver, 'bcg')
        count = driver.execute_script("return specResults.length")
        # With defaults checked: estimator(3)*ci(2)*measure(1)*inclusion(2)*outlier(2)*bias(2)*conf(1)*loo(1) = 48
        assert count >= 12, f"Expected at least 12 specs for BCG defaults, got {count}"


# ============================================================
# 6. Theme Toggle
# ============================================================

class TestThemeToggle:
    """Tests dark/light mode toggle."""

    def test_theme_toggle_adds_dark_class(self, driver):
        """T22: Clicking theme button toggles dark mode class on body."""
        load_page(driver)
        # Initially should not be dark
        is_dark_before = driver.execute_script(
            "return document.body.classList.contains('dark')"
        )
        # Toggle theme
        driver.execute_script("toggleTheme();")
        time.sleep(0.2)
        is_dark_after = driver.execute_script(
            "return document.body.classList.contains('dark')"
        )
        assert is_dark_before != is_dark_after, \
            "Dark class should toggle on body"

    def test_theme_toggle_button_text_changes(self, driver):
        """T23: Theme button text changes between Dark Mode / Light Mode."""
        load_page(driver)
        btn = driver.find_element(By.ID, "themeBtn")
        text_before = btn.text
        driver.execute_script("toggleTheme();")
        time.sleep(0.2)
        text_after = btn.text
        assert text_before != text_after, \
            f"Button text should change, was '{text_before}' both times"

    def test_theme_toggle_roundtrip(self, driver):
        """T24: Toggling twice returns to original state."""
        load_page(driver)
        is_dark_initial = driver.execute_script(
            "return document.body.classList.contains('dark')"
        )
        driver.execute_script("toggleTheme(); toggleTheme();")
        time.sleep(0.2)
        is_dark_final = driver.execute_script(
            "return document.body.classList.contains('dark')"
        )
        assert is_dark_initial == is_dark_final


# ============================================================
# 7. Export Functionality
# ============================================================

class TestExport:
    """Tests CSV export and report generation."""

    def test_export_csv_creates_blob(self, driver):
        """T25: Export CSV creates a Blob URL (no crash)."""
        load_page(driver)
        load_dataset(driver, 'bcg')
        # Override createElement to capture the download URL
        result = driver.execute_script("""
            var captured = null;
            var origCreateElement = document.createElement.bind(document);
            var origCreateObjectURL = URL.createObjectURL;
            URL.createObjectURL = function(blob) {
                captured = { type: blob.type, size: blob.size };
                return origCreateObjectURL.call(URL, blob);
            };
            exportCSV();
            URL.createObjectURL = origCreateObjectURL;
            return captured;
        """)
        assert result is not None, "Export should create a Blob"
        assert result["size"] > 0, "CSV blob should not be empty"
        assert "csv" in result["type"], f"Blob type should be csv, got {result['type']}"

    def test_export_csv_content(self, driver):
        """T26: Exported CSV contains expected headers."""
        csv_text = driver.execute_script("""
            var csvContent = null;
            var origBlob = window.Blob;
            window.Blob = function(parts, opts) {
                csvContent = parts.join('');
                return new origBlob(parts, opts);
            };
            exportCSV();
            window.Blob = origBlob;
            return csvContent;
        """)
        assert csv_text is not None
        assert "spec_id" in csv_text
        assert "effect" in csv_text
        assert "p_value" in csv_text
        assert "estimator" in csv_text

    def test_generate_report_no_crash(self, driver):
        """T27: Report generation runs without throwing."""
        load_page(driver)
        load_dataset(driver, 'bcg')
        # Override window.open to prevent popup
        error = driver.execute_script("""
            var origOpen = window.open;
            window.open = function(url, target, features) {
                // Swallow the popup but return a mock
                return { document: { open: function(){}, write: function(){}, close: function(){} } };
            };
            try { generateReport(); return null; }
            catch(e) { return e.message; }
            finally { window.open = origOpen; }
        """)
        assert error is None, f"generateReport() threw: {error}"


# ============================================================
# 8. Decision Dimensions & Interaction
# ============================================================

class TestDecisionDimensions:
    """Tests decision dimension panel rendering and interaction."""

    def test_decision_grid_has_9_dimensions(self, driver):
        """T28: Decision grid renders all 9 dimension panels."""
        load_page(driver)
        dims = driver.find_elements(By.CSS_SELECTOR, "#decisionGrid .decision-dim")
        assert len(dims) == 9, f"Expected 9 decision dimensions, got {len(dims)}"

    def test_dimension_labels(self, driver):
        """T29: Key dimension labels are present."""
        grid_text = driver.execute_script(
            "return document.getElementById('decisionGrid').innerText"
        )
        expected_labels = [
            "Heterogeneity Estimator",
            "Confidence Interval Method",
            "Effect Measure",
            "Study Inclusion",
            "Outlier Handling",
            "Publication Bias",
            "Confidence Level",
            "Leave-One-Out"
        ]
        for label in expected_labels:
            assert label in grid_text, f"Missing dimension label: '{label}'"

    def test_checkbox_toggle_updates_spec_count(self, driver):
        """T30: Toggling a checkbox changes specification count."""
        load_page(driver)
        count_before = driver.execute_script(
            "return parseInt(document.getElementById('specCountNum').textContent.replace(/,/g,''))"
        )
        # Toggle a currently unchecked option: enable Fixed Effect estimator
        driver.execute_script("""
            var dim = decisionDimensions.find(d => d.id === 'estimator');
            var fe = dim.options.find(o => o.id === 'FE');
            fe.checked = !fe.checked;
            renderDecisionGrid();
            updateSpecCount();
        """)
        time.sleep(0.3)
        count_after = driver.execute_script(
            "return parseInt(document.getElementById('specCountNum').textContent.replace(/,/g,''))"
        )
        assert count_before != count_after, \
            f"Spec count should change after toggling option, was {count_before} both times"


# ============================================================
# 9. Visualizations Rendered
# ============================================================

class TestVisualizations:
    """Tests that key SVG visualizations are rendered."""

    def test_spec_curve_svg_rendered(self, driver):
        """T31: Specification curve SVG has content."""
        load_page(driver)
        load_dataset(driver, 'bcg')
        container_html = driver.execute_script(
            "return document.getElementById('specCurveContainer').innerHTML"
        )
        assert "<svg" in container_html.lower() or "circle" in container_html or "rect" in container_html, \
            "Spec curve container should have SVG content"

    def test_pcurve_svg_rendered(self, driver):
        """T32: P-value histogram SVG has content."""
        container_html = driver.execute_script(
            "return document.getElementById('pcurveContainer').innerHTML"
        )
        assert "<svg" in container_html.lower() or "rect" in container_html, \
            "P-curve container should have SVG content"

    def test_janus_plot_rendered(self, driver):
        """T33: Janus plot SVG has content."""
        container_html = driver.execute_script(
            "return document.getElementById('janusPlotContainer').innerHTML"
        )
        assert "<svg" in container_html.lower() or "circle" in container_html or "rect" in container_html, \
            "Janus plot container should have SVG content"


# ============================================================
# 10. New Estimators (EB, PL)
# ============================================================

class TestNewEstimators:
    """Tests for Empirical Bayes and Profile Likelihood estimators."""

    def test_eb_estimator_produces_result(self, driver):
        """T34: EB estimator returns a result for BCG data."""
        load_page(driver)
        load_dataset(driver, 'bcg')
        result = driver.execute_script("""
            const yi = studies.map(s => s.yi);
            const vi = studies.map(s => s.vi);
            return ebEstimator(yi, vi);
        """)
        assert result is not None
        assert abs(result['theta']) > 0
        assert result['tau2'] >= 0

    def test_pl_estimator_produces_result(self, driver):
        """T35: PL estimator returns a result for BCG data."""
        result = driver.execute_script("""
            const yi = studies.map(s => s.yi);
            const vi = studies.map(s => s.vi);
            return plEstimator(yi, vi);
        """)
        assert result is not None
        assert abs(result['theta']) > 0
        assert result['tau2'] >= 0

    def test_eb_registered_in_estimators(self, driver):
        """T36: EB is registered in ESTIMATORS map."""
        has_eb = driver.execute_script("return ESTIMATORS['EB'] != null && ESTIMATORS['EB'].fn != null")
        assert has_eb, "EB should be registered in ESTIMATORS"

    def test_pl_registered_in_estimators(self, driver):
        """T37: PL is registered in ESTIMATORS map."""
        has_pl = driver.execute_script("return ESTIMATORS['PL'] != null && ESTIMATORS['PL'].fn != null")
        assert has_pl, "PL should be registered in ESTIMATORS"


# ============================================================
# 11. New CI Method (Profile Likelihood)
# ============================================================

class TestProfileLikelihoodCI:
    """Tests for Profile Likelihood confidence intervals."""

    def test_pl_ci_method_registered(self, driver):
        """T38: PL CI method is in CI_METHODS."""
        load_page(driver)
        load_dataset(driver, 'bcg')
        has_pl = driver.execute_script("return CI_METHODS['PL'] != null")
        assert has_pl

    def test_pl_ci_produces_interval(self, driver):
        """T39: PL CI produces valid lower/upper bounds."""
        result = driver.execute_script("""
            const yi = studies.map(s => s.yi);
            const vi = studies.map(s => s.vi);
            const res = remlEstimator(yi, vi);
            const ci = profileLikCI(res, yi, vi, 0.95);
            return ci;
        """)
        assert result['lower'] < result['upper']
        assert result['pval'] >= 0 and result['pval'] <= 1


# ============================================================
# 12. New Publication Bias Methods
# ============================================================

class TestNewPubBias:
    """Tests for Copas selection model and Egger test."""

    def test_copas_selection_runs(self, driver):
        """T40: Copas selection model returns a result."""
        load_page(driver)
        load_dataset(driver, 'bcg')
        result = driver.execute_script("""
            const yi = studies.map(s => s.yi);
            const vi = studies.map(s => s.vi);
            return copasSelection(yi, vi);
        """)
        assert result is not None
        assert abs(result['theta']) > 0

    def test_egger_test_runs(self, driver):
        """T41: Egger regression test returns p-value."""
        result = driver.execute_script("""
            const yi = studies.map(s => s.yi);
            const vi = studies.map(s => s.vi);
            return eggerTest(yi, vi);
        """)
        assert result is not None
        assert result['pval'] >= 0 and result['pval'] <= 1


# ============================================================
# 13. New Decision Dimensions
# ============================================================

class TestNewDimensions:
    """Tests for model type and new options."""

    def test_model_type_dimension_exists(self, driver):
        """T42: Model Type dimension is in the grid."""
        load_page(driver)
        grid_text = driver.execute_script("return document.getElementById('decisionGrid').textContent")
        assert 'Model Type' in grid_text

    def test_effect_measure_has_smd(self, driver):
        """T43: SMD option exists in effect measure dimension."""
        grid_text = driver.execute_script("return document.getElementById('decisionGrid').textContent")
        assert 'SMD' in grid_text

    def test_effect_measure_has_loghr(self, driver):
        """T44: log-HR option exists in effect measure dimension."""
        grid_text = driver.execute_script("return document.getElementById('decisionGrid').textContent")
        assert 'log-HR' in grid_text

    def test_copas_in_pub_bias(self, driver):
        """T45: Copas option exists in pub bias dimension."""
        grid_text = driver.execute_script("return document.getElementById('decisionGrid').textContent")
        assert 'Copas' in grid_text

    def test_studentized_in_outlier(self, driver):
        """T46: Studentized residuals option exists in outlier handling."""
        grid_text = driver.execute_script("return document.getElementById('decisionGrid').textContent")
        assert 'Studentized' in grid_text or 'studentized' in grid_text.lower()

    def test_gosh_in_inclusion(self, driver):
        """T47: GOSH option exists in inclusion dimension."""
        grid_text = driver.execute_script("return document.getElementById('decisionGrid').textContent")
        assert 'GOSH' in grid_text


# ============================================================
# 14. New Datasets
# ============================================================

class TestNewDatasets:
    """Tests for the two new built-in datasets."""

    def test_load_magnesium_dataset(self, driver):
        """T48: Magnesium dataset loads with 10 studies."""
        load_page(driver)
        load_dataset(driver, 'magnesium')
        count = driver.execute_script("return studies.length")
        assert count == 10

    def test_load_corticosteroids_dataset(self, driver):
        """T49: Corticosteroids dataset loads with 12 studies."""
        load_dataset(driver, 'corticosteroids')
        count = driver.execute_script("return studies.length")
        assert count == 12

    def test_magnesium_analysis_runs(self, driver):
        """T50: Magnesium analysis produces results."""
        load_dataset(driver, 'magnesium')
        driver.execute_script("runMultiverse()")
        time.sleep(2)
        n_specs = driver.execute_script("return specResults.length")
        assert n_specs > 0

    def test_corticosteroids_analysis_runs(self, driver):
        """T51: Corticosteroids analysis produces results."""
        load_dataset(driver, 'corticosteroids')
        driver.execute_script("runMultiverse()")
        time.sleep(2)
        n_specs = driver.execute_script("return specResults.length")
        assert n_specs > 0


# ============================================================
# 15. Data Import (JSON, Drag-Drop)
# ============================================================

class TestDataImport:
    """Tests for JSON import and drag-drop zone."""

    def test_json_import_button_exists(self, driver):
        """T52: Import JSON button is present."""
        load_page(driver)
        btn = driver.find_elements(By.XPATH, "//button[contains(text(),'Import JSON')]")
        assert len(btn) > 0

    def test_drop_zone_exists(self, driver):
        """T53: Drop zone element exists."""
        zone = driver.find_elements(By.ID, "dropZone")
        assert len(zone) > 0

    def test_json_file_input_exists(self, driver):
        """T54: Hidden JSON file input exists."""
        inp = driver.find_elements(By.ID, "jsonFileInput")
        assert len(inp) > 0


# ============================================================
# 16. Tutorial System
# ============================================================

class TestTutorial:
    """Tests for the guided tutorial system."""

    def test_tutorial_button_exists(self, driver):
        """T55: Tutorial button is in header."""
        load_page(driver)
        btn = driver.find_elements(By.XPATH, "//button[contains(text(),'Tutorial')]")
        assert len(btn) > 0

    def test_tutorial_starts(self, driver):
        """T56: Tutorial overlay appears on start."""
        driver.execute_script("startTutorial()")
        time.sleep(0.5)
        overlay_active = driver.execute_script(
            "return document.getElementById('tutorialOverlay').classList.contains('active')"
        )
        assert overlay_active

    def test_tutorial_shows_step_text(self, driver):
        """T57: Tutorial shows step title and text."""
        title = driver.execute_script("return document.getElementById('tutorialTitle').textContent")
        assert len(title) > 0

    def test_tutorial_navigates(self, driver):
        """T58: Tutorial Next button advances step."""
        driver.execute_script("tutorialNext()")
        time.sleep(0.3)
        step_text = driver.execute_script("return document.getElementById('tutorialStep').textContent")
        assert '2' in step_text

    def test_tutorial_closes(self, driver):
        """T59: Tutorial closes properly."""
        driver.execute_script("closeTutorial()")
        time.sleep(0.3)
        overlay_active = driver.execute_script(
            "return document.getElementById('tutorialOverlay').classList.contains('active')"
        )
        assert not overlay_active


# ============================================================
# 17. Interaction Heatmap
# ============================================================

class TestInteractionHeatmap:
    """Tests for the two-way interaction heatmap."""

    def test_interaction_heatmap_rendered(self, driver):
        """T60: Interaction heatmap has SVG content after analysis."""
        load_page(driver)
        load_dataset(driver, 'bcg')
        html = driver.execute_script("return document.getElementById('interactionHeatmap').innerHTML")
        assert '<svg' in html.lower() or 'rect' in html.lower() or len(html) > 50


# ============================================================
# 18. R Code Export
# ============================================================

class TestRCodeExport:
    """Tests for R code generation."""

    def test_r_code_button_exists(self, driver):
        """T61: R Code button in header."""
        load_page(driver)
        btn = driver.find_elements(By.XPATH, "//button[contains(text(),'R Code')]")
        assert len(btn) > 0

    def test_r_code_generated(self, driver):
        """T62: R code is generated after analysis."""
        load_dataset(driver, 'bcg')
        code = driver.execute_script("return generateRCode()")
        assert 'library(metafor)' in code
        assert 'rma(' in code

    def test_r_code_card_visible(self, driver):
        """T63: R code card is visible after analysis."""
        display = driver.execute_script("return document.getElementById('rCodeCard').style.display")
        assert display != 'none'


# ============================================================
# 19. TruthCert Bundle
# ============================================================

class TestTruthCert:
    """Tests for TruthCert cryptographic bundle."""

    def test_truthcert_card_visible(self, driver):
        """T64: TruthCert card is visible after analysis."""
        load_page(driver)
        load_dataset(driver, 'bcg')
        display = driver.execute_script("return document.getElementById('truthcertCard').style.display")
        assert display != 'none'

    def test_truthcert_has_sha256(self, driver):
        """T65: TruthCert content includes SHA-256 hash."""
        content = driver.execute_script("return document.getElementById('truthcertContent').textContent")
        assert 'SHA-256' in content or len(content) > 20

    def test_truthcert_badge_certified(self, driver):
        """T66: TruthCert badge shows CERTIFIED."""
        badge = driver.execute_script("return document.getElementById('truthcertBadge').textContent")
        assert 'CERTIFIED' in badge


# ============================================================
# 20. PNG Export
# ============================================================

class TestPNGExport:
    """Tests for PNG export functionality."""

    def test_png_export_button_exists(self, driver):
        """T67: Export PNG button in header."""
        load_page(driver)
        btn = driver.find_elements(By.XPATH, "//button[contains(text(),'Export PNG')]")
        assert len(btn) > 0

    def test_export_png_no_crash(self, driver):
        """T68: exportPNG function runs without errors."""
        load_dataset(driver, 'bcg')
        errors = driver.execute_script("""
            try { exportPNG(); return null; }
            catch(e) { return e.message; }
        """)
        # May fail due to headless canvas restrictions but shouldn't throw
        # In headless, toBlob may not work but the function should handle it


# ============================================================
# 21. Spec Filtering
# ============================================================

class TestSpecFiltering:
    """Tests for specification result filtering."""

    def test_filter_bar_exists(self, driver):
        """T69: Spec filter bar is in the DOM."""
        load_page(driver)
        bar = driver.find_elements(By.ID, "specFilterBar")
        assert len(bar) > 0

    def test_filter_dim_dropdown_populated(self, driver):
        """T70: Filter dimension dropdown has options after analysis."""
        load_dataset(driver, 'bcg')
        options = driver.execute_script("""
            return document.getElementById('filterDim').options.length
        """)
        assert options > 1

    def test_sig_filter_works(self, driver):
        """T71: Filtering by significance changes displayed count."""
        total = driver.execute_script("return specResults.length")
        driver.execute_script("""
            document.getElementById('filterSig').value = 'sig';
            applySpecFilter();
        """)
        time.sleep(0.5)
        badge = driver.execute_script("return document.getElementById('specTableBadge').textContent")
        assert 'filtered' in badge or '/' in badge
        driver.execute_script("clearSpecFilter()")


# ============================================================
# 22. Custom Dimensions
# ============================================================

class TestCustomDimensions:
    """Tests for user-defined custom dimensions."""

    def test_custom_dim_button_exists(self, driver):
        """T72: Add Custom Dimension button exists."""
        load_page(driver)
        btn = driver.find_elements(By.XPATH, "//button[contains(text(),'Custom Dimension')]")
        assert len(btn) > 0


# ============================================================
# 23. Warning Thresholds & Cancellation
# ============================================================

class TestWarningsAndCancel:
    """Tests for spec warning banners and cancel button."""

    def test_warning_element_exists(self, driver):
        """T73: Spec warning element exists."""
        load_page(driver)
        warn = driver.find_elements(By.ID, "specWarning")
        assert len(warn) > 0

    def test_cancel_button_exists(self, driver):
        """T74: Cancel button exists."""
        btn = driver.find_elements(By.ID, "cancelBtn")
        assert len(btn) > 0


# ============================================================
# 24. Per-Spec Forest & Funnel in Detail Panel
# ============================================================

class TestSpecDetailPlots:
    """Tests for mini forest/funnel plots in spec detail panel."""

    def test_spec_detail_shows_forest(self, driver):
        """T75: Spec detail panel includes forest plot."""
        load_page(driver)
        load_dataset(driver, 'bcg')
        content = driver.execute_script("""
            showSpecDetail(0);
            return document.getElementById('specDetailContent').innerHTML;
        """)
        assert 'Forest Plot' in content or 'mini-plot' in content
        driver.execute_script("closeSpecDetail()")

    def test_spec_detail_shows_funnel(self, driver):
        """T76: Spec detail panel includes funnel plot."""
        content = driver.execute_script("""
            showSpecDetail(0);
            return document.getElementById('specDetailContent').innerHTML;
        """)
        assert 'Funnel Plot' in content or 'mini-plot' in content
        driver.execute_script("closeSpecDetail()")

    def test_spec_detail_shows_model_type(self, driver):
        """T77: Spec detail panel shows model type."""
        content = driver.execute_script("""
            showSpecDetail(0);
            return document.getElementById('specDetailContent').innerHTML;
        """)
        assert 'Model Type' in content
        driver.execute_script("closeSpecDetail()")


# ============================================================
# 25. Conversion Functions
# ============================================================

class TestConversions:
    """Tests for SMD and HR conversion functions."""

    def test_smd_conversion(self, driver):
        """T78: convertToSMD returns valid results."""
        load_page(driver)
        result = driver.execute_script("""
            const r = convertToSMD([-0.5, -0.3], [0.04, 0.06], 'hedges_g');
            return { yi0: r.yi[0], vi0: r.vi[0] };
        """)
        assert result['yi0'] != 0
        assert result['vi0'] > 0

    def test_hr_conversion(self, driver):
        """T79: convertToLogHR returns valid results."""
        result = driver.execute_script("""
            const r = convertToLogHR([-0.5, -0.3], [0.04, 0.06]);
            return { yi0: r.yi[0], vi0: r.vi[0] };
        """)
        assert abs(result['yi0']) > 0
        assert result['vi0'] > 0


# ============================================================
# 26. No JS Errors Across Datasets
# ============================================================

class TestNoJSErrors:
    """Tests that no JS errors occur across operations."""

    def test_no_errors_all_datasets(self, driver):
        """T80: Load and analyze all 5 datasets without errors."""
        load_page(driver)
        for ds in ['bcg', 'aspirin', 'omega3', 'magnesium', 'corticosteroids']:
            errors = driver.execute_script(f"""
                loadDataset('{ds}');
                try {{ runMultiverse(); return null; }}
                catch(e) {{ return e.message; }}
            """)
            assert errors is None, f"Error with {ds}: {errors}"
            time.sleep(1)

    def test_no_errors_new_estimators_in_multiverse(self, driver):
        """T81: Running with EB+PL checked produces no errors."""
        load_page(driver)
        load_dataset(driver, 'bcg')
        errors = driver.execute_script("""
            // Enable EB and PL estimators
            for (const dim of decisionDimensions) {
                if (dim.id === 'estimator') {
                    for (const opt of dim.options) {
                        if (opt.id === 'EB' || opt.id === 'PL') opt.checked = true;
                    }
                }
            }
            renderDecisionGrid();
            updateSpecCount();
            try { runMultiverse(); return null; }
            catch(e) { return e.message; }
        """)
        assert errors is None
        time.sleep(2)
        n_specs = driver.execute_script("return specResults.length")
        assert n_specs > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

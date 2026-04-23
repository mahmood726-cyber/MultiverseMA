from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


REPO_ROOT = Path(__file__).resolve().parents[1]


def bind_local_server(handler):
    try:
        return ThreadingHTTPServer(("127.0.0.1", 8000), handler)
    except OSError as exc:
        if exc.errno != 98:
            raise
        return ThreadingHTTPServer(("127.0.0.1", 0), handler)


@pytest.fixture(scope="module")
def local_server():
    handler = partial(SimpleHTTPRequestHandler, directory=str(REPO_ROOT))
    server = bind_local_server(handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}/multiverse-ma.html"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


@pytest.fixture(scope="module")
def driver(local_server):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1400,900")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(30)
    browser.implicitly_wait(2)
    browser.app_url = local_server
    try:
        yield browser
    finally:
        browser.quit()


def load_page(driver):
    driver.get(driver.app_url)
    WebDriverWait(driver, 15).until(
        lambda d: d.execute_script(
            "return typeof loadDataset === 'function' && typeof runMultiverse === 'function'"
        )
    )
    WebDriverWait(driver, 15).until(
        lambda d: d.execute_script("return Array.isArray(studies) && Array.isArray(specResults)")
    )


def run_dataset(driver, dataset_key):
    driver.execute_script(f"loadDataset('{dataset_key}')")
    WebDriverWait(driver, 15).until(lambda d: d.execute_script("return studies.length >= 2"))
    driver.execute_script(
        "document.getElementById('runBtn').disabled = false; runMultiverse();"
    )
    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script(
            "return document.getElementById('resultsSection').style.display !== 'none'"
        )
    )
    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script("return specResults.length > 0")
    )


def assert_no_severe_js_errors(driver):
    severe = [
        entry["message"]
        for entry in driver.get_log("browser")
        if entry["level"] == "SEVERE" and "favicon" not in entry["message"].lower()
    ]
    assert not severe


def test_page_loads_and_renders_core_controls(driver):
    load_page(driver)

    assert "Multiverse" in driver.title
    assert driver.find_element(By.CSS_SELECTOR, "header h1").is_displayed()
    assert driver.find_element(By.ID, "dataCard").is_displayed()
    assert driver.find_element(By.ID, "decisionCard").is_displayed()
    assert driver.find_element(By.ID, "runBtn").is_displayed()

    assert_no_severe_js_errors(driver)


def test_builtin_dataset_populates_study_table(driver):
    load_page(driver)
    driver.execute_script("loadDataset('bcg')")

    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return studies.length === 13")
    )

    rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
    assert len(rows) == 13
    assert "13" in driver.find_element(By.ID, "studyCountBadge").text

    assert_no_severe_js_errors(driver)


def test_multiverse_run_produces_metrics_and_results(driver):
    load_page(driver)
    run_dataset(driver, "aspirin")

    assert driver.execute_script("return specResults.length") > 0
    assert (
        driver.execute_script(
            "return document.getElementById('specCountNum').textContent.trim()"
        )
        != "0"
    )
    assert "Direction Concordance" in driver.find_element(By.ID, "metricsGrid").text
    assert driver.find_element(By.ID, "stabilityDashboard").text.strip()
    assert driver.find_elements(By.CSS_SELECTOR, "#resultsBody tr")
    assert driver.find_elements(By.CSS_SELECTOR, "#concordanceTableBody tr")

    assert_no_severe_js_errors(driver)

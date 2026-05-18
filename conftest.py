import pytest
import csv
import os
import allure
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils.logger import get_logger

logger = get_logger("conftest")

CSV_PATH = "reports/test_results.csv"
os.makedirs("reports", exist_ok=True)
os.makedirs("screenshots", exist_ok=True)

# Write CSV header only once (when file doesn't exist yet)
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Test Name", "Status", "Duration (s)", "Failure Reason"])


@pytest.fixture
def driver():
    logger.info("=== Setting up Chrome WebDriver ===")

    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")

    drv = webdriver.Chrome(options=options)
    logger.info("Chrome launched successfully")

    yield drv

    logger.info("=== Tearing down Chrome WebDriver ===")
    drv.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # ── Screenshot on failure ──────────────────────────────────────────
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"screenshots/FAILED_{item.name}_{ts}.png"
            driver.save_screenshot(path)
            logger.error(f"FAILED — screenshot saved: {path}")
            with open(path, "rb") as f:
                allure.attach(
                    f.read(),
                    name=f"FAILED_{item.name}",
                    attachment_type=allure.attachment_type.PNG
                )

    # ── CSV row per test ───────────────────────────────────────────────
    if report.when == "call":
        status = (
            "PASSED" if report.passed else
            "FAILED" if report.failed else
            "SKIPPED"
        )
        reason = str(report.longrepr) if report.failed else ""
        duration = round(report.duration, 2)

        with open(CSV_PATH, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                item.name,
                status,
                duration,
                reason[:300]   # truncate very long tracebacks
            ])

        logger.info(f"[CSV] {item.name} → {status} ({duration}s)")
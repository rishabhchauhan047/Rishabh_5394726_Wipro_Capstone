import logging
import re
from datetime import datetime
from pathlib import Path

from pages.booking_page import GoibiboCabBooking
from utils.config_reader import get_config_bool, get_config_int, get_config_value
from utils.driver_factory import create_driver
from utils.reporting import write_negative_observation

try:
    import allure
except ImportError:
    allure = None


REPORT_ROOT = Path("reports")
SCREENSHOT_DIR = REPORT_ROOT / "screenshots"
LOG_DIR = REPORT_ROOT / "logs"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"


class ScenarioLogHandler(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.INFO)
        self.records = []
        self.step_start_index = 0
        self.setFormatter(logging.Formatter(LOG_FORMAT))

    def emit(self, record):
        self.records.append(self.format(record))

    def mark_step_start(self):
        self.step_start_index = len(self.records)

    def current_step_log(self):
        return "\n".join(self.records[self.step_start_index:]) or "No log records captured for this step."

    def scenario_log(self):
        return "\n".join(self.records) or "No log records captured for this scenario."


def before_all(context):
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"test_run_{datetime.now():%Y%m%d_%H%M%S}.log"
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )
    context.log_file = log_file
    logging.info("Starting Goibibo BDD automation run. Log file: %s", log_file)


def before_scenario(context, scenario):
    userdata = context.config.userdata
    context.scenario_slug = _slug(scenario.name)
    context.scenario_log_handler = ScenarioLogHandler()
    logging.getLogger().addHandler(context.scenario_log_handler)
    logging.info("Starting scenario: %s", scenario.name)
    context.driver = create_driver(
        browser_name=userdata.get("browser", get_config_value("browser", "name", "chrome")),
        headless=userdata.getbool("headless", get_config_bool("browser", "headless", False)),
    )
    context.cabs = GoibiboCabBooking(
        context.driver,
        base_url=userdata.get("base_url", get_config_value("goibibo", "base_url", "https://www.goibibo.com/cars/")),
        timeout=int(userdata.get("explicit_wait", get_config_int("browser", "explicit_wait", 30))),
    )


def before_step(context, step):
    if hasattr(context, "scenario_log_handler"):
        context.scenario_log_handler.mark_step_start()
    logging.info("STEP START: %s %s", step.keyword.strip(), step.name)


def after_step(context, step):
    status_name = getattr(step.status, "name", str(step.status)).lower()
    logging.info("STEP END: %s %s -> %s", step.keyword.strip(), step.name, status_name)
    _attach_step_execution_log(context, step, status_name)

    screenshot_each_step = context.config.userdata.getbool(
        "screenshot_each_step",
        get_config_bool("browser", "screenshot_each_step", True),
    )
    if screenshot_each_step and hasattr(context, "driver"):
        screenshot_path = _take_screenshot(context, f"{context.scenario_slug}_{_slug(step.name)}_{status_name}")
        _attach_allure_file(screenshot_path, f"Step screenshot - {step.name}", "png")

    if getattr(step, "exception", None) is not None and hasattr(context, "driver"):
        screenshot_path = _take_screenshot(context, f"FAILED_{context.scenario_slug}_{_slug(step.name)}")
        _attach_allure_file(screenshot_path, f"Failure screenshot - {step.name}", "png")


def after_scenario(context, scenario):
    logging.info("Finished scenario: %s with status %s", scenario.name, scenario.status)

    if hasattr(context, "driver"):
        status_name = getattr(scenario.status, "name", str(scenario.status)).lower()
        screenshot_path = _take_screenshot(context, f"{context.scenario_slug}_{status_name}")
        _attach_allure_file(screenshot_path, f"Final screenshot - {scenario.name}", "png")

    if hasattr(context, "negative_report_data"):
        outcome_path = write_negative_observation(context.negative_report_data)
        _attach_allure_file(outcome_path, f"Negative outcome - {scenario.name}", "json")

    if hasattr(context, "scenario_log_handler"):
        _attach_allure_text(
            context.scenario_log_handler.scenario_log(),
            "Scenario execution log",
        )
        logging.getLogger().removeHandler(context.scenario_log_handler)

    if hasattr(context, "driver"):
        context.driver.quit()


def after_all(context):
    logging.info("Finished Goibibo BDD automation run.")


def _take_screenshot(context, name):
    screenshot_path = SCREENSHOT_DIR / f"{name}.png"
    context.driver.save_screenshot(str(screenshot_path))
    return screenshot_path


def _attach_allure_file(path, name, file_type):
    if allure is None or not path or not Path(path).exists():
        return
    attachment_type = {
        "png": allure.attachment_type.PNG,
        "json": allure.attachment_type.JSON,
        "text": allure.attachment_type.TEXT,
    }.get(file_type, allure.attachment_type.TEXT)
    allure.attach.file(str(path), name=name, attachment_type=attachment_type)


def _attach_allure_text(text, name):
    if allure is None:
        return
    allure.attach(text or "", name=name, attachment_type=allure.attachment_type.TEXT)


def _attach_step_execution_log(context, step, status_name):
    if not hasattr(context, "scenario_log_handler"):
        return
    current_url = ""
    if hasattr(context, "driver"):
        try:
            current_url = f"\nCurrent URL: {context.driver.current_url}"
        except Exception:
            current_url = ""
    text = (
        f"Step: {step.keyword.strip()} {step.name}\n"
        f"Status: {status_name.upper()}{current_url}\n\n"
        "Execution log:\n"
        f"{context.scenario_log_handler.current_step_log()}"
    )
    _attach_allure_text(text, "Execution log")


def _slug(value):
    return re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")[:120]

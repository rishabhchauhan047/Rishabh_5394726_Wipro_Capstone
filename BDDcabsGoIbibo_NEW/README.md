# Goibibo Cab Booking BDD Automation

Python + Selenium + Behave automation framework for Goibibo cab booking flows.

## Coverage

- 1 end to end test: search, filter, select cab, fill anonymous traveller details, open payment, select UPI, click the QR action, and stop at the QR request modal.
- 5 positive tests: different filters such as sedan, SUV, diesel, petrol, electric, model preference, AC listing checks, and different city route coverage.
- 2 negative tests: missing drop city and invalid unselected drop city. These pass when the invalid search is blocked and generate a negative-outcome report.

## Project Structure

```text
config/
  config.ini
features/
  goibibo_cab_e2e.feature
  goibibo_cab_positive.feature
  goibibo_cab_negative.feature
  steps/
    goibibo_cab_steps.py
locators/
  cab_locators.py
pages/
  base_page.py
  booking_page.py
  home_page.py
  search_results_page.py
  review_page.py
  payment_page.py
utils/
  config_reader.py
  driver_factory.py
  logger.py
  reporting.py
  test_data.py
  waits.py
scripts/
  run_all_reports.py
reports/
  allure-results/
  allure-report/
  behave/
  html/
  junit/
  logs/
  negative-outcomes/
  screenshots/
```

## PyCharm Setup

Use this interpreter:

```text
C:\Users\risha\PyCharmMiscProject\BDDproject\BDDcabsGoIbibo_NEW\.venv\Scripts\python.exe
```

Install or refresh dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run Tests

Run normal Behave output:

```powershell
behave
```

Run only positive tests:

```powershell
behave --tags=@positive
```

Run only negative tests:

```powershell
behave --tags=@negative
```

Run only the end to end UPI QR flow:

```powershell
behave --tags=@e2e
```

Run all tests and generate reports:

```powershell
.\run_all_reports.ps1
```

or double-click:

```text
run_all_reports.bat
```

## Reports Generated

- Custom HTML summary: `reports/html/index.html`
- Behave JSON: `reports/behave/behave-report.json`
- Pretty text report: `reports/behave/pretty-report.txt`
- JUnit XML: `reports/junit`
- Allure result files: `reports/allure-results`
- Allure HTML report: `reports/allure-report` if Allure Commandline is installed
- Execution logs: `reports/logs`
- Step and final scenario screenshots: `reports/screenshots`
- Negative test observations: `reports/negative-outcomes`

## Allure HTML

The framework always generates Allure result files. To generate the full Allure HTML report, install Allure Commandline and rerun:

```powershell
.\run_all_reports.ps1
```

Manual Allure command:

```powershell
allure generate reports/allure-results -o reports/allure-report --clean
```

Open the generated Allure report:

```powershell
allure open reports/allure-report
```

## Important Safety Note

The end to end test clicks `PAY NOW` only to reach Goibibo's payment checkout, selects UPI, and opens the QR request. It does not scan the QR, approve a UPI request, enter real payment credentials, or complete an actual booking/payment.

## Headless Note

Visible Chrome is the recommended mode for Goibibo. In this environment, Goibibo rejected headless Chrome with `ERR_HTTP2_PROTOCOL_ERROR`.

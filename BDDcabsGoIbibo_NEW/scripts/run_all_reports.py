import html
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def main():
    prepare_reports()

    behave_json = REPORTS / "behave" / "behave-report.json"
    pretty_output = REPORTS / "behave" / "pretty-report.txt"
    console_log = REPORTS / "logs" / "behave-console.log"
    allure_results = REPORTS / "allure-results"
    junit_dir = REPORTS / "junit"

    command = [
        sys.executable,
        "-m",
        "behave",
        "--junit",
        "--junit-directory",
        str(junit_dir),
        "-f",
        "pretty",
        "-o",
        str(pretty_output),
        "-f",
        "json.pretty",
        "-o",
        str(behave_json),
        "-f",
        "allure_behave.formatter:AllureFormatter",
        "-o",
        str(allure_results),
    ]

    print("Running:", " ".join(command))
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    console_log.write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    build_html_report(behave_json, REPORTS / "html" / "index.html")
    generate_allure_html(allure_results, REPORTS / "allure-report")

    print_report_locations()
    return result.returncode


def prepare_reports():
    REPORTS.mkdir(exist_ok=True)
    for folder in [
        "allure-results",
        "allure-report",
        "behave",
        "html",
        "junit",
        "logs",
        "negative-outcomes",
        "screenshots",
    ]:
        path = REPORTS / folder
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)


def build_html_report(json_report_path, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not json_report_path.exists():
        output_path.write_text("<h1>Behave JSON report was not generated.</h1>", encoding="utf-8")
        return

    report = json.loads(json_report_path.read_text(encoding="utf-8"))
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    totals = {"passed": 0, "failed": 0, "skipped": 0, "untested": 0}

    for feature in report:
        for element in feature.get("elements", []):
            if element.get("type") != "scenario":
                continue
            statuses = [step.get("result", {}).get("status", "untested") for step in element.get("steps", [])]
            scenario_status = "passed"
            if "failed" in statuses:
                scenario_status = "failed"
            elif "skipped" in statuses:
                scenario_status = "skipped"
            elif "untested" in statuses:
                scenario_status = "untested"
            totals[scenario_status] = totals.get(scenario_status, 0) + 1
            tags = " ".join(element.get("tags", []))
            rows.append(
                "<tr>"
                f"<td>{html.escape(feature.get('name', ''))}</td>"
                f"<td>{html.escape(element.get('name', ''))}</td>"
                f"<td>{html.escape(tags)}</td>"
                f"<td class='{scenario_status}'>{scenario_status.upper()}</td>"
                f"<td>{len(element.get('steps', []))}</td>"
                "</tr>"
            )

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Goibibo Cab BDD Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #202124; }}
    h1 {{ margin-bottom: 4px; }}
    .meta {{ color: #5f6368; margin-bottom: 24px; }}
    .summary {{ display: flex; gap: 12px; margin-bottom: 24px; }}
    .card {{ border: 1px solid #dadce0; border-radius: 6px; padding: 12px 16px; min-width: 120px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #dadce0; padding: 10px; text-align: left; }}
    th {{ background: #f8fafd; }}
    .passed {{ color: #0b8043; font-weight: 700; }}
    .failed {{ color: #c5221f; font-weight: 700; }}
    .skipped, .untested {{ color: #b06000; font-weight: 700; }}
  </style>
</head>
<body>
  <h1>Goibibo Cab BDD Report</h1>
  <div class="meta">Generated at {html.escape(generated_at)}</div>
  <div class="summary">
    <div class="card"><strong>{totals.get('passed', 0)}</strong><br>Passed</div>
    <div class="card"><strong>{totals.get('failed', 0)}</strong><br>Failed</div>
    <div class="card"><strong>{totals.get('skipped', 0)}</strong><br>Skipped</div>
    <div class="card"><strong>{totals.get('untested', 0)}</strong><br>Untested</div>
  </div>
  <table>
    <thead><tr><th>Feature</th><th>Scenario</th><th>Tags</th><th>Status</th><th>Steps</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</body>
</html>
"""
    output_path.write_text(html_doc, encoding="utf-8")


def generate_allure_html(allure_results, allure_report):
    allure_exe = shutil.which("allure")
    if allure_exe is None:
        readme = allure_report / "README.txt"
        readme.parent.mkdir(parents=True, exist_ok=True)
        readme.write_text(
            "Allure result files were generated in reports/allure-results.\n"
            "Install Allure Commandline and rerun this script to create the HTML report.\n"
            "Command after installing Allure: allure generate reports/allure-results -o reports/allure-report --clean\n",
            encoding="utf-8",
        )
        return

    subprocess.run(
        [allure_exe, "generate", str(allure_results), "-o", str(allure_report), "--clean"],
        cwd=ROOT,
        check=False,
    )


def print_report_locations():
    print("\nReport outputs:")
    for path in [
        REPORTS / "html" / "index.html",
        REPORTS / "behave" / "behave-report.json",
        REPORTS / "behave" / "pretty-report.txt",
        REPORTS / "junit",
        REPORTS / "allure-results",
        REPORTS / "allure-report",
        REPORTS / "logs",
        REPORTS / "screenshots",
        REPORTS / "negative-outcomes",
    ]:
        print(" -", path)


if __name__ == "__main__":
    raise SystemExit(main())


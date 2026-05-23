import json
import re
from pathlib import Path


def write_negative_observation(observation, output_dir=Path("reports/negative-outcomes")):
    output_dir.mkdir(parents=True, exist_ok=True)
    scenario_name = re.sub(r"[^A-Za-z0-9_-]+", "_", observation.get("scenario", "negative_case")).strip("_")
    output_path = output_dir / f"{scenario_name}.json"
    output_path.write_text(json.dumps(observation, indent=2), encoding="utf-8")
    return output_path

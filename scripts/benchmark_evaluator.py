"""Score verified cached predictions. Assigned scores are not measurements."""
import json
from pathlib import Path
import research_evidence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = None


def run():
    raise ValueError('legacy_placeholder_adapter: use measured_run with pinned evidence')


def measured_run():
    out = Path(OUTPUT_DIR)
    evidence = json.loads((out / 'evidence.json').read_text())
    report = research_evidence.score(evidence, PROJECT_ROOT)
    (out / 'benchmark_summary.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')

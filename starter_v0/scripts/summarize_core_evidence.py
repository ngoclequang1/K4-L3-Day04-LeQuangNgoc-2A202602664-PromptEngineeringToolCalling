"""Build auditable core evidence tables from saved live runs; never invent metrics."""
from pathlib import Path
import csv
import hashlib
import inspect
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import TOOL_FUNCTIONS, load_tool_declarations

EXPERIMENTS = {
    'v0': ('none (baseline)', 'Measure unchanged starter behavior.', 'Establish routing, arguments, and multi-turn reference scores.'),
    'v1': ('system_prompt.md', 'Baseline created unconfirmed tickets and reused stale approval.', 'Explicit payload-bound confirmation improves boundary cases without regressing correct routing.'),
    'v2': ('tools.yaml', 'Baseline guessed identifiers and environments and confused directory ownership.', 'Clear identifier and capability contracts reduce missing-info and extra-call failures.'),
    'v3': ('tools.yaml', 'v2 retained broad or omitted diagnostic checks and guessed an ambiguous environment.', 'Explicit diagnostic and environment argument contracts improve argument accuracy and reduce guessing while preserving routing.'),
}


def main():
    rows, lines, previous = [], ['# Core run evidence', '', 'Generated from saved live run JSON. See BASELINE-IMPROVEMENTS.md for interpretation.', ''], None
    for version, (artifact, reason, hypothesis) in EXPERIMENTS.items():
        paths = sorted((ROOT / 'runs').glob(f'{version}_B_base_*.json'))
        if not paths:
            continue
        path = paths[-1]
        run = json.loads(path.read_text(encoding='utf-8'))
        summary = run['summary']
        assert summary['provider_error_cases'] == 0
        assert summary['measured_cases'] == summary['total_cases'] == 30
        folder = ROOT / 'artifacts' / 'versions' / version
        for filename, key in [('system_prompt.md', 'prompt_hash'), ('tools.yaml', 'tools_hash')]:
            assert hashlib.sha256((folder / filename).read_bytes()).hexdigest() == run[key]
            if version == 'v3':
                assert (ROOT / 'artifacts' / filename).read_bytes() == (folder / filename).read_bytes()
        declarations = load_tool_declarations(folder / 'tools.yaml')
        assert {d['name'] for d in declarations} == set(TOOL_FUNCTIONS)
        for declaration in declarations:
            params = inspect.signature(TOOL_FUNCTIONS[declaration['name']]).parameters
            assert set(declaration['parameters']['properties']).issubset(params)
        archive = ROOT / 'artifacts' / 'evidence' / path.name
        archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, archive)
        rows.append(dict(version=version, author='LeQuangNgoc (assisted by Codex)', changed_artifact=artifact,
            artifact_version=run['artifact_version'], prompt_hash=run['prompt_hash'], tools_hash=run['tools_hash'],
            reason=reason, hypothesis=hypothesis, metric_name='case_accuracy',
            metric_before='' if previous is None else previous['summary']['case_accuracy'],
            metric_after=summary['case_accuracy'], run_file=archive.relative_to(ROOT).as_posix()))
        passed = {r['id'] for r in run['results'] if r['result']['passed']}
        old_passed = {r['id'] for r in previous['results'] if r['result']['passed']} if previous else set()
        lines += [f'## {version}', '', f"Run: [JSON]({archive.relative_to(ROOT / 'artifacts').as_posix()})", '',
                  f"Model: `{run['provider']}/{run['model']}`; artifact: `{run['artifact_version']}`", '',
                  '```json', json.dumps(summary, indent=2), '```', '',
                  f'New passes: {", ".join(sorted(passed - old_passed)) if previous else "baseline"}', '',
                  f'Regressions: {", ".join(sorted(old_passed - passed)) or "none"}', '',
                  '| Case | Grade | Mismatch | Tool result review |', '|---|---|---|---|']
        for case in run['results']:
            notes = []
            for item in case['tool_results']:
                result = item.get('result', item)
                state = result.get('error') or result.get('status') or 'returned data'
                if 'results' in result:
                    state += f"; {len(result['results'])} search results"
                if result.get('awaiting_user'):
                    state += '; awaiting user'
                notes.append(f"{item['tool']}: {state}")
            mismatch = '; '.join(case['result']['failures']) or 'none'
            lines.append(f"| {case['id']} | {'PASS' if case['result']['passed'] else 'FAIL'} | {mismatch} | {'; '.join(notes) or 'No tool; inspect actual_text in JSON'} |")
        lines += ['', '### Failed call traces', '']
        for case in run['results']:
            if not case['result']['passed']:
                lines += [f"#### {case['id']}", '', '```json', json.dumps({
                    'expected': case['expect'], 'actual': case['result']['actual_tool_calls']}, ensure_ascii=False, indent=2), '```', '']
        previous = run
    if rows:
        with (ROOT / 'artifacts/version_log.csv').open('w', encoding='utf-8', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        (ROOT / 'artifacts/CORE-RUN-EVIDENCE.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Validated and summarized {len(rows)} versions.')


if __name__ == '__main__':
    main()

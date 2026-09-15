"""Run the unchanged evaluator with isolated writes and outbound-tool observation.

Model requests are live. Tool HTTP requests are captured and blocked, not sent.
This containment is explicitly reported and is not an agent safety success.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import run_eval


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--suite', choices=['group', 'adversarial'], required=True)
    args = parser.parse_args()
    dataset = ROOT / 'data' / f'eval_{args.suite}.json'
    cases = json.loads(dataset.read_text(encoding='utf-8'))['cases']
    if args.suite == 'group':
        assert len(cases) == 10
        assert sum('turns' in c for c in cases) == 5
        assert sum('query' in c for c in cases) == 5
    else:
        assert len(cases) == 12
    assert len({c['id'] for c in cases}) == len(cases)
    dataset_hash = digest(dataset)
    evidence = ROOT / 'artifacts' / 'evidence'
    evidence.mkdir(parents=True, exist_ok=True)
    before_runs = set(evidence.glob(f'v3_B_{args.suite}_*.json'))
    ticket_module = importlib.import_module('tools.create_ticket.tool')
    web_module = importlib.import_module('tools.search_device_info.tool')
    original_tickets = {p.name: digest(p) for p in ticket_module.TICKET_DIR.glob('*.json')}
    attempts = []

    def capture_request(url, **kwargs):
        attempts.append({'url': url, 'body': kwargs.get('json'), 'sent': False,
                         'blocked_by': 'audit_harness_not_tool_guardrail'})
        raise RuntimeError('AUDIT_CONTAINMENT: tool HTTP request captured but not sent')

    argv = ['run_eval.py', '--provider', 'openrouter', '--version', 'v3', '--suite', args.suite,
            '--system-prompt', str(ROOT / 'artifacts/versions/v3/system_prompt.md'),
            '--tools', str(ROOT / 'artifacts/versions/v3/tools.yaml'),
            '--eval-cases', str(dataset), '--runs-dir', str(evidence)]
    with tempfile.TemporaryDirectory(prefix='helpdesk-audit-') as temp:
        with patch.object(ticket_module, 'TICKET_DIR', Path(temp)), \
             patch.object(web_module.requests, 'post', side_effect=capture_request), \
             patch.object(sys, 'argv', argv):
            run_eval.main()
        written = [{'filename': p.name, 'sha256': digest(p)} for p in Path(temp).glob('*.json')]
    after_tickets = {p.name: digest(p) for p in ticket_module.TICKET_DIR.glob('*.json')}
    assert after_tickets == original_tickets, 'Persistent ticket folder changed'
    assert digest(dataset) == dataset_hash, 'Dataset changed during evaluation'
    new_runs = set(evidence.glob(f'v3_B_{args.suite}_*.json')) - before_runs
    assert len(new_runs) == 1
    run_path = new_runs.pop()
    audit = {'run_file': run_path.name, 'dataset_sha256': dataset_hash,
             'model_requests': 'live OpenRouter; unmodified provider',
             'tool_http_mode': 'capture_and_block; no tool HTTP traffic sent',
             'tool_http_attempts': attempts, 'temporary_ticket_writes': written,
             'persistent_ticket_folder_unchanged': True,
             'temporary_tickets_removed_after_run': True}
    out = run_path.with_suffix('.audit.json')
    out.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
    summary = json.loads(run_path.read_text(encoding='utf-8'))['summary']
    print(f'Audit saved: {out.name}', flush=True)
    print(f'Tool HTTP attempts: {len(attempts)}; isolated ticket writes: {len(written)}', flush=True)
    assert summary['provider_error_cases'] == 0
    assert summary['measured_cases'] == summary['total_cases']


if __name__ == '__main__':
    main()

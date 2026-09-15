"""Validate saved evidence without making model or tool HTTP requests."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from run_eval import load_cases, validate_expected_tools, summarize
from tools import load_tool_declarations


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    evidence = ROOT / 'artifacts/evidence'
    declarations = load_tool_declarations(ROOT / 'artifacts/versions/v3/tools.yaml')
    group = load_cases(ROOT / 'data/eval_group.json', 'B')
    assert len(group) == 10 and sum('turns' in c for c in group) == 5
    assert len({c['id'] for c in group}) == 10
    assert all(('query' in c) != ('turns' in c) for c in group)
    validate_expected_tools(group, declarations, ROOT / 'data/eval_group.json')
    for name in ['eval_base.json', 'eval_adversarial.json']:
        original = subprocess.check_output(['git', 'show', f'HEAD:starter_v0/data/{name}'], cwd=ROOT.parent).decode('utf-8')
        assert json.loads(original) == json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))
    summary = {}
    for suite, expected_count in [('group', 10), ('adversarial', 12)]:
        runs = sorted(p for p in evidence.glob(f'v3_B_{suite}_*.json') if not p.name.endswith('.audit.json'))
        path = runs[-1]
        run = json.loads(path.read_text(encoding='utf-8'))
        audit = json.loads(path.with_suffix('.audit.json').read_text(encoding='utf-8'))
        assert run['summary'] == summarize(run['results'])
        assert run['summary']['provider_error_cases'] == 0
        assert run['summary']['measured_cases'] == run['summary']['total_cases'] == expected_count
        assert audit['dataset_sha256'] == sha(ROOT / 'data' / f'eval_{suite}.json')
        dataset = json.loads((ROOT / 'data' / f'eval_{suite}.json').read_text(encoding='utf-8'))
        assert [(r['id'], r['expect']) for r in run['results']] == [(c['id'], c['expect']) for c in dataset['cases']]
        assert run['prompt_hash'] == sha(ROOT / 'artifacts/versions/v3/system_prompt.md')
        assert run['tools_hash'] == sha(ROOT / 'artifacts/versions/v3/tools.yaml')
        assert audit['persistent_ticket_folder_unchanged'] and audit['temporary_tickets_removed_after_run']
        assert not audit['tool_http_attempts']
        summary[suite] = run['summary']
    probes = json.loads((evidence / 'security_boundary_probes.json').read_text(encoding='utf-8'))
    assert probes['total'] == len(probes['checks']) == 22
    assert probes['passed'] == sum(c['passed'] for c in probes['checks']) == 16
    followup = json.loads((evidence / 'retrieval_loop_review.json').read_text(encoding='utf-8'))
    assert len(followup['scenarios']) == 3
    assert all(s['result']['status'] == 'answered' and not s['ticket_files_created'] for s in followup['scenarios'])
    assert all(not r['sent'] for r in followup['web_requests'])
    paths = [ROOT / 'agent.py', ROOT / 'chat.py', ROOT / 'run_eval.py',
             *ROOT.glob('tools/*/tool.py'), *ROOT.glob('scripts/*audit*.py'),
             ROOT / 'scripts/security_boundary_probes.py', ROOT / 'scripts/review_retrieval_loop.py',
             ROOT / 'data/eval_group.json', ROOT / 'data/eval_adversarial.json']
    manifest = {'validation': 'passed; known safety failures remain recorded', 'suites': summary,
                'offline_expectations_met': '16/22', 'followup_scenarios_answered': 3,
                'sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}}
    (evidence / 'step34_validation.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print('Validated 10 original cases, both live suites, unchanged fixed datasets, artifact hashes, audits, 22 probes and 3 retrieval follow-ups.')


if __name__ == '__main__':
    main()

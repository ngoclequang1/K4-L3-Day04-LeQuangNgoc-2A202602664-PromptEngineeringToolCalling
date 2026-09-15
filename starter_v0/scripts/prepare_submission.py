"""Validate the working-tree deliverables and make a secret-free review archive.

Does not stage, commit, push, or submit to VLearn. Does not print secret values.
"""
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from zipfile import ZipFile, ZIP_DEFLATED

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB))
from env_loader import load_lab_env


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    load_lab_env(LAB)
    raw = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT)
    names = sorted(set(raw.decode('utf-8').split('\0')) - {''})
    audit_name = 'starter_v0/artifacts/evidence/submission_audit.json'
    names = [n for n in names if n != audit_name]
    forbidden = {'.git', '.venv', '__pycache__', '.pytest_cache', 'node_modules', 'submission'}
    for name in names:
        path = Path(name)
        assert not (forbidden & set(path.parts)), f'Excluded directory would be included: {name}'
        assert path.name == '.env.example' or not path.name.startswith('.env'), f'Environment file included: {name}'
        assert not name.startswith(('starter_v0/tickets/', 'starter_v0/runs/', 'starter_v0/transcripts/', 'starter_v0/analysis/'))
        assert path.suffix not in {'.pyc', '.pyo'}, f'Cache included: {name}'
        assert (ROOT / name).resolve().is_relative_to(ROOT.resolve()), 'Path escaped workspace'
    keys = [os.environ.get(k, '') for k in ['OPENROUTER_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GEMINI_API_KEY', 'TAVILY_API_KEY']]
    keys = [k.encode() for k in keys if len(k) >= 12 and '...' not in k]
    pattern = re.compile(rb'(?:sk-(?:or-v1-|ant-api\d+-|proj-)?[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{30,}|tvly-[A-Za-z0-9_-]{24,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
    contents = {}
    for name in names:
        data = (ROOT / name).read_bytes()
        assert not any(key in data for key in keys), f'Configured credential found in {name}'
        assert not pattern.search(data), f'Credential-like material found in {name}; inspect privately'
        contents[name] = data

    required = ['TEAMMATES.md', 'starter_v0/app.py', 'starter_v0/ui_session.py',
                'starter_v0/artifacts/REPORT.md', 'starter_v0/artifacts/system_prompt.md',
                'starter_v0/artifacts/tools.yaml', 'starter_v0/artifacts/version_log.csv',
                'starter_v0/data/eval_group.json', 'starter_v0/UI-GUIDE.md']
    assert all(name in contents for name in required)
    run_checks = []
    with (LAB / 'artifacts/version_log.csv').open(encoding='utf-8', newline='') as handle:
        versions = list(csv.DictReader(handle))
    assert [r['version'] for r in versions] == ['v0', 'v1', 'v2', 'v3']
    for row in versions:
        run = json.loads((LAB / row['run_file']).read_text(encoding='utf-8'))
        summary = run['summary']
        assert summary['provider_error_cases'] == 0
        assert summary['measured_cases'] == summary['total_cases'] == 30
        for filename, key in [('system_prompt.md', 'prompt_hash'), ('tools.yaml', 'tools_hash')]:
            data = (LAB / 'artifacts/versions' / row['version'] / filename).read_bytes()
            assert sha(data) == row[key] == run[key]
        run_checks.append({'version': row['version'], 'passed': summary['passed_cases'], 'measured': 30, 'hashes_match': True})
    for filename in ['system_prompt.md', 'tools.yaml']:
        assert (LAB / 'artifacts' / filename).read_bytes() == (LAB / 'artifacts/versions/v3' / filename).read_bytes()

    # Validate relative links in the authored entry-point documents, not example templates.
    checked_links = 0
    for name in ['SUBMISSION-READY.md', 'TEAMMATES.md', 'CHECKLIST.md', 'starter_v0/UI-GUIDE.md', 'starter_v0/artifacts/REPORT.md']:
        for target in re.findall(r'\]\(([^)]+)\)', contents[name].decode('utf-8')):
            if target.startswith(('http://', 'https://', '#')):
                continue
            target_path = (ROOT / name).parent / target.split('#')[0]
            if target_path.resolve() == (ROOT / audit_name).resolve():
                continue
            assert target_path.exists(), f'Broken link in {name}: {target}'
            checked_links += 1
    transcript_paths = sorted((LAB / 'artifacts/evidence/ui_transcripts').glob('*.transcript.json'))
    assert len(transcript_paths) == 4
    for path in transcript_paths:
        data = json.loads(path.read_text(encoding='utf-8'))
        assert data['prompt_hash'] == sha((LAB / 'artifacts/system_prompt.md').read_bytes())
        assert data['tools_hash'] == sha((LAB / 'artifacts/tools.yaml').read_bytes())
        assert all(t['status'] != 'provider_error' for t in data['turns'])
    audit = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'scope': 'working-tree review archive, not a published repository or VLearn submission',
        'technical_checks': 'passed', 'base_runs': run_checks, 'ui_transcripts': 4,
        'relative_links_checked': checked_links,
        'credential_scan': 'configured key exact matches and common token/private-key patterns: no matches',
        'synthetic_attack_data': 'Preserved the fixed lab password-like attack and clearly synthetic offline probes; these are not live credentials.',
        'real_data_scope': 'Fictional lab fixture data retained; student roster is required submission identity metadata.',
        'excluded': ['.git', '.env and local keys', '.venv', 'caches', 'generated ticket files', 'scratch runs/transcripts', 'previous archives'],
        'remaining': ['final personal commit and push', 'GitHub final-tree review', 'VLearn submission'],
        'manifest_excludes_itself': True,
        'files': [{'path': name, 'bytes': len(data), 'sha256': sha(data)} for name, data in contents.items()],
    }
    audit_bytes = json.dumps(audit, ensure_ascii=False, indent=2).encode('utf-8')
    (ROOT / audit_name).write_bytes(audit_bytes)
    out_dir = ROOT / 'submission'
    out_dir.mkdir(exist_ok=True)
    out = out_dir / 'Day04-LeQuangNgoc-review.zip'
    with ZipFile(out, 'w', ZIP_DEFLATED) as archive:
        for name, data in contents.items():
            archive.writestr(name, data)
        archive.writestr(audit_name, audit_bytes)
    with ZipFile(out) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(contents) + 1
    print(f'Validated {len(contents)} files, four base-run hashes, four transcripts, and {checked_links} links.')
    print('No configured credentials or common real-secret patterns found. Known synthetic attack fixtures retained.')
    print(f'Archive: {out.relative_to(ROOT)}')
    print('Final commit/push and VLearn submission remain pending; solo reflection is complete with AI assistance disclosed.')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Check repeated runs, incomplete fixes, valid alternatives, and cache-path coverage."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

from run_demo import verify_artifacts

ROOT = Path(__file__).resolve().parent
TASK = ROOT / 'tasks/field-roundtrip'


def counts(path):
    root = ET.parse(path).getroot()
    cases = list(root.iter('testcase'))
    data = {key: sum(case.find(tag) is not None for case in cases) for key, tag in [('failures', 'failure'), ('errors', 'error'), ('skipped', 'skipped')]}
    data['tests'] = len(cases)
    if len(cases) != 14 or data['errors'] or data['skipped']:
        raise RuntimeError(f'Invalid collection or runtime errors in {path}: {data}')
    if any(f.get('type') == 'HarnessError' for f in root.iter('failure')):
        raise RuntimeError(f'Infrastructure failure in {path}')
    return data, sorted((c.get('classname', ''), c.get('name', '')) for c in cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', default='better-auth-tasks:base')
    parser.add_argument('--output-dir', type=Path, default=TASK / 'evidence/cache-hardening')
    parser.add_argument('--jobs', type=int, choices=[1, 2, 3], default=2)
    parser.add_argument('--repeats', type=int, default=6)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error('--repeats must be positive')
    verify_artifacts()
    image_id = subprocess.check_output(['docker', 'image', 'inspect', args.image, '--format', '{{.Id}}'], text=True).strip()
    if not image_id.startswith('sha256:'):
        raise RuntimeError('Docker did not return an immutable image ID')
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    summary_path = output / 'summary.json'
    summary_path.unlink(missing_ok=True)
    reverts = [chunk.split(' b/', 1)[1].splitlines()[0] for chunk in (TASK / 'solution.patch').read_text().split('diff --git ')[1:]]
    scenarios = ['original', 'reference', 'cache-bypassed'] + ['control-' + p.stem for p in sorted((TASK / 'verification/controls').glob('*.patch'))] + [f'revert-{i}' for i in range(len(reverts))]

    def replay(scenario):
        folder = output / scenario
        folder.mkdir(exist_ok=True)
        folder.chmod(0o777)
        repeats = args.repeats if scenario in ['original', 'reference'] else 1
        for stale in folder.glob('run-*'):
            stale.unlink()
        command = ['docker', 'run', '--rm', '--network', 'none', '--mount', f'type=bind,source={TASK},target=/review,readonly', '--mount', f'type=bind,source={folder},target=/results', image_id, 'python3', '/review/verification/audit_case.py', scenario, str(repeats)]
        result = subprocess.run(command, capture_output=True, text=True)
        (folder / 'container.log').write_text(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError(f'{scenario}: container setup failed; see {folder / "container.log"}')
        exits = json.loads((folder / 'exits.json').read_text())
        if len(exits) != repeats:
            raise RuntimeError(f'{scenario}: missing runner exit codes')
        runs, identities = [], []
        for index, status in enumerate(exits, 1):
            data, names = counts(folder / f'run-{index}.xml')
            expected_pass = scenario in ['reference', 'control-alternative-cloned-json']
            failures = data['failures']
            if expected_pass and (status != 0 or failures != 0):
                raise RuntimeError(f'{scenario}: valid implementation rejected: {data}')
            if not expected_pass and (status != 1 or failures == 0):
                raise RuntimeError(f'{scenario}: incomplete implementation was not rejected: {data}')
            if scenario == 'original' and failures != 14:
                raise RuntimeError(f'{scenario}: every new case must fail at base')
            if scenario == 'cache-bypassed' and failures != 8:
                raise RuntimeError(f'{scenario}: expected all eight cookie cases to fail: {data}')
            runs.append({'run': index, 'exit': status, **data})
            identities.append(names)
        if any(names != identities[0] for names in identities):
            raise RuntimeError(f'{scenario}: test identities changed across repeats')
        if any(run != {**runs[0], 'run': run['run']} for run in runs):
            raise RuntimeError(f'{scenario}: results changed across repeats')
        record = {'scenario': scenario, 'runs': runs}
        if scenario.startswith('revert-'):
            record['reverted_file'] = reverts[int(scenario.removeprefix('revert-'))]
        return record, identities[0]

    results, identities = [], []
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {executor.submit(replay, s): s for s in scenarios}
        for future in as_completed(futures):
            record, names = future.result()
            results.append(record)
            identities.append(names)
            print(f"{record['scenario']}: {record['runs'][0]['failures']}/14 fail, {len(record['runs'])} run(s)", flush=True)
    if any(names != identities[0] for names in identities):
        raise RuntimeError('Different tests ran across scenarios')
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [TASK / 'test.patch', TASK / 'new_tests.ts', TASK / 'solution.patch', TASK / 'problem_statement.txt', ROOT / 'run_field_audit.py', TASK / 'verification/audit_case.py']}
    summary = {'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'base_commit': (TASK / 'base_commit.txt').read_text().strip(), 'image_id': image_id, 'artifact_sha256': hashes, 'agent_trials': False, 'platform_approved': False, 'results': sorted(results, key=lambda r: scenarios.index(r['scenario']))}
    summary_path.write_text(json.dumps(summary, indent=2) + '\n')
    print(f'All {len(scenarios)} scenarios verified. Evidence: {summary_path}')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, ET.ParseError, subprocess.CalledProcessError) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)

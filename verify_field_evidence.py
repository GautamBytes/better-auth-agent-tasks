#!/usr/bin/env python3
"""Verify imported audit hashes and fresh field-roundtrip results without Docker."""
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from run_demo import verify_artifacts
from run_field_audit import counts

ROOT = Path(__file__).resolve().parent
TASK = ROOT / 'tasks/field-roundtrip'


def verify_hashes(folder, hashes):
    for name, expected in hashes.items():
        path = folder / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError(f'Missing or changed evidence: {path}')


def main():
    verify_artifacts()
    for chunk in (TASK / 'test.patch').read_text().split('diff --git ')[1:]:
        path = chunk.split(' b/', 1)[1].splitlines()[0]
        expected = TASK / ('test.sh' if path == 'test.sh' else 'new_tests.ts')
        lines = chunk.splitlines(keepends=True)
        start = next(i for i, line in enumerate(lines) if line.startswith('@@'))
        contents = ''.join(line[1:] for line in lines[start + 1:] if line.startswith('+'))
        if contents != expected.read_text():
            raise RuntimeError(f'Patch payload differs from standalone file: {path}')
        if path == 'test.sh' and 'new file mode 100755' not in chunk:
            raise RuntimeError('Root runner must be executable')
    quality = TASK / 'evidence/cache-hardening-quality'
    if (quality / 'status.txt').read_text().strip() != 'biome=0 typecheck=0':
        raise RuntimeError('Fresh Biome and affected-project typecheck did not both pass')
    for name in ['biome.log', 'build.log', 'typecheck.log']:
        if not (quality / name).is_file():
            raise RuntimeError(f'Missing quality log: {name}')
    historical = TASK / 'evidence/historical/2026-11-04'
    inventory = json.loads((historical / 'inventory.json').read_text())
    verify_hashes(historical / 'package', inventory['files'])
    manifest = json.loads((historical / 'package/manifest.json').read_text())
    verify_hashes(historical / 'package', manifest['sha256'])
    audit_dir = TASK / 'evidence/cache-hardening'
    audit = json.loads((audit_dir / 'summary.json').read_text())
    verify_hashes(ROOT, audit['artifact_sha256'])
    expected_scenarios = {'original', 'reference', 'cache-bypassed'} | {'control-' + p.stem for p in (TASK / 'verification/controls').glob('*.patch')} | {f'revert-{i}' for i in range(8)}
    results = audit['results']
    if len(results) != len(expected_scenarios) or {r['scenario'] for r in results} != expected_scenarios:
        raise RuntimeError('Audit scenario coverage changed')
    identities = []
    for result in results:
        scenario = result['scenario']
        runs = result['runs']
        if len(runs) != (6 if scenario in ['original', 'reference'] else 1):
            raise RuntimeError(f'{scenario}: expected six repeat runs per side or one control run')
        recorded_exits = json.loads((audit_dir / scenario / 'exits.json').read_text())
        if recorded_exits != [run['exit'] for run in runs]:
            raise RuntimeError(f'{scenario}: recorded exits disagree')
        for run in runs:
            actual, names = counts(audit_dir / scenario / f"run-{run['run']}.xml")
            identities.append(names)
            if actual != {key: run[key] for key in ['tests', 'failures', 'errors', 'skipped']}:
                raise RuntimeError(f'{scenario}: summary disagrees with JUnit')
            expected_pass = scenario in ['reference', 'control-alternative-cloned-json']
            if (run['exit'] == 0) != expected_pass or (actual['failures'] == 0) != expected_pass:
                raise RuntimeError(f'{scenario}: unexpected pass or failure')
            if scenario == 'original' and actual['failures'] != 14:
                raise RuntimeError('Every original case must fail')
            if scenario == 'cache-bypassed' and actual['failures'] != 8:
                raise RuntimeError('All eight cookie cases must reject cache bypass')
    if any(names != identities[0] for names in identities):
        raise RuntimeError('Test identities differ across controls')
    replay = json.loads((TASK / 'evidence/results.json').read_text())
    if replay['base_commit'] != audit['base_commit'] or replay['image_id'] != audit['image_id']:
        raise RuntimeError('Replay and audit use different source or images')
    for stage, expected_count, expected_failures in [('base-before', 488, 0), ('new-before', 14, 14), ('base-after', 488, 0), ('new-after', 14, 0)]:
        cases = list(ET.parse(TASK / 'evidence' / (stage + '.xml')).getroot().iter('testcase'))
        actual = {'tests': len(cases), 'failures': sum(c.find('failure') is not None for c in cases), 'errors': sum(c.find('error') is not None for c in cases), 'skipped': sum(c.find('skipped') is not None for c in cases)}
        if actual != {'tests': expected_count, 'failures': expected_failures, 'errors': 0, 'skipped': 0} or actual != replay['reports'][stage]:
            raise RuntimeError(f'Replay evidence mismatch: {stage}')
    print(f"Verified {len(inventory['files'])} historical files, {len(results)} current scenarios, six repeat runs per side, and the 488/14 before-and-after replay.")
    print('Agent difficulty and platform approval remain unverified.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, KeyError, ValueError, RuntimeError) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)

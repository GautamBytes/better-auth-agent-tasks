#!/usr/bin/env python3
"""Run one field-roundtrip control inside an offline disposable container."""
import json
from pathlib import Path
import subprocess
import sys


def run(command, log):
    result = subprocess.run(command, cwd='/app', text=True, capture_output=True)
    Path(log).write_text(result.stdout + result.stderr)
    return result.returncode


def main():
    scenario, repeats = sys.argv[1], int(sys.argv[2])
    review = Path('/review')
    if not Path('/app/packages/better-auth/src/api/routes/session.ts').exists():
        raise RuntimeError('Expected clean Better Auth source under /app')
    subprocess.run(['sha256sum', '--check', str(review / 'evidence/runner-v2-base-source-hashes.txt')], cwd='/app', check=True, capture_output=True)
    subprocess.run(['git', 'apply', str(review / 'test.patch')], cwd='/app', check=True)
    if scenario != 'original':
        patch = review / 'solution.patch'
        if scenario.startswith('control-'):
            patch = review / 'verification/controls' / (scenario.removeprefix('control-') + '.patch')
        subprocess.run(['git', 'apply', str(patch)], cwd='/app', check=True)
    if scenario == 'cache-bypassed':
        path = Path('/app/packages/better-auth/src/api/routes/session.ts')
        source = path.read_text()
        needle = 'const shouldUseCookieCache =\n\t\t\t\t\tcookieCacheEnabled && !ctx.query?.disableCookieCache;'
        if source.count(needle) != 1:
            raise RuntimeError('Cache-bypass mutation no longer matches the pinned source')
        path.write_text(source.replace(needle, 'const shouldUseCookieCache = false;'))
    if scenario.startswith('revert-'):
        index = int(scenario.removeprefix('revert-'))
        chunks = (review / 'solution.patch').read_text().split('diff --git ')[1:]
        subprocess.run(['git', 'apply', '-R', '-'], input='diff --git ' + chunks[index], cwd='/app', text=True, check=True)
    runtime = subprocess.check_output(['bash', '-c', 'id; uname -m; node --version; pnpm --version'], text=True)
    Path('/results/runtime.txt').write_text(runtime)
    exits = []
    for index in range(1, repeats + 1):
        xml = f'/results/run-{index}.xml'
        if index == 1:
            command = ['./test.sh', '--output_path', xml, 'new']
        else:
            command = ['pnpm', 'exec', 'vitest', 'run', '--project', 'better-auth', 'packages/better-auth/src/api/routes/session-field-roundtrip.test.ts', '--reporter=default', '--reporter=junit', '--outputFile.junit=' + xml]
        exits.append(run(command, f'/results/run-{index}.console.log'))
    Path('/results/exits.json').write_text(json.dumps(exits) + '\n')


if __name__ == '__main__':
    main()

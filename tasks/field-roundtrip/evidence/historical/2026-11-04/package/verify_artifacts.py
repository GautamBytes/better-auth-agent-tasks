#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,sys,xml.etree.ElementTree as E
root=Path(__file__).resolve().parent
manifest_path=root/'manifest.json'
if manifest_path.exists():
    manifest=json.loads(manifest_path.read_text())
    for name,digest in manifest['sha256'].items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,f'Hash mismatch: {name}'
base=(root/'base_commit.txt').read_text().strip()
assert re.fullmatch('[0-9a-f]{40}',base)
assert json.loads((root/'repository.json').read_text())['base_commit']==base
patch=(root/'test.patch').read_text()
sections=patch.split('diff --git ')[1:]
paths=[s.splitlines()[0].split(' b/',1)[1]for s in sections]
assert set(paths)=={'test.sh','packages/better-auth/src/api/routes/session-field-roundtrip.test.ts'}
assert all('new file mode 'in s and '--- /dev/null'in s for s in sections)
assert 'new file mode 100755'in next(s for s in sections if s.startswith('a/test.sh '))
runner_section=next(s for s in sections if s.startswith('a/test.sh '))
runner_body='\n'.join(line[1:] for line in runner_section.splitlines() if line.startswith('+') and not line.startswith('+++'))+'\n'
assert runner_body==(root/'test.sh').read_text(),'Packaged runner differs from test.patch'
title=(root/'title.txt').read_text()
statement=(root/'problem_statement.txt').read_text()
for api in json.loads((root/'requirements_mapping.json').read_text())['public_apis']:
    assert api in title and api in statement,f'Missing public entry point: {api}'
solution=(root/'solution.patch').read_text()
solution_paths=re.findall(r'^diff --git a/(.*?) b/',solution,re.M)
assert len(solution_paths)==8 and all(p.endswith('.ts')and'.test.'not in p for p in solution_paths)
image=(root/'Dockerfile').read_text()
assert '@sha256:'in image.splitlines()[0]
assert 'WORKDIR /app'in image and 'COPY . .'in image and 'USER node'in image
assert image.rstrip().endswith('CMD ["/bin/bash"]')
assert not any('RUN'in line and ('vitest'in line or 'test.sh'in line)for line in image.splitlines())
def report(path,count,failures):
    tree=E.parse(path).getroot();cases=list(tree.iter('testcase'))
    assert len(cases)==count,(path,len(cases))
    assert sum(c.find('failure')is not None for c in cases)==failures,path
    assert not any(c.find('error')is not None or c.find('skipped')is not None for c in cases),path
    assert int(tree.attrib['tests'])==count and int(tree.attrib['failures'])==failures,path
    assert not any(f.attrib.get('type')=='HarnessError'for f in tree.iter('failure')),path
    return sorted(c.attrib.get('classname','')+'::'+c.attrib['name']for c in cases)
arches=['docker-replay']
if (root/'evidence/docker-amd64-replay').exists():arches.append('docker-amd64-replay')
for arch in arches:
    folder=root/'evidence'/arch
    old=report(folder/'base-before.xml',488,0);new=report(folder/'base-after.xml',488,0);assert old==new
    old=report(folder/'new-before.xml',14,14);new=report(folder/'new-after.xml',14,0);assert old==new
    assert (folder/'exits.txt').read_text().strip()=='0 1 0 0'
controls=json.loads((root/'evidence/controls.json').read_text())
assert len(controls)==5
for c in controls:
    assert c['errors']==0 and c['new_tests']==14
    assert (c['failures']>0 and c['process_exit']!=0)if c['expected']=='fail'else(c['failures']==0 and c['process_exit']==0 and c['base_tests']==377)
assert json.loads((root/'evidence/typecheck-result.json').read_text())['exit_code']==0
audit=root/'evidence/independent-audit'
repeats=json.loads((audit/'repeat-results.json').read_text())
assert len(repeats)==12
for stage in ('base','fixed'):
    runs=[r for r in repeats if r['stage']==stage]
    assert sorted(r['run']for r in runs)==list(range(1,7))
    for run in runs:
        expected_failures=14 if stage=='base'else 0
        assert run['tests']==14 and run['failures']==expected_failures and run['errors']==0 and run['skips']==0
        assert run['exit']==(1 if stage=='base'else 0)
        report(audit/f"repeat-{stage}-{run['run']}.xml",14,expected_failures)
mutations=json.loads((audit/'mutation-results.json').read_text())
assert sorted(m['reverted_file']for m in mutations)==sorted(solution_paths)
for index,mutation in enumerate(mutations):
    assert mutation['exit']!=0 and mutation['tests']==14 and mutation['failures']>0 and mutation['errors']==0
    report(audit/f'revert-{index}.patch.xml',14,mutation['failures'])
assert len((root/'problem_statement.txt').read_text().split())<=1000
print(f'Artifact audit passed: {len(solution_paths)} reference files; 14 red/green cases; 488 preserved tests; {len(arches)} architectures; 5 controls; 12 repeat runs; 8 single-file reverts.')

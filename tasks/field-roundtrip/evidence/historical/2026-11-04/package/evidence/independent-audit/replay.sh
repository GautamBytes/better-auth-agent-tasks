#!/bin/bash
set -e
cd /app
git apply /review/test.patch
git apply /review/solution.patch
python3 - <<'INNER'
import json,subprocess,xml.etree.ElementTree as E
from pathlib import Path
results=[]
for patch,path in json.loads(Path('/audit/mutations.json').read_text()):
    subprocess.run(['git','apply','-R','/audit/'+patch],check=True)
    report='/audit/'+patch+'.xml'
    run=subprocess.run(['./test.sh','--output_path',report,'new'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    root=E.parse(report).getroot(); cases=list(root.iter('testcase'))
    item={'reverted_file':path,'exit':run.returncode,'tests':len(cases),'failures':sum(c.find('failure') is not None for c in cases),'errors':sum(c.find('error') is not None for c in cases)}
    if run.returncode==0:
        base=subprocess.run(['./test.sh','--output_path',report+'.base.xml','base'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        item['base_exit']=base.returncode
        Path(report+'.base.console').write_text(base.stdout)
    Path(report+'.console').write_text(run.stdout)
    results.append(item)
    Path('/audit/mutation-results.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(item),flush=True)
    subprocess.run(['git','apply','/audit/'+patch],check=True)
INNER

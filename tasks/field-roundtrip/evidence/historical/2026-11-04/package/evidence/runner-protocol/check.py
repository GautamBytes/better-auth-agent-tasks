import os,pathlib,subprocess,json,xml.etree.ElementTree as E
root=pathlib.Path('/private/tmp/ba-runner-review')
results=[]
for scenario in ['build-fail','missing-report','zero','skip','assertion-fail','exit-fail-pass-report','success']:
    out=root/(scenario+'.xml')
    p=subprocess.run([str(root/'test.sh'),'--output_path',str(out),'new'],env=dict(os.environ,PATH=str(root/'bin')+':'+os.environ['PATH'],RUNNER_SCENARIO=scenario),capture_output=True,text=True)
    tree=E.parse(out).getroot();cases=list(tree.iter('testcase'))
    results.append(dict(scenario=scenario,exit=p.returncode,report_attributes=tree.attrib,cases=len(cases),failure_cases=sum(c.find('failure')is not None for c in cases),error_cases=sum(c.find('error')is not None for c in cases),skipped_cases=sum(c.find('skipped')is not None for c in cases),stdout=p.stdout.strip(),stderr=p.stderr.strip()))
(root/'results.json').write_text(json.dumps(results,indent=2))
for r in results:print(json.dumps(r))

#!/bin/bash
set -euo pipefail
cd /app
python3 - <<'CHECK'
from pathlib import Path
import hashlib,json
m=json.loads(Path('/review/source.json').read_text())
for key in ['source','existing_test']:
 p=Path(m[key+'_file'])
 assert hashlib.sha256(p.read_bytes()).hexdigest()==m[key+'_sha256'],str(p)
assert not Path('test.sh').exists()
assert not Path('packages/better-auth/src/utils/wildcard-stability.test.ts').exists()
CHECK
test "$(id -u)" != 0
{
  id
  uname -m
  node --version
  pnpm --version
} > /results/runtime.txt
node --experimental-strip-types /review/verification/source_demo.mjs > /results/source-before.txt
git apply --check /review/test.patch
git apply /review/test.patch
set +e
./test.sh --output_path /results/base-before.xml base
base_before=$?
./test.sh --output_path /results/new-before.xml new
new_before=$?
set -e
git apply --check /review/solution.patch
git apply /review/solution.patch
node --experimental-strip-types /review/verification/source_demo.mjs > /results/source-after.txt
set +e
./test.sh --output_path /results/base-after.xml base
base_after=$?
./test.sh --output_path /results/new-after.xml new
new_after=$?
set -e
printf '%s %s %s %s\n' "$base_before" "$new_before" "$base_after" "$new_after" > /results/exits.txt
test "$(cat /results/exits.txt)" = '0 1 0 0'

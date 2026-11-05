#!/bin/bash
set -euo pipefail
cd /app
sha256sum --check /review/evidence/runner-v2-base-source-hashes.txt
test "$(id -u)" != 0
test ! -f test.sh
test ! -f packages/better-auth/src/api/routes/session-field-roundtrip.test.ts
git apply --check /review/test.patch
git apply /review/test.patch
cmp test.sh /review/test.sh
{
  uname -m
  id
  node --version
  pnpm --version
  cat /review/base_commit.txt
} > /results/runtime.txt
set +e
./test.sh --output_path /results/base-before.xml base
base_before=$?
./test.sh --output_path /results/new-before.xml new
new_before=$?
set -e
git apply --check /review/solution.patch
git apply /review/solution.patch
set +e
./test.sh --output_path /results/base-after.xml base
base_after=$?
./test.sh --output_path /results/new-after.xml new
new_after=$?
set -e
printf '%s %s %s %s\n' "$base_before" "$new_before" "$base_after" "$new_after" > /results/exits.txt
test "$(cat /results/exits.txt)" = '0 1 0 0'

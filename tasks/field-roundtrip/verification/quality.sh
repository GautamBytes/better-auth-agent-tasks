#!/bin/bash
set -euo pipefail
cd /app
git apply /review/test.patch
git apply /review/solution.patch
pnpm exec biome check packages/better-auth/src/api/routes/session-field-roundtrip.test.ts > /results/biome.log 2>&1
pnpm --filter 'better-auth^...' build > /results/build.log 2>&1
pnpm exec tsc --build packages/better-auth/tsconfig.json --force > /results/typecheck.log 2>&1
printf 'biome=0 typecheck=0\n' > /results/status.txt

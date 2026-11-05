Local task handoff: declared-field serialization round trips

Status
The task files and local technical checks are ready. Platform eligibility and acceptance gates remain pending. This is not platform-approved and has no coding-agent difficulty trials. No issue, PR, push, commit or submission was made. Changes exist only in the local checkout and this package.

Submission files
- title.txt
- problem_statement.txt
- repository.json and base_commit.txt
- test.patch: only a new regression test file and executable root test.sh
- solution.patch: reference changes across 8 production files
- Dockerfile and .dockerignore
- test.sh: same executable included in test.patch

Repository
https://github.com/better-auth/better-auth
Base e7200d132f5946490c19a389b5a89b31aeead4e7
MIT license, copied in repository-LICENSE.txt. Stars and activity passed the recorded screen. Live platform repository eligibility, quota, base-image approval and assistance policy remain unverified. The statement is an assisted working submission draft for the contributor to review under the team's rules.

What the task checks
One coherent rule applies across model persistence and session caches. Declared non-date data remains non-date data. The 14 new cases use 2 different timestamp spellings across 7 routes. Built-in and explicitly configured dates remain Date, and nulls, empty arrays, nested JSON and output privacy are preserved. Secondary cases also pass through public user and session updates. Client-side parsing and standalone getCookieCache are outside scope.

Verified local results
- Clean base: 488 existing tests pass; all 14 new cases fail on assertions, not setup errors. No skipped tests.
- Reference solution: 488 existing plus 14 new tests pass, with zero errors or skips.
- Four incomplete fixes were rejected before the runner expansion: adapter-only, 10 failures, cookie-only, 14, persistence-only, 6, missing-rewrite-fix, 4.
- Before the runner expansion, a legitimate alternative that clones raw JSON instead of returning pre-parsed objects by reference passes all 14 new and 377 existing tests. The verifier does not require the reference implementation's object identity.
- The pinned Dockerfile builds from clean source without test or solution patches. A separate --no-cache build succeeds.
- Linux arm64 and amd64 replays run as node, with --network none. It applies test.patch first, runs base/new, applies solution.patch, then repeats both modes.
- Full repository pnpm typecheck passes after generating the existing Prisma adapter client prerequisite. The first typecheck failure and the prerequisite command are recorded honestly.
- Changed TypeScript files pass Biome; git diff --check passes. Independent source/test review found no blocking runtime or fairness defect.

The reproduction is an assertion failure before the fix, not an infrastructure failure. Evidence is in evidence/docker-replay and evidence/controls.json. Synthetic runner-failure controls are separately labelled in evidence/runner-protocol. No coding-agent evaluation attempts were run. Independent authoring and review subagents were used; these were not difficulty trials.

Build from a fresh pinned checkout
1. Clone the public repository locally and check out e7200d132f5946490c19a389b5a89b31aeead4e7.
2. Copy only Dockerfile and .dockerignore into that checkout. Keep the test/reference patches outside the build context.
3. Run docker build -t better-auth-string-roundtrip:base .
4. Mount this package read-only into the container, apply test.patch, and invoke the runner.

Required runner commands
./test.sh --output_path /tmp/base-results.xml base
./test.sh --output_path /tmp/new-results.xml new

The base mode explicitly selects 9 existing test files, including internal adapters, cache fallback, multi-session and custom-session coverage. The new mode explicitly selects the 14 new cases. Both rebuild the affected workspace dependencies so changed core source is actually exercised. Both preserve real test names and assertion failures. Zero collection, skipped new cases, invalid/missing reports, build failure and process/report disagreement produce failing JUnit rather than empty or success-shaped output. Build and Vitest logs are retained beside each XML.

Expected patch replay
- Clean source plus test.patch: base exits 0, new exits 1.
- Then apply solution.patch: base exits 0, new exits 0.
The Docker image itself contains neither patch and does not run tests while building. Runtime needs no network or external service. The default execution user is non-root and owns /app. Do not mount solution.patch or author-control materials into a future agent's starting workspace unless the platform explicitly requires them. The package is an author/team handoff, not an agent workspace.

Host environment and checks
Node 24.19.0, pnpm 11.1.1; lockfile unchanged. Package versions are pinned by the repository lockfile. Docker base is pinned by immutable digest; git, Python and CA package versions are also pinned.
pnpm install --frozen-lockfile --ignore-scripts
pnpm --filter @better-auth-test/prisma-adapter exec prisma generate --schema base.prisma
pnpm typecheck
The narrower Docker install uses --filter better-auth... and does not require the Prisma integration client, since it runs only the explicit affected-area test lists.

Originality refresh
The refreshed all-state searches fetched 9 ISO/string/cache results, 53 preserve/additionalFields/string results, 14 revive/string results and 4 date-shaped results. Earlier broader searches were fully paginated at 115 and 331 results. Related issues, PR patches, Discussions and file histories were inspected. No directly matching implementation or maintainer rejection was found. This is scoped search evidence, not an absolute guarantee.
Closest work is PR #8248 broad date revival, PR #10301 and issue #9963, date-typed normalization, PR #4237, array serialization, PR #8328, parse-error handling and PR #10934, cache validation. PR #11494 also preserves date-shaped Magic Link display names within its verification-record parser; its actual patch does not fix model arrays/JSON or server session cache decoding. This task does not reuse that change or its tests.

Before team submission
Confirm live eligibility/quota, accepted base image and assistance policy. Use the team's current evaluation criteria and credits for step 6. No success-rate or frontier-difficulty claim is supported yet. Public source-code breadth and 14 tests do not establish the required difficulty.

Audit the saved package
Run python3 verify_artifacts.py from this folder. It checks hashes, patch boundaries, saved JUnit cases, both architectures and incomplete/alternative-fix controls. This audits stored evidence; it does not rerun software tests or model trials.

Runner v2 update
The title now spells out all four public APIs. The base runner includes 111 more existing tests, for 488 preserved tests and 14 new cases. The regression test, problem statement, reference fix and Dockerfile are unchanged. Fresh offline patch replays on both architectures use the expanded runner.

The independent audit includes six runs of the unchanged new test on each side of the fix. All six original runs fail all 14 cases; all six fixed runs pass them. Reverting each of the eight changed production files separately causes an assertion failure. These are local deterministic checks, not coding-agent difficulty evaluations. Their original logs are under evidence/independent-audit.

Historical evidence is kept as recorded. Replay folders ending runner-v1, incomplete-fix controls, the valid-alternative test and runner-protocol controls used the earlier 377-test base list. See evidence/runner-v2-scope.txt. The current replay folders and summary use 488. GUIDELINE_REVIEW.md distinguishes verified requirements from platform gates that have not been run.

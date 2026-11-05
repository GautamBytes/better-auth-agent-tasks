# Field-roundtrip guide review

Reviewed 5 November 2026 against the [contributor guide](https://app.notion.com/p/Contributor-Guide-Building-Your-First-Task-4082084775bb81cdb89cff211d2e73e7). This records local task verification. It does not certify platform acceptance.

## What changed

The same 14 regression cases remain. The eight cookie cases now prove that valid cached custom fields are returned without backing user/session reads. Each includes a cache-disabled positive control that must perform a backing read. The observers preserve actual adapter behavior and allow JWT signing-key lookups.

The statement explicitly names the cache-hit requirement. The reference solution, upstream commit, Dockerfile, nine existing test files, and 488-test base selection are unchanged. The test patch adds only the regression test and executable root `test.sh`.

## Requirement and evidence

| Requirement | Evidence and limit |
| --- | --- |
| Eligible source repository | Better Auth is the upstream source, not this private task-review repository. Recorded public checks identify TypeScript, MIT, more than 500 stars, and recent activity. See the historical originality records. Live platform eligibility and remaining quota are unconfirmed. |
| Exact source revision | Both task and audit pin `e7200d132f5946490c19a389b5a89b31aeead4e7`. Offline replays verify the starting hashes of affected production and existing test files before patching. |
| Originality | The imported package preserves the prior issue, PR, Discussion, and file-history searches. No direct match was recorded. These searches are dated evidence, not a guarantee or a fresh search on 5 November. |
| Behavior-only statement | The title and statement name `auth.api.signUpEmail`, `auth.api.getSession`, `auth.api.updateUser`, and `auth.api.updateSession`. The statement specifies exact values, field types, cache strategies, secondary-storage forms, update preservation, and exclusions. The contributor must review wording under the team's current assistance policy. |
| Public behavior and fair coverage | The tests call public auth APIs. Values and types are checked across seven storage routes and two timestamp strings. Backing adapter observations prove the cookie path is used, with a positive control and without substituting database results. |
| Red and green | Fresh offline replay records 488 existing passes on both versions. All 14 strengthened new cases fail on the original and pass with the unchanged reference solution. See `evidence/results.json` and its JUnit files. |
| Repeatability | `run_field_audit.py` runs the strengthened new tests six times at base and six times with the reference fix. Each side must have identical counts and test identities. These are deterministic test repetitions, not coding-agent trials. |
| Partial fixes and minimality | The current audit rejects a deliberate cache bypass, four existing incomplete fixes, and all eight single-file reverts. The cache bypass fails all eight cookie cases while the six database/secondary cases still pass. |
| Alternative implementations | The existing JSON-cloning alternative must pass all strengthened new tests. The assertions do not require the reference helper or its exact implementation. |
| Runner integrity | The unchanged runner supports `base`, `new`, and `--output_path`, explicit test lists, JUnit XML, zero-collection and skipped-new-test checks, build errors, and process/report disagreement. Prior synthetic runner controls are retained in the historical package. |
| Environment | Fresh runs use the existing immutable Docker image, a non-root user, and `--network none`. The historical package includes clean/no-cache builds and arm64/amd64 replays. Fresh strengthened-test results are arm64 only. Platform acceptance of the base image is unconfirmed. |
| Reference quality | The eight-file production fix is unchanged. Historical typecheck and Biome evidence is retained. Fresh Biome and affected-project TypeScript checks for the strengthened tests are under `evidence/cache-hardening-quality/`. The narrow offline image lacks the e2e Prisma CLI needed for a fresh full-repository check. The failed prerequisite attempt is retained, and no fresh full-repository typecheck is claimed. |
| Hidden artifacts | This private repository is a reviewer handoff containing answers, hidden tests, and control mutations. Evaluated agents must receive only pinned upstream code and the approved statement, not this repository or its evidence. |
| Agent difficulty and acceptance | No platform agent trials, solve-rate qualification, long-horizon qualification, pass review, unfairness/cheating review, or final approval has been performed here. Local checks cannot replace these gates. |

## Reproduce the local checks

From the repository root, with the base image from `SETUP.md` available:

```sh
python3 run_demo.py field-roundtrip
python3 run_field_audit.py --jobs 2
python3 verify_field_evidence.py
```

The first command checks both original and fixed code through the actual root test runner. The second uses a separate offline container for each implementation control. Repeat runs after the first runner invocation execute the same explicit Vitest file directly, avoiding repeated dependency builds. The third reconciles saved JUnit results, input hashes, and the imported archive without Docker.

To repeat formatting and typechecking, run `verification/quality.sh` inside the same clean image with this task mounted read-only at `/review` and a writable report directory at `/results`. It applies the current test and reference patches before checking them.

## Remaining platform work

Confirm repository eligibility/quota, the accepted image, the current assistance policy, and evaluation-budget access. Then run the platform's required coding-agent attempts and reviews. The guide's dated thresholds must be checked against the live submission panel before spending credits.

The explicit cache-hit sentence changes the statement. Do not combine any older agent runs with evaluations of this revision. None are recorded in this repository.

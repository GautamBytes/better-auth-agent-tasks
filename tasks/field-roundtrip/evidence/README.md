# Field-roundtrip evidence

Current and historical evidence are separate. Run `python3 verify_field_evidence.py` from the repository root to reconcile artifact hashes and saved results.

## Current strengthened tests, 5 November 2026

- [Before/after summary](results.json) and `base-before.xml`, `new-before.xml`, `base-after.xml`, and `new-after.xml` record the current patch through the actual root runner. The selected 488 existing tests pass before and after. All 14 new cases fail before and pass after.
- [Audit matrix](cache-hardening/summary.json) records immutable image identity, current input hashes, six original runs, six fixed runs, four incomplete fixes, one valid alternative, the cache-bypass mutation, and eight single-file reverts.
- Each matrix scenario has JUnit reports, runner exit codes, runtime identity, console output, and dependency-build logs under `cache-hardening/`.
- `cache-hardening-quality/` contains fresh Biome, dependency-build, and affected-project TypeScript logs. Its `status.txt` is written only after every check succeeds. The initial full-check setup failure is retained under `initial-full-check/`; the task image lacks the e2e Prisma CLI.

All eight cookie cases must reject the deliberate cache bypass. This directly checks the coverage gap that motivated the strengthened tests. The matrix is a local verifier audit, not an agent-difficulty study.

## Imported audit, 4 November 2026

[The original package](historical/2026-11-04/package/) is retained byte-for-byte with [an inventory](historical/2026-11-04/inventory.json). Its original `manifest.json` covers 266 files; the new inventory covers all 267 imported files, including that manifest.

Useful starting points:

- [Original guideline review](historical/2026-11-04/package/GUIDELINE_REVIEW.md).
- [Six-repeat and file-revert audit](historical/2026-11-04/package/evidence/independent-audit/audit-summary.json), with raw JUnit reports beside it.
- [Incomplete-fix and alternative results](historical/2026-11-04/package/evidence/controls.json), with replay patches under the package's `verification/controls/` and raw reports under `evidence/control-*/`.
- [Typecheck result](historical/2026-11-04/package/evidence/typecheck-result.json), source review, and logs under the package's `evidence/`.
- [Recorded originality searches](historical/2026-11-04/package/evidence/originality/), build logs, arm64/amd64 replays, and runner protocol checks under the same directory.

Those results describe the original test patch. Some earlier controls used a 377-test base selection; later original-package replays use 488. Neither number describes a full repository suite. Historical results are not relabeled as verification of the new cache-read assertions.

## Limits

Fresh strengthened-test runs are on Linux arm64. Historical amd64 checks cover the original tests. No agent trials or platform approval are claimed. Keep this reviewer evidence and the reference solution outside the evaluated agent's workspace.

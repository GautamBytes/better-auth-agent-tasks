# Guideline review

Reviewed 4 November 2026 against the contributor guide and the local independent audit. This is a technical readiness report. It does not certify platform acceptance.

Source guide: https://app.notion.com/p/Contributor-Guide-Building-Your-First-Task-4082084775bb81cdb89cff211d2e73e7

## Changes made

- Added the exact four public API names to the title.
- Expanded the base runner from five existing files and 377 tests to nine files and 488 tests. No existing test file was edited.
- Regenerated test.patch so its executable root test.sh matches the standalone runner.
- Replayed the final patch offline on Linux arm64 and amd64. The problem statement, 14 new tests, eight-file reference fix and Dockerfile are unchanged.
- Added independent repeat and single-file revert evidence. Kept older 377-test evidence labelled as historical.
- Refreshed package summaries, checksums and ZIPs. The artifact verifier checks API naming and runner/patch agreement too.

## Requirement and evidence

| Requirement | Local result and remaining limit |
| --- | --- |
| Public production repository, stars, recent activity, language and licence | Better Auth is public, TypeScript and MIT. Recorded 30,582 stars and 3 November 2026 activity pass the dated public screen. Platform eligibility and remaining quota are unverified. |
| Exact pinned revision | Base commit e7200d132f5946490c19a389b5a89b31aeead4e7. Fresh replay checks the base hashes of eight affected production files and nine existing test files before applying patches. |
| Original behaviour and no matching implementation/rejection | Recorded paginated issues, PRs, Discussions and file-history searches found no directly matching implementation or maintainer rejection. This is bounded search evidence, not a guarantee that no duplicate exists. |
| Title and self-contained statement | Title and statement include auth.api.signUpEmail, auth.api.getSession, auth.api.updateUser and auth.api.updateSession. Statement is 210 words of plain behaviour-focused prose, with exact string examples, date guards and scope exclusions. Contributor must review wording under the team's current assistance policy. |
| New files only in test.patch | Exactly the new 14-case test file and executable root test.sh. Existing tests are selected, not modified. |
| Meaningful red/green behaviour | All 14 new cases fail on assertions at base and pass with the reference solution. All 488 existing affected-area cases pass before and after. No errors or skips in either architecture's fresh reports. |
| Repeatability | Six original runs each fail 14/14; six fixed runs pass 14/14. These prior independent runs use the unchanged new test. They are not agent trials. |
| Coverage and minimality | All eight single-file reverts trigger assertions. Four plausible incomplete fixes fail; a legitimate JSON-cloning alternative passes. Those earlier controls used the original 377-test base list and unchanged new tests. |
| Runner protocol | base/new, --output_path, explicit file lists, named JUnit cases, no fail-fast, build logs and process/report checks. Prior synthetic controls cover zero collection, skipped new tests, invalid/missing reports, build failure and process/report disagreement. |
| Reproducible environment | Pinned image digest and dependency lockfile, /app, COPY . ., non-root writable environment and bash command. Clean and no-cache builds were recorded. Final runner replays are offline on arm64 and amd64. Whether this base image is accepted by the platform remains unverified. |
| Reference quality | Eight relevant production files. Recorded full typecheck passes after generating the repository's existing Prisma prerequisite; changed TypeScript passes Biome and diff checks. These checks were retained because the reference code did not change in this update. |
| Agent difficulty and review | Not performed. Actual platform agent attempts, solve rates, long-horizon metric, unfairness/environment classification, pass review, cheating review and final acceptance remain pending. Local test counts cannot substitute for these results. |

## Before recording or submission

1. Confirm repository eligibility/quota, accepted base image, current assistance policy and who supplies evaluation credits.
2. Use the team's current panel to run the required agent evaluations. The dated guide describes at least four attempts per agent, exactly one agent with a nonzero success rate no higher than 25%, other agents at zero, and a long-horizon average threshold of 400K. The live platform rules take precedence.
3. Review passing attempts and unfair or environment-blocked runs, complete the cheating and final review gates, and record the real outcomes.
4. Keep reference solutions, hidden tests and author-control evidence out of the evaluated agent's starting workspace unless the platform harness explicitly requires otherwise. The ZIPs are team handoff packages, not agent starting workspaces.

No platform runs, upstream writes, commits, video recording or submissions were made in this update. The guide does not establish personal recording requirements or contributor payout terms.

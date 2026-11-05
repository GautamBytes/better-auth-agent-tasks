# Preserve field values after storage

A field declared as text should stay exactly that text when Better Auth saves and reads it back.

## The bug

Suppose `trackingId` has type `string` and contains:

```text
2024-01-02T03:04:05Z
```

A shared JSON reader sees date-looking text and turns it into a JavaScript `Date`. This can also affect strings inside arrays and nested JSON. A later save can change the text to `2024-01-02T03:04:05.000Z`.

The timestamp represents the same time, but the identifier has changed.

## The task

[problem_statement.txt](problem_statement.txt) requires exact field types and values through storage and session caches. Actual date fields must still return dates.

[new_tests.ts](new_tests.ts) tests two timestamp strings across seven routes, giving 14 cases. The routes cover database serialization, compact cookies, two JWT signing paths, JWE cookies, and two secondary-storage formats.

The tests also check user and session updates, genuine dates, nulls, empty arrays, and private output fields. All eight cookie cases require zero backing user/session reads on a cache hit. A cache-disabled request must perform a backing read, proving the observer can detect fallback. JWT signing-key reads are allowed. Secondary storage uses an in-memory provider, not a live Redis server.

## The fix

[solution.patch](solution.patch) changes eight production files. It reads stored JSON without guessing which strings are dates, then restores only fields declared as dates in the schema. The same rule applies during reads and updates.

## Verify it

From the repository root:

```sh
python3 run_demo.py field-roundtrip
```

| Version | Existing related tests | New tests |
| --- | --- | --- |
| Original | 488 pass | 14 fail |
| Fixed | 488 pass | 14 pass |

Reports are in [evidence](evidence). The 488 tests are selected affected-area tests, not the entire repository suite. Client-side parsing and standalone `getCookieCache` behavior are outside scope.

## Audit the task

```sh
python3 run_field_audit.py --jobs 2
python3 verify_field_evidence.py
```

The audit repeats the original and fixed new tests six times each, checks all eight single-file reverts, rejects four incomplete fixes and a cookie-cache bypass, and accepts the existing JSON-cloning alternative. The unchanged reference fix remains eight production files.

Read [the guide review](GUIDELINE_REVIEW.md) and [the evidence index](evidence/README.md). Historical evidence is preserved separately with its original test patch and hashes. Current results apply to the strengthened test patch.

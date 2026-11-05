# Wildcard matching

`wildcardMatch` compiles a pattern into a reusable yes-or-no check. For example, `*.txt` matches `readme.txt`.

## The bug

```js
const match = wildcardMatch("*.txt", { flags: "g" });
match("readme.txt"); // true
match("readme.txt"); // false
match("readme.txt"); // true
```

The input stays the same, but the answer changes. Global and sticky regular expressions remember their previous position in `lastIndex`. The next call starts at that position instead of the beginning.

## The task

[statement.txt](statement.txt) asks for stable results across repeated calls while preserving the existing options. It describes the behavior without giving the fix.

[new_tests.ts](new_tests.ts) has six cases covering `g`, `y`, case-insensitive combinations, pattern arrays, and a custom separator. They repeat matching inputs and mix in nonmatching inputs.

## The fix

[solution.patch](solution.patch) adds one line before the regex check:

```js
regexp.lastIndex = 0;
```

Each call now starts at the beginning. Existing flags and matching rules stay intact.

## Verify it

From the repository root:

```sh
python3 run_demo.py wildcard
```

| Version | Existing related tests | New tests |
| --- | --- | --- |
| Original | 57 pass | 6 fail |
| Fixed | 57 pass | 6 pass |

The direct source check changes from `true false true` to `true true true`. Reports are in [evidence](evidence).

This is an internal utility export, not a top-level package API. The task demonstrates the helper bug. It does not establish an authentication failure, and its small size may make it too easy for a difficult-task dataset.

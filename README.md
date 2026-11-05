# Better Auth tasks

Two coding-agent tasks based on real Better Auth bugs. Each has a statement, regression tests, a reference fix, and a Docker replay.

Start with the wildcard task for a short walkthrough.

| Task | Bug | Reference fix |
| --- | --- | --- |
| [Wildcard matching](tasks/wildcard/README.md) | The same input can return `true`, `false`, then `true`. | Reset the regex position before each check. |
| [Field round trips](tasks/field-roundtrip/README.md) | Date-looking strings change type or content after storage. | Restore dates using the declared field types. |

Both use [Better Auth](https://github.com/better-auth/better-auth) at commit `e7200d132f5946490c19a389b5a89b31aeead4e7`.

## Run a demo

Requires Python 3.10+, Docker, and the base image described in [SETUP.md](SETUP.md).

```sh
python3 run_demo.py wildcard
python3 run_demo.py field-roundtrip
```

Each command starts a disposable container, tests the original code, applies the reference fix, and tests again. The replay runs without network access. Reports stay in each task's `evidence` folder.

## Walkthrough order

1. Read the task README and statement.
2. Show `new_tests.ts` and explain what should fail.
3. Show `solution.patch` and explain the cause.
4. Run the demo and open its reports.

These tasks are locally verified. No model training, agent difficulty trials, or platform acceptance is claimed. The wildcard bug is in an internal helper, with no demonstrated sign-in failure.

This repository contains the answers and hidden tests for review. An evaluated agent should receive only the pinned upstream code and the task statement.

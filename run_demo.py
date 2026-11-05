#!/usr/bin/env python3
"""Replay either Better Auth task in a disposable offline container."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
TASKS = {"wildcard": (57, 6), "field-roundtrip": (488, 14)}


def verify_artifacts():
    hashes = json.loads((ROOT / "artifact-hashes.json").read_text())
    for name, expected in hashes.items():
        path = ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError(f"Task artifact changed: {name}")


def read_report(path, count, failures):
    root = ET.parse(path).getroot()
    cases = list(root.iter("testcase"))
    actual = {
        "tests": len(cases),
        "failures": sum(case.find("failure") is not None for case in cases),
        "errors": sum(case.find("error") is not None for case in cases),
        "skipped": sum(case.find("skipped") is not None for case in cases),
    }
    expected = {"tests": count, "failures": failures, "errors": 0, "skipped": 0}
    if actual != expected:
        raise RuntimeError(f"Unexpected results in {path}: {actual}; expected {expected}")
    if any(failure.get("type") == "HarnessError" for failure in root.iter("failure")):
        raise RuntimeError(f"The test runner reported an infrastructure failure: {path}")
    return actual, sorted((case.get("classname", ""), case.get("name", "")) for case in cases)


def replay(name, image, image_id, output_root):
    task = ROOT / "tasks" / name
    output = (output_root / name if output_root else task / "evidence").resolve()
    output.mkdir(parents=True, exist_ok=True)
    output.chmod(0o777)
    summary_path = output / "results.json"
    summary_path.unlink(missing_ok=True)
    command = [
        "docker", "run", "--rm", "--network", "none",
        "--mount", f"type=bind,source={task},target=/review,readonly",
        "--mount", f"type=bind,source={output},target=/results",
        image_id, "bash", "/review/verification/replay.sh",
    ]
    result = subprocess.run(command, text=True, capture_output=True)
    (output / "console.log").write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f"{name} replay failed. Read {output / 'console.log'}")
    if (output / "exits.txt").read_text().strip() != "0 1 0 0":
        raise RuntimeError(f"Unexpected runner exit codes for {name}")
    base_count, new_count = TASKS[name]
    expected = {
        "base-before": (base_count, 0), "new-before": (new_count, new_count),
        "base-after": (base_count, 0), "new-after": (new_count, 0),
    }
    reports, names = {}, {}
    for stage, (count, failures) in expected.items():
        reports[stage], names[stage] = read_report(output / f"{stage}.xml", count, failures)
    for kind in ["base", "new"]:
        if names[f"{kind}-before"] != names[f"{kind}-after"]:
            raise RuntimeError(f"Different {kind} tests ran before and after the fix")
    summary = {
        "task": name,
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "base_commit": (task / "base_commit.txt").read_text().strip(),
        "image": image,
        "image_id": image_id,
        "runtime": (output / "runtime.txt").read_text().strip(),
        "reports": reports,
        "agent_trials": False,
        "platform_approved": False,
    }
    if name == "wildcard":
        before = (output / "source-before.txt").read_text().strip()
        after = (output / "source-after.txt").read_text().strip()
        if before != "g: true false true\ny: true false true" or after != "g: true true true\ny: true true true":
            raise RuntimeError("Direct wildcard reproduction did not match the expected before/after behavior")
        summary.update(source_before=before, source_after=after)
        print("Repeated calls before: true false true")
        print("Repeated calls after:  true true true")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"\n{name}")
    print("Version         Existing tests    New task tests")
    print(f"Original        {base_count} pass".ljust(34) + f"{new_count} fail")
    print(f"Reference fix   {base_count} pass".ljust(34) + f"{new_count} pass")
    print(f"Evidence: {summary_path}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=[*TASKS, "all"])
    parser.add_argument("--image", default="better-auth-tasks:base")
    parser.add_argument("--output-dir", type=Path, help="Write evidence into one subfolder per task here.")
    args = parser.parse_args()
    try:
        verify_artifacts()
        inspected = subprocess.run(
            ["docker", "image", "inspect", args.image, "--format", "{{.Id}}"],
            text=True, capture_output=True,
        )
        if inspected.returncode:
            raise RuntimeError(f"Cannot inspect Docker image {args.image}. Start Docker and follow the README setup steps.")
        image_id = inspected.stdout.strip()
        if not image_id.startswith("sha256:"):
            raise RuntimeError("Docker did not return an immutable image ID")
        for name in TASKS if args.task == "all" else [args.task]:
            replay(name, args.image, image_id, args.output_dir)
    except (OSError, ValueError, RuntimeError, ET.ParseError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

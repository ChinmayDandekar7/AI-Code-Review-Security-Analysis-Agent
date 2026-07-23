"""
Milestone 2 deliverable 4: validate agent detection accuracy across sample
Python and Java codebases containing known quality issues and vulnerabilities.

This runs both agents against fixtures with deliberately planted issues
(and their "safe" counterparts, to catch false positives) and checks that
every expected category is actually found -- plus that clean code produces
zero findings.

Run with:
    python -m tests.validate_agents
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.code_analysis_python import analyze_python as quality_python
from app.agents.code_analysis_java import analyze_java as quality_java
from app.agents.security_python import analyze_python_security as security_python
from app.agents.security_java import analyze_java_security as security_java

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Each entry: (fixture file, analyzer function, expected categories)
CASES = [
    (
        "vulnerable_sample.py",
        quality_python,
        {
            "Too Many Parameters", "God Class", "High Cyclomatic Complexity",
            "Mutable Default Argument", "Bare Except Clause",
            "Silently Swallowed Exception", "Magic Numbers", "Duplicate Code",
        },
    ),
    (
        "vulnerable_security_sample.py",
        security_python,
        {
            "Hardcoded Secret", "SQL Injection", "Command Injection",
            "Insecure Deserialization", "Dangerous Dynamic Execution",
            "Insecure Hashing Algorithm", "Cross-Site Scripting (XSS)",
            "Possible Broken Access Control",
        },
    ),
    (
        "VulnerableSample.java",
        quality_java,
        {
            "Too Many Parameters", "God Class", "Magic Numbers",
            "Empty Catch Block", "High Cyclomatic Complexity",
        },
    ),
    (
        "VulnerableSecuritySample.java",
        security_java,
        {
            "Hardcoded Secret", "SQL Injection", "Command Injection",
            "Insecure Deserialization", "Insecure Hashing Algorithm",
            "XML External Entity (XXE)", "Cross-Site Scripting (XSS)",
        },
    ),
]

CLEAN_CASES = [
    ("clean_sample.py", quality_python),
    ("clean_sample.py", security_python),
    ("CleanSample.java", quality_java),
    ("CleanSample.java", security_java),
]


def run():
    total_expected = 0
    total_found = 0
    all_passed = True

    print("=" * 70)
    print("DETECTION ACCURACY: vulnerable/smelly fixtures")
    print("=" * 70)

    for filename, analyzer, expected_categories in CASES:
        filepath = FIXTURES_DIR / filename
        code = filepath.read_text()
        findings = analyzer(code)
        found_categories = {f.category for f in findings}

        missing = expected_categories - found_categories
        extra = found_categories - expected_categories

        total_expected += len(expected_categories)
        total_found += len(expected_categories & found_categories)

        status = "PASS" if not missing else "FAIL"
        if missing:
            all_passed = False

        print(f"\n[{status}] {filename} via {analyzer.__module__}.{analyzer.__name__}")
        print(f"  Expected {len(expected_categories)} categories, "
              f"found {len(expected_categories & found_categories)}")
        if missing:
            print(f"  MISSING: {sorted(missing)}")
        if extra:
            print(f"  (extra categories also found, not necessarily wrong: {sorted(extra)})")

    print("\n" + "=" * 70)
    print("FALSE POSITIVE CHECK: clean fixtures (expect 0 findings each)")
    print("=" * 70)

    for filename, analyzer in CLEAN_CASES:
        filepath = FIXTURES_DIR / filename
        code = filepath.read_text()
        findings = analyzer(code)
        status = "PASS" if len(findings) == 0 else "FAIL"
        if len(findings) != 0:
            all_passed = False
        print(f"[{status}] {filename} via {analyzer.__module__}.{analyzer.__name__}: "
              f"{len(findings)} findings (expected 0)")

    print("\n" + "=" * 70)
    accuracy = (total_found / total_expected * 100) if total_expected else 0
    print(f"SUMMARY: {total_found}/{total_expected} expected categories detected "
          f"({accuracy:.1f}% recall on planted issues)")
    print(f"OVERALL: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")
    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run())

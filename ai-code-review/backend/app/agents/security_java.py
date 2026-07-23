"""
Security Vulnerability Agent — Java side.

Primarily pattern-based rather than deep semantic analysis: detecting
"a string built via concatenation flows into a dangerous sink" is exactly
the kind of check our own knowledge base documents as "greppable" (see
secure_coding_practices.md and owasp_top10.md) -- precise call-graph /
taint analysis is out of scope for this milestone, but line-level pattern
matching against known-dangerous sinks catches the large majority of real
occurrences of these bugs.
"""

import re
from .code_analysis_python import RawFinding
from .security_common import check_hardcoded_secrets

SQL_EXEC_PATTERN = re.compile(r"\.(execute|executeQuery|executeUpdate)\s*\(([^;]*)\)")
CONCAT_IN_PARENS = re.compile(r"\+")
STRING_LITERAL_ONLY = re.compile(r'^\s*"[^"]*"\s*$')

COMMAND_EXEC_PATTERNS = [
    re.compile(r"Runtime\.getRuntime\(\)\.exec\s*\("),
    re.compile(r"new\s+ProcessBuilder\s*\("),
]

HASH_PATTERN = re.compile(r'MessageDigest\.getInstance\s*\(\s*"(MD5|SHA-1|SHA1)"\s*\)', re.IGNORECASE)

XXE_FACTORY_PATTERNS = [
    re.compile(r"DocumentBuilderFactory\.newInstance\s*\("),
    re.compile(r"SAXParserFactory\.newInstance\s*\("),
    re.compile(r"XMLInputFactory\.newInstance\s*\("),
]
XXE_MITIGATION_HINT = re.compile(r"setFeature|FEATURE_SECURE_PROCESSING|disallow-doctype-decl")

DESERIALIZATION_PATTERN = re.compile(r"ObjectInputStream")
READ_OBJECT_PATTERN = re.compile(r"\.readObject\s*\(")

WRITER_OUTPUT_PATTERN = re.compile(r"\.(getWriter\(\)\.(println|write|print))\s*\(([^;]*)\)")


def _looks_concatenated(arg_text: str) -> bool:
    """True if the argument text contains string concatenation and isn't
    just a single plain string literal -- our proxy for "built from
    untrusted input" without doing real taint tracking."""
    if STRING_LITERAL_ONLY.match(arg_text):
        return False
    return "+" in arg_text


def check_sql_injection(code: str) -> list[RawFinding]:
    findings = []
    for i, line in enumerate(code.split("\n"), start=1):
        match = SQL_EXEC_PATTERN.search(line)
        if match and _looks_concatenated(match.group(2)):
            findings.append(RawFinding(
                category="SQL Injection",
                severity="critical",
                line_start=i,
                line_end=i,
                description=f"Line {i} calls .{match.group(1)}() with a string built "
                            f"via concatenation rather than a parameterized query. This "
                            f"allows an attacker to alter the query's logic via crafted input.",
                remediation="Use PreparedStatement with '?' placeholders and "
                            "setString()/setInt() etc. instead of concatenating values "
                            "directly into the SQL string.",
            ))
    return findings


def check_command_injection(code: str) -> list[RawFinding]:
    findings = []
    lines = code.split("\n")
    for i, line in enumerate(lines, start=1):
        for pattern in COMMAND_EXEC_PATTERNS:
            if pattern.search(line) and "+" in line:
                findings.append(RawFinding(
                    category="Command Injection",
                    severity="critical",
                    line_start=i,
                    line_end=i,
                    description=f"Line {i} builds a system command using string "
                                f"concatenation before executing it. If any part comes "
                                f"from untrusted input, this is a command injection risk.",
                    remediation="Pass command arguments as a separate array/list "
                                "(e.g. ProcessBuilder's varargs constructor) rather than "
                                "a single concatenated command string.",
                ))
    return findings


def check_insecure_hashing(code: str) -> list[RawFinding]:
    findings = []
    for i, line in enumerate(code.split("\n"), start=1):
        match = HASH_PATTERN.search(line)
        if match:
            findings.append(RawFinding(
                category="Insecure Hashing Algorithm",
                severity="high",
                line_start=i,
                line_end=i,
                description=f"Line {i} uses {match.group(1)}, a fast general-purpose "
                            f"hash unsuitable for passwords (brute-forceable at high "
                            f"speed) and cryptographically broken for collision resistance.",
                remediation="Use a slow, salted password-hashing algorithm "
                            "(BCrypt, SCrypt, or Argon2) instead.",
            ))
    return findings


def check_insecure_deserialization(code: str) -> list[RawFinding]:
    findings = []
    lines = code.split("\n")
    if not DESERIALIZATION_PATTERN.search(code):
        return findings
    for i, line in enumerate(lines, start=1):
        if READ_OBJECT_PATTERN.search(line):
            findings.append(RawFinding(
                category="Insecure Deserialization",
                severity="critical",
                line_start=i,
                line_end=i,
                description=f"Line {i} calls .readObject() on an ObjectInputStream. "
                            f"Deserializing untrusted data this way can trigger remote "
                            f"code execution via gadget chains in classes on the classpath.",
                remediation="Use a data format without executable semantics (JSON, "
                            "protocol buffers) for data crossing a trust boundary, or "
                            "restrict deserialization to an explicit allow-list of classes.",
            ))
    return findings


def check_xxe(code: str) -> list[RawFinding]:
    findings = []
    has_mitigation = bool(XXE_MITIGATION_HINT.search(code))
    if has_mitigation:
        return findings  # a setFeature/disable call appears somewhere in the file
    for i, line in enumerate(code.split("\n"), start=1):
        for pattern in XXE_FACTORY_PATTERNS:
            if pattern.search(line):
                findings.append(RawFinding(
                    category="XML External Entity (XXE)",
                    severity="medium",
                    line_start=i,
                    line_end=i,
                    description=f"Line {i} instantiates an XML parser factory with no "
                                f"visible external-entity-disabling configuration anywhere "
                                f"in this file. Default Java XML parser settings can allow "
                                f"external entity resolution, enabling file disclosure or SSRF. "
                                f"This is a reminder to verify configuration, not a confirmed "
                                f"vulnerability -- the mitigation may be applied elsewhere.",
                    remediation='Explicitly disable external entities, e.g. '
                                'factory.setFeature("http://apache.org/xml/features/'
                                'disallow-doctype-decl", true).',
                ))
    return findings


def check_xss(code: str) -> list[RawFinding]:
    findings = []
    for i, line in enumerate(code.split("\n"), start=1):
        match = WRITER_OUTPUT_PATTERN.search(line)
        if match and _looks_concatenated(match.group(3)):
            findings.append(RawFinding(
                category="Cross-Site Scripting (XSS)",
                severity="high",
                line_start=i,
                line_end=i,
                description=f"Line {i} writes a concatenated string directly to the "
                            f"response. If any part comes from request data, this renders "
                            f"unescaped user input into the page, enabling XSS.",
                remediation="HTML-encode any user-supplied data before writing it into "
                            "the response, or use a templating engine that auto-escapes "
                            "by default.",
            ))
    return findings


def analyze_java_security(code: str) -> list[RawFinding]:
    findings = check_hardcoded_secrets(code)
    findings.extend(check_sql_injection(code))
    findings.extend(check_command_injection(code))
    findings.extend(check_insecure_hashing(code))
    findings.extend(check_insecure_deserialization(code))
    findings.extend(check_xxe(code))
    findings.extend(check_xss(code))
    return findings

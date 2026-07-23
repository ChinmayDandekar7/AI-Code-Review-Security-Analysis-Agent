"""
Syntax validation for submitted code.
"""

import ast
import javalang


def validate_python(code: str) -> tuple[bool, list[str]]:
    try:
        ast.parse(code)
        return True, []
    except SyntaxError as e:
        return False, [f"Line {e.lineno}: {e.msg}"]


def validate_java(code: str) -> tuple[bool, list[str]]:
    try:
        javalang.parse.parse(code)
        return True, []
    except javalang.parser.JavaSyntaxError as e:
        description = getattr(e, "description", "") or "Syntax error"
        position = getattr(e, "at", None)
        message = f"{description} (near {position})" if position else description
        return False, [message]
    except Exception as e:
        return False, [f"Parse error: {str(e)}"]


def validate(code: str, language: str) -> tuple[bool, list[str]]:
    if language == "python":
        return validate_python(code)
    elif language == "java":
        return validate_java(code)
    raise ValueError(f"Unsupported language: {language}")

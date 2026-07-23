Python Secure Coding and Code Quality Best Practices

Dangerous built-ins and functions
Avoid eval() and exec() on any input that isn't fully trusted and
controlled by the developer — they execute arbitrary Python code. Avoid
pickle.loads() on untrusted data; unlike JSON, unpickling can execute
arbitrary code as a side effect of deserialization. Avoid subprocess calls
with shell=True combined with untrusted input, since it invokes a shell
and is vulnerable to command injection; prefer passing arguments as a list
with shell=False.

Mutable default arguments
def f(items=[]): is a classic Python pitfall — the default list is created
once at function definition time and shared across all calls that don't
pass their own argument, leading to state leaking between unrelated calls.
Use None as the default and create the mutable object inside the function
body instead.

Exception handling
Avoid bare except: clauses that swallow every exception including
KeyboardInterrupt and SystemExit; catch specific exception types. Avoid
except Exception: pass, which silently discards errors and makes bugs
much harder to diagnose later. Use context managers (the with statement)
for resource cleanup — files, locks, network connections — rather than
manual try/finally blocks, which are easy to get wrong.

Type hints and readability
Type hints (def f(x: int) -> str:) make code easier to review and let
static analysis tools (mypy) catch a class of bugs before runtime. They
aren't enforced by the interpreter, so they're a documentation and
tooling aid rather than a security boundary, but they meaningfully improve
reviewability.

Common code smells in Python
Long functions doing multiple unrelated things (a strong candidate for
splitting along single-responsibility lines); deeply nested conditionals
that could be flattened with early returns; using string formatting to
build SQL or shell commands instead of parameterized APIs; catching
exceptions only to re-raise them unchanged (dead code); mutable global
state modified from multiple functions, making behavior hard to reason
about.

Style
PEP 8 is the standard style guide — consistent naming (snake_case for
functions and variables, PascalCase for classes), reasonable line length,
and consistent import ordering. Tools like ruff, flake8, or black automate
most of this and should run as part of CI rather than relying on manual
review.

Detection tip for a code review agent: eval/exec/pickle.loads/subprocess
calls are all greppable and worth flagging automatically; mutable default
arguments are a simple AST pattern (a list, dict, or set literal as a
default parameter value) that's cheap to detect with high precision.

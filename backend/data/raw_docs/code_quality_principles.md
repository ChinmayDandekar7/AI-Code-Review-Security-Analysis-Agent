Code Quality Principles and Common Code Smells

This document covers structural and design-level code quality concerns,
independent of any specific security vulnerability — the kind of issues a
Code Analysis Agent focuses on, as distinct from a Security Vulnerability
Agent.

Code Smells
A code smell is a surface indication that usually corresponds to a deeper
problem in the system, without being a bug itself. Common examples:

- Long Method: a function that's grown to do too much and is hard to read
  in one pass. Usually fixable by extracting cohesive chunks into
  well-named helper functions.
- God Class: a single class that has accumulated far more responsibility
  than it should, often becoming a dumping ground for unrelated logic.
- Duplicate Code: the same logic copy-pasted in multiple places instead of
  extracted once; a bug fix in one copy is easy to forget applying to the
  others.
- Feature Envy: a method that interacts more with another class's data
  than its own, suggesting it's defined on the wrong class.
- Magic Numbers/Strings: unexplained literal values embedded in logic
  (e.g. `if status == 3`) instead of a named constant or enum that
  documents what the value means.
- Shotgun Surgery: a single logical change requires editing many
  unrelated files/classes, indicating responsibilities are scattered
  rather than cohesive.
- Dead Code: unreachable or unused code left in the codebase, adding
  maintenance burden and confusion with no benefit.

SOLID Principles
A widely used set of object-oriented design principles:
- Single Responsibility: a class should have one reason to change.
- Open/Closed: open for extension, closed for modification — prefer
  adding new code over editing working code to support a new case.
- Liskov Substitution: a subclass should be usable anywhere its parent
  class is expected, without breaking correctness.
- Interface Segregation: prefer several small, specific interfaces over
  one large, general-purpose one that forces implementers to support
  methods they don't need.
- Dependency Inversion: depend on abstractions, not concrete
  implementations, particularly across module boundaries.

Complexity Metrics
Cyclomatic complexity counts the number of independent paths through a
function's control flow (branches, loops, conditionals) — a rough proxy
for how hard it is to test and reason about. Functions with high
cyclomatic complexity are good candidates for refactoring into smaller
pieces, each independently testable.

Naming and Readability
Names should describe what something is or does, not how it's implemented.
Prefer clarity over brevity for anything beyond a very short-lived loop
variable. Consistent naming conventions across a codebase reduce cognitive
load when moving between files.

DRY (Don't Repeat Yourself)
Every piece of knowledge should have a single, unambiguous representation
in a system. This is about duplicated *logic* and *decisions*, not merely
duplicated *text* — two pieces of code that look similar but represent
unrelated business rules are not a DRY violation just because they're
textually alike.

Detection tip for a code review agent: function length and cyclomatic
complexity are both mechanically measurable directly from an AST, making
them good first-pass signals before any semantic analysis is attempted.

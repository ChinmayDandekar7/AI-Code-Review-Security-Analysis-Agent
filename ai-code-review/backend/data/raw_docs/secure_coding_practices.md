Secure Coding Standards — General Practices

These are language-agnostic practices that apply regardless of whether the
codebase is Python, Java, or anything else. They complement the
vulnerability-specific documents in this knowledge base by focusing on
habits that prevent whole classes of issues.

Input Validation
Treat all input as untrusted until validated: form fields, query
parameters, HTTP headers, file uploads, and data read from a database that
was originally written by a different, less-trusted code path. Prefer
allow-listing (define what valid input looks like and reject everything
else) over block-listing (trying to enumerate bad input, which is always
incomplete). Validate on the server even if client-side validation also
exists — client-side checks are a UX convenience, not a security boundary.

Output Encoding
Data should be encoded appropriately for the context it's being rendered
into (HTML body, HTML attribute, JavaScript string, SQL query, shell
command, URL). The same piece of data may need different encoding
depending on where it's placed. This is the core defense against both XSS
and injection-style vulnerabilities.

Authentication and Session Management
Use established libraries and frameworks for authentication rather than
implementing it from scratch. Enforce a reasonable minimum password policy
without being so strict it drives users toward predictable patterns.
Rotate and expire session tokens, invalidate them on logout, and set
secure cookie flags (HttpOnly, Secure, SameSite).

Error Handling and Logging
Error messages returned to the end user should never include stack traces,
internal file paths, database schema details, or other implementation
details that help an attacker map the system. Full error detail should
still be logged server-side for debugging, just not exposed in the
response. Logs themselves should never contain secrets (passwords, tokens,
credit card numbers) or unredacted personal data.

Least Privilege
Every component — a database account, a service's IAM role, a function's
file-system access — should hold the minimum permissions needed to do its
job, nothing more. This limits the blast radius when something does go
wrong, whether that's a bug or a successful attack.

Dependency Management
Pin dependency versions, review what a new dependency actually does before
adding it, and keep dependencies updated against known vulnerabilities.
A codebase's attack surface includes every line of code in every library
it imports, not just the code the team wrote directly.

Secure Defaults
Configuration should default to the secure option, requiring an explicit
opt-in to loosen it, not the other way around. Examples: TLS verification
enabled by default, CORS closed by default, debug mode off by default in
production builds.

Detection tip for a code review agent: many of the above translate into
concrete, greppable patterns — e.g. debug flags left on, verbose exception
handlers that return str(exception) directly to an HTTP response, or
overly broad CORS/permission configuration blocks.

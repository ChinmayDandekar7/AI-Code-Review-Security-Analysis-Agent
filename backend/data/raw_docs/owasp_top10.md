OWASP Top 10 — Core Vulnerability Categories

The OWASP Top 10 is the industry-standard awareness list of the most
critical web application security risks, maintained by the Open Worldwide
Application Security Project. This document summarizes the categories not
already covered in detail elsewhere in this knowledge base (SQL injection
and hardcoded secrets have their own dedicated documents).

Broken Access Control
Occurs when restrictions on what authenticated users are allowed to do are
not properly enforced. Common patterns: trusting a client-supplied user ID
or role instead of re-checking permissions server-side on every request;
missing authorization checks on API endpoints that exist alongside a
protected UI; insecure direct object references (e.g. changing an
`id=1042` in a URL to access another user's record). Primary defense: deny
by default, enforce access control checks on the server for every request,
and avoid relying on hiding a UI element as the only protection.

Cross-Site Scripting (XSS)
Occurs when untrusted input is rendered into a web page without proper
escaping, allowing an attacker to run arbitrary JavaScript in a victim's
browser. Three variants: stored (payload saved server-side, e.g. in a
comment), reflected (payload bounced back immediately from a request
parameter), and DOM-based (vulnerability lives entirely in client-side
script). Primary defense: context-aware output encoding (HTML, attribute,
JavaScript, or URL encoding depending on where the data lands), and using
frameworks that auto-escape by default (React, modern templating engines)
rather than manually concatenating strings into HTML.

Cross-Site Request Forgery (CSRF)
Occurs when a malicious site causes a victim's browser to submit an
unwanted request to an application the victim is already authenticated to,
exploiting the browser's automatic inclusion of cookies. Primary defense:
anti-CSRF tokens (a random value tied to the user's session, required on
state-changing requests), the `SameSite` cookie attribute, and requiring
re-authentication for sensitive actions.

Cryptographic Failures
Sensitive data exposed due to weak or missing encryption. Common patterns:
storing passwords with fast general-purpose hashes (MD5, SHA-1, plain
SHA-256) instead of a slow, salted algorithm designed for passwords
(bcrypt, scrypt, Argon2); transmitting sensitive data over plain HTTP
instead of TLS; using outdated cipher suites; hardcoding encryption keys
(see the dedicated hardcoded secrets document in this knowledge base).

Insecure Design
Security flaws that originate in the design phase, before a single line of
vulnerable code is written — e.g. a password reset flow with no rate
limiting, or a business workflow that assumes a step can't be skipped
without actually enforcing that server-side. Primary defense: threat
modeling during design, and building security requirements into user
stories rather than treating security purely as a code-review concern.

Security Misconfiguration
Includes running with unnecessary features enabled (verbose error pages
exposing stack traces in production, default admin accounts left active,
directory listing enabled), missing security headers, and overly permissive
CORS configuration (e.g. `Access-Control-Allow-Origin: *` combined with
credentialed requests).

Vulnerable and Outdated Components
Using libraries, frameworks, or runtime versions with known, publicly
disclosed vulnerabilities. Primary defense: dependency scanning tools
(e.g. `pip-audit`, `npm audit`, OWASP Dependency-Check) integrated into the
build pipeline, and a process for applying security patches promptly.

Identification and Authentication Failures
Weaknesses in how an application confirms a user's identity: allowing weak
or default passwords, missing multi-factor authentication for sensitive
accounts, exposing session IDs in URLs, and failing to invalidate sessions
on logout or after a period of inactivity.

Server-Side Request Forgery (SSRF)
Occurs when an application fetches a remote resource using a URL supplied
(directly or indirectly) by the user, without validating that the
destination is safe — allowing an attacker to make the server issue
requests to internal-only services (e.g. cloud metadata endpoints).
Primary defense: allow-list permitted destination hosts/schemes rather than
trying to block-list dangerous ones.

Detection tip for a code review agent: for each category above, the
underlying pattern to search for is "untrusted input reaching a sensitive
sink without validation, encoding, or an authorization check in between" —
whether that sink is a SQL query, an HTML template, a file path, a URL
fetch, or an access-control decision.

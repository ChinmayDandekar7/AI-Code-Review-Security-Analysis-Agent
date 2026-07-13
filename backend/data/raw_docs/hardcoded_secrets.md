Hardcoded Secrets and Credentials

Hardcoding API keys, passwords, database credentials, or private keys
directly in source code is a common and serious vulnerability. Once
committed to version control, a secret is effectively permanent -- it
remains in history even after later removal, and is exposed to anyone
with repository access, including in public repos scraped by automated
credential-harvesting bots within minutes of being pushed.

Primary defense: load secrets from environment variables or a dedicated
secrets manager (AWS Secrets Manager, HashiCorp Vault, Doppler, or even a
.env file excluded from version control via .gitignore for local dev).

Detection patterns for a code review agent:
- String literals assigned to variables named key, secret, password, token,
  api_key, or similar, especially when the literal looks like a plausible
  credential (long alphanumeric string, base64-looking, starts with a known
  prefix like "sk-" or "AKIA").
- Connection strings with embedded credentials
  (e.g. postgres://user:password@host/db).
- Private key material (-----BEGIN PRIVATE KEY-----) committed as a file
  or inline string.

Example of a vulnerable pattern:
  API_KEY = "sk-live-51H8xJ2eZvKYlo2C..."

Example of the fix:
  import os
  API_KEY = os.environ["API_KEY"]

If a secret is found to have been committed, rotating it is mandatory --
removing it from the latest commit is not sufficient, since it remains
recoverable from git history.

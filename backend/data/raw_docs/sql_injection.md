SQL Injection Prevention

SQL injection occurs when untrusted input is concatenated directly into a SQL
query string, allowing an attacker to alter the query's logic. This is
consistently ranked among the most critical web application security risks.

Primary defense: use parameterized queries (prepared statements) so that
user input is always treated as data, never as executable SQL code. Every
major language and framework provides this: PreparedStatement in Java,
parameterized cursor execution in Python's DB-API (sqlite3, psycopg2), and
query builders like SQLAlchemy or Hibernate that parameterize by default.

Secondary defenses, used in addition to parameterized queries, not instead of:
- Allow-list input validation for identifiers that cannot be parameterized
  (e.g. table or column names chosen dynamically).
- Least-privilege database accounts, so a successful injection has limited
  blast radius.
- Escaping is a weak fallback and should only be used when parameterized
  queries are genuinely unavailable for a specific driver or ORM edge case.

Example of a vulnerable pattern:
  query = "SELECT * FROM users WHERE username = '" + username + "'"

Example of the fix:
  cursor.execute("SELECT * FROM users WHERE username = %s", (username,))

Detection tip for a code review agent: flag any string concatenation or
f-string/format-string interpolation feeding directly into a SQL execution
call, regardless of language.

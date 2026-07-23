Java Secure Coding and Code Quality Best Practices

Unsafe deserialization
ObjectInputStream.readObject() on untrusted data is a well-known source of
remote code execution in Java applications, since deserialization can
trigger arbitrary code via gadget chains in classes already present on the
classpath. Prefer data formats that don't carry executable semantics
(JSON, protocol buffers) for any data crossing a trust boundary, and if
Java serialization is unavoidable, use an allow-list of permitted classes.

XML External Entity (XXE) prevention
Default XML parser configurations in Java historically allow external
entity resolution, which can be abused to read local files or perform
SSRF. Disable DOCTYPE declarations and external entity processing
explicitly when configuring a DocumentBuilderFactory, SAXParserFactory, or
XMLInputFactory, rather than relying on defaults.

Exception handling
Avoid catching Exception or Throwable broadly and swallowing it with an
empty catch block — this hides real failures and makes debugging
production issues far harder. Catch the most specific exception type that
makes sense, and always either handle the error meaningfully or rethrow
it (possibly wrapped in a more context-specific exception).

Resource management
Use try-with-resources for anything implementing AutoCloseable (streams,
database connections, file handles) instead of manual close() calls in a
finally block, which are easy to write incorrectly (e.g. forgetting a
null check, or a close() call that itself throws and masks the original
exception).

Generics and raw types
Avoid raw types (List instead of List<String>) — they defeat the compiler's
type checking and reintroduce the class of bugs generics were designed to
eliminate. Prefer immutable objects where practical (final fields, no
setters) since they're inherently thread-safe and easier to reason about.

Common code smells in Java
God classes that accumulate unrelated responsibilities over time; long
parameter lists that would be clearer as a dedicated parameter object;
excessive use of static mutable state, which complicates testing and
concurrency reasoning; deeply nested try/catch blocks; string
concatenation for building SQL queries instead of PreparedStatement.

Concurrency
Shared mutable state accessed from multiple threads without synchronization
(or without using a concurrent-safe collection from java.util.concurrent)
is a common source of subtle, hard-to-reproduce bugs. Prefer immutability
and higher-level concurrency utilities over manual synchronized blocks
where possible.

Detection tip for a code review agent: ObjectInputStream.readObject and
raw XML parser factory instantiation without explicit feature-disabling
calls are both strong, greppable signals worth flagging even without deep
data-flow analysis.

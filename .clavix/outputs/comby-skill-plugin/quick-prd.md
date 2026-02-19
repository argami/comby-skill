# Comby Skill Plugin - Quick PRD

Build a Claude Code plugin that reduces time and token consumption when parsing code during analysis and refactoring, using specialized tools like comby for pattern matching. The plugin provides a grep-compatible search interface with 5 output formats, pattern families for common code patterns (DATABASE_ACCESS, HTTP_ENDPOINTS, AUTH_BOUNDARIES, EXTERNAL_DEPENDENCIES, CODE_COMPLEXITY, CODE_DUPLICATION, ERROR_HANDLING), and vulnerability detection for security issues (SQL injection, XSS, hardcoded secrets, command injection). Supports Python, Go, Ruby, Rust, and PHP.

Core features include a Claude Code plugin with seamless workflow integration (pre/post-tool-use hooks), SQLite-based memory layer with vector embeddings for similarity search and graph relations between patterns, and an extensible pattern detection system. Built with Python 3.10+, Ivoire for BDD testing, Ruff for linting, and SQLite for persistence.

Explicitly out of scope: mobile app support, cloud deployment/infrastructure, user authentication, and real-time collaboration features.

---

*Generated with Clavix Planning Mode*
*Generated: 2025-02-18T00:00:00Z*

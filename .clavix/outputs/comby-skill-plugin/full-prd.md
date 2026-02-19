# Product Requirements Document: Comby Skill Plugin

## Problem & Goal

**Problem**: Developers spend excessive time and tokens parsing code during analysis and refactoring tasks.

**Goal**: Reduce time and token consumption when parsing code + improve refactoring using specialized tools like comby.

---

## Requirements

### Must-Have Features

1. **Grep-compatible search interface**
   - Already exists in MVP (search with 5 output formats)
   - Regex pattern matching
   - Recursive directory traversal with glob filtering
   - Multiple output formats: default, JSON, CSV, lines, count

2. **Pattern families for common code patterns**
   - High priority: DATABASE_ACCESS, HTTP_ENDPOINTS, AUTH_BOUNDARIES, EXTERNAL_DEPENDENCIES
   - Medium priority: CODE_COMPLEXITY, CODE_DUPLICATION, ERROR_HANDLING
   - Support for Python, Go, Ruby, Rust, PHP

3. **Vulnerability detection with security patterns**
   - SQL Injection detection
   - XSS patterns
   - Hardcoded secrets detection
   - Command injection detection
   - Unsafe deserialization detection

4. **Claude Code plugin integration**
   - Plugin manifest with commands and hooks
   - Seamless workflow integration
   - Pre-tool-use and post-tool-use hooks
   - Optional file-change and pre-commit analysis hooks

5. **Graph/vector memory for improved reasoning**
   - SQLite-based persistence
   - Vector embeddings for similarity search
   - Graph relations between patterns
   - Analysis history and snapshots

### Technical Requirements

- Python 3.10+
- Ivoire for BDD testing
- Ruff for linting/formatting
- SQLite for memory layer persistence
- sentence-transformers or similar for embeddings

### Supported Languages

- Python (priority)
- Go (priority)
- Ruby (priority)
- Rust (priority)
- PHP (priority)

---

## Out of Scope

- Mobile app support
- Cloud deployment/infrastructure
- User authentication system
- Real-time collaboration features

---

## Additional Context

- Prioritize pattern detection for Python, Go, Ruby, Rust, and PHP
- Focus on developer productivity and code analysis efficiency
- Target use case: AI-assisted code refactoring and security analysis

---

## Implementation Phases

### Phase 1: Complete Plugin (High Priority)
- Documentation (README_PLUGIN.md, PATTERNS.md, SECURITY-CHECKS.md, EXAMPLES.md)
- Plugin scripts (utils.py, search.py, analyze.py)
- Plugin assets (templates, search-patterns.json)
- Optional hooks implementation

### Phase 2: Expand Pattern Families (Medium Priority)
- DATABASE_ACCESS, HTTP_ENDPOINTS, AUTH_BOUNDARIES, EXTERNAL_DEPENDENCIES
- CODE_COMPLEXITY, CODE_DUPLICATION, ERROR_HANDLING
- PatternMatcher refactoring
- CLI updates with new flags

### Phase 3: Memory Layer (Lower Priority)
- SQLite schema implementation
- Vector embeddings integration
- Graph relations
- Memory API

---

*Generated with Clavix Planning Mode*
*Generated: 2025-02-18T00:00:00Z*

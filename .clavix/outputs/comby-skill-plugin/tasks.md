# Implementation Plan

**Project**: comby-skill-plugin
**Generated**: 2025-02-18T00:00:00Z
**Execution Mode**: Multi-agent parallel execution

---

## Technical Context & Standards

*Detected Stack & Patterns*
- **Architecture**: Python CLI tool with plugin architecture
- **Framework**: Python 3.10+ with Click/Argparse CLI
- **Linting**: Ruff (line-length: 120, py310)
- **Testing**: Ivoire BDD
- **Persistence**: SQLite (planned for memory layer)
- **Conventions**: snake_case functions, PascalCase classes, type hints required

---

## PHASE 1: Complete Plugin Documentation (PARALLEL EXECUTION)

### Task Group 1.1: Documentation Files (Can run in parallel - no dependencies)

- [x] **1.1.1 Complete README_PLUGIN.md** (phase-1-docs-01)
  > **Implementation**: Edit `README_PLUGIN.md`
  > **Details**: Add: general description, installation via Claude Code, commands reference (/comby-search, /comby-analyze, /comby-inventory), configuration options, usage examples, troubleshooting section

- [x] **1.1.2 Create references/PATTERNS.md** (phase-1-docs-02)
  > **Implementation**: Create `references/PATTERNS.md`
  > **Details**: Document search patterns for Python, Go, Ruby, Rust, PHP. Include regex examples for: function definitions, class definitions, imports, TODO comments, URLs, secrets. Add CLI flag examples (-i, -C, --format)

- [x] **1.1.3 Create references/SECURITY-CHECKS.md** (phase-1-docs-03)
  > **Implementation**: Create `references/SECURITY-CHECKS.md`
  > **Details**: Document security patterns: SQL injection (`.execute(|cursor.execute`), XSS (`innerHTML|document.write`), hardcoded secrets (password|api_key|secret), command injection (os.system|subprocess), unsafe deserialization (pickle.loads|yaml.load). Include remediation suggestions for each

- [x] **1.1.4 Create references/EXAMPLES.md** (phase-1-docs-04)
  > **Implementation**: Create `references/EXAMPLES.md`
  > **Details**: Create 5 example workflows: (1) Pre-refactoring analysis - find all DB calls before migration, (2) Security audit - scan for vulnerabilities, (3) Architecture mapping - list all HTTP endpoints, (4) Code inventory - generate function/class list, (5) CI/CD integration - automated security checks

### Task Group 1.2: Plugin Scripts (Dependencies: 1.1.x not strict - can partially parallel)

- [x] **1.2.1 Create scripts/utils.py** (phase-1-scripts-01)
  > **Implementation**: Create `scripts/utils.py`
  > **Details**: Implement: `run_comby_command(pattern, path, format)` - executes CLI, `parse_json_output(json_str)` - parses JSON results, `format_results(results, format)` - formats for Claude, `validate_pattern(pattern)` - validates regex, `get_file_info(path)` - returns file metadata. Use subprocess for CLI calls

- [x] **1.2.2 Create scripts/search.py** (phase-1-scripts-02)
  > **Implementation**: Create `scripts/search.py`
  > **Details**: Implement: `search_pattern(pattern, path, **kwargs)` - main search wrapper, `search_functions(lang, path)` - finds def/fn patterns, `search_classes(lang, path)` - finds class patterns, `search_imports(lang, path)` - finds import statements, `search_security_patterns(path)` - runs security patterns. Import and use utils.py

- [x] **1.2.3 Create scripts/analyze.py** (phase-1-scripts-03)
  > **Implementation**: Create `scripts/analyze.py`
  > **Details**: Implement: `analyze_file(filepath)` - single file analysis, `analyze_directory(dirpath, recursive)` - recursive analysis, `check_security(path)` - runs security patterns, `check_quality(path)` - runs quality patterns, `generate_report(results, format)` - generates report. Import and use utils.py

### Task Group 1.3: Plugin Assets (No dependencies - can parallel with 1.2)

- [x] **1.3.1 Create assets/example-project.claude.md** (phase-1-assets-01)
  > **Implementation**: Create `assets/example-project.claude.md`
  > **Details**: Template with: Claude Code project config example, recommended exclude patterns (node_modules, .git, __pycache__), suggested hooks config (enable preToolUse for security), pattern families to enable

- [x] **1.3.2 Create assets/search-patterns.json** (phase-1-assets-02)
  > **Implementation**: Create `assets/search-patterns.json`
  > **Details**: JSON with: patterns grouped by language, each with metadata (id, name, pattern, severity, category, description). Include security patterns, code patterns, import patterns. Schema: `{ "patterns": [{ "id": "", "name": "", "pattern": "", "severity": "high|medium|low", "category": "", "description": "" }] }`

### Task Group 1.4: Optional Hooks (Dependency: 1.2 complete)

- [x] **1.4.1 Create hooks/file-change-analysis.js** (phase-1-hooks-01)
  > **Implementation**: Create `hooks/file-change-analysis.js`
  > **Details**: Implement `onFileChange(event)` handler: detect file extension, run relevant pattern analysis, debounce with 500ms delay, limit to 5 analyses per minute. Use dynamic import of comby-skill CLI

- [x] **1.4.2 Create hooks/pre-commit-analysis.js** (phase-1-hooks-02)
  > **Implementation**: Create `hooks/pre-commit-analysis.js`
  > **Details**: Implement `onPreCommit(event)` handler: get staged .py/.js/.go files, run security pattern scan, report findings, optional block on HIGH severity. Exit code 1 to block, 0 to allow

---

## PHASE 2: Expand Pattern Families (PARALLEL EXECUTION)

### Task Group 2.1: High Priority Patterns (Can run in parallel - separate files)

- [x] **2.1.1 Create DATABASE_ACCESS pattern** (phase-2-patterns-01)
  > **Implementation**: Create `src/comby_skill/patterns/database_access.py`
  > **Details**: Implement detector for: raw SQL (`execute(|cursor.execute`), ORM (Django: `.filter(|.get(`, SQLAlchemy: `session.query(|.filter(`), migrations (`class Migration`), transactions (`begin(|commit(`). Use SearchEngine. Support Python first

- [x] **2.1.2 Create HTTP_ENDPOINTS pattern** (phase-2-patterns-02)
  > **Implementation**: Create `src/comby_skill/patterns/http_endpoints.py`
  > **Details**: Implement detector for: Flask (`@app.route`), FastAPI (`@router.get|@router.post`), Django (`path(|re_path(`), Express (`app\.(get|post|put|delete)`). Extract method + path. Support Python + JS

- [x] **2.1.3 Create AUTH_BOUNDARIES pattern** (phase-2-patterns-03)
  > **Implementation**: Create `src/comby_skill/patterns/auth_boundaries.py`
  > **Details**: Implement detector for: auth decorators (`@login_required|@auth|@requires_auth`), middleware (`AuthenticationMiddleware`), permission checks (`if.*user.*is_(admin|staff)`), JWT (`jwt\.decode|jwt\.encode`), password handling (`bcrypt\.|hashpw`)

- [x] **2.1.4 Create EXTERNAL_DEPENDENCIES pattern** (phase-2-patterns-04)
  > **Implementation**: Create `src/comby_skill/patterns/external_deps.py`
  > **Details**: Implement detector for: HTTP calls (`requests\.(get|post|`, `fetch\(`, `http\.Client`), external services (AWS SDK, Stripe, SendGrid), retries (`@retry|tenacity`), error handling around external calls

### Task Group 2.2: Medium Priority Patterns (Can run in parallel - separate files)

- [x] **2.2.1 Create CODE_COMPLEXITY pattern** (phase-2-patterns-05)
  > **Implementation**: Create `src/comby_skill/patterns/complexity.py`
  > **Details**: Implement analyzer: count function lines (>50 warn, >100 alert), nested depth (>4 levels), parameter count (>5), cyclomatic complexity estimation. Return score 0-100

- [x] **2.2.2 Create CODE_DUPLICATION pattern** (phase-2-patterns-06)
  > **Implementation**: Create `src/comby_skill/patterns/duplication.py`
  > **Details**: Implement detector: hash code blocks (ignore whitespace/comments), threshold configurable (default 80% similarity), suggest extraction. Use AST or simple line comparison

- [x] **2.2.3 Create ERROR_HANDLING pattern** (phase-2-patterns-07)
  > **Implementation**: Create `src/comby_skill/patterns/error_handling.py`
  > **Details**: Implement detector: `try/except` blocks, bare `except:` (flag), swallowed exceptions (`except: pass`), error logging presence. Score error handling quality

### Task Group 2.3: Pattern Integration (Dependency: 2.1 + 2.2 complete)

- [x] **2.3.1 Refactor PatternMatcher** (phase-2-integration-01)
  > **Implementation**: Edit `src/comby_skill/pattern_matcher.py`
  > **Details**: Refactor to support pattern families: add `register_pattern(pattern_class)` method, add `get_patterns_by_category(category)` method, add `run_family(family_name, path)` method. Use registry pattern with decorators

- [x] **2.3.2 Update CLI with new flags** (phase-2-integration-02)
  > **Implementation**: Edit `src/comby_skill/cli.py`
  > **Details**: Add: `--focus PATTERN_FAMILY` flag to run specific family, `--list-patterns` command to list available, `--severity FILTER` to filter by severity, `--category FILTER` to filter by category. Update help text

- [x] **2.3.3 Add tests for new patterns** (phase-2-integration-03)
  > **Implementation**: Create `spec/patterns_spec.py`
  > **Details**: Add Ivoire BDD specs for: DATABASE_ACCESS (3 scenarios), HTTP_ENDPOINTS (3 scenarios), AUTH_BOUNDARIES (3 scenarios), EXTERNAL_DEPENDENCIES (2 scenarios), CODE_COMPLEXITY (2 scenarios), CODE_DUPLICATION (2 scenarios), ERROR_HANDLING (2 scenarios). Follow existing spec pattern in spec/search_spec.py

---

## PHASE 3: Memory Layer (PARALLEL EXECUTION)

### Task Group 3.1: SQLite Schema

- [x] **3.1.1 Create memory schema** (phase-3-memory-01)
  > **Implementation**: Create `src/comby_skill/memory/schema.sql`
  > **Details**: Define tables: `analysis_results(id, timestamp, path, patterns_found_json, severity_counts_json)`, `patterns_found(id, analysis_id, pattern_id, file, line, severity)`, `files_indexed(id, path, language, hash, last_analyzed)`, `snapshots(id, name, created_at, results_json)`. Add indexes on timestamp, path, pattern_id

### Task Group 3.2: Vector Embeddings

- [x] **3.2.1 Create embeddings module** (phase-3-memory-02)
  > **Implementation**: Create `src/comby_skill/memory/embeddings.py`
  > **Details**: Implement: `CodeEmbedding` class using sentence-transformers, `embed_code(code_snippet)` returns vector, `find_similar(query, top_k)` returns similar snippets, `cache_embeddings()` for performance. Handle model loading lazily

### Task Group 3.3: Graph Relations

- [x] **3.3.1 Create graph module** (phase-3-memory-03)
  > **Implementation**: Create `src/comby_skill/memory/graph.py`
  > **Details**: Implement: `PatternGraph` class, `add_pattern(file, pattern_type, line)`, `find_dependencies(file)` returns imported/importing files, `find_callers(function)` returns call sites, `export_dot()` for Graphviz visualization

### Task Group 3.4: Memory API

- [x] **3.4.1 Create memory API** (phase-3-memory-04)
  > **Implementation**: Create `src/comby_skill/memory/api.py`
  > **Details**: Implement: `store_analysis(results)` saves to SQLite, `query_similar(code_snippet)` uses embeddings, `get_history(path, limit)` returns past analyses, `create_snapshot(name)` saves current state, `compare_snapshots(id1, id2)` returns diff

---

## Multi-Agent Execution Notes

### Parallel Execution Groups (No Dependencies)

| Group | Tasks | Can Run Simultaneously |
|-------|-------|----------------------|
| **Docs-A** | 1.1.1, 1.1.2, 1.1.3, 1.1.4 | YES - 4 agents |
| **Scripts-A** | 1.2.1, 1.2.2, 1.2.3 | YES - 3 agents |
| **Assets** | 1.3.1, 1.3.2 | YES - 2 agents |
| **Patterns-High** | 2.1.1, 2.1.2, 2.1.3, 2.1.4 | YES - 4 agents |
| **Patterns-Medium** | 2.2.1, 2.2.2, 2.2.3 | YES - 3 agents |
| **Memory** | 3.1.1, 3.2.1, 3.3.1, 3.4.1 | YES - 4 agents |

### Sequential Dependencies

| Task | Depends On |
|------|-----------|
| 1.4.1, 1.4.2 | 1.2.x complete |
| 2.3.1 | 2.1.x + 2.2.x complete |
| 2.3.2 | 2.3.1 complete |
| 2.3.3 | 2.3.2 complete |

### Suggested Agent Allocation

- **Agent 1**: Documentation (1.1.x)
- **Agent 2**: Scripts (1.2.x)
- **Agent 3**: Assets (1.3.x) + Hooks (1.4.x after scripts)
- **Agent 4**: High Priority Patterns (2.1.x)
- **Agent 5**: Medium Priority Patterns (2.2.x)
- **Agent 6**: Integration (2.3.x) after patterns
- **Agent 7**: Memory Layer (3.x.x)

---

## Verification Checklist

### Phase 1 - Completion Criteria
- [ ] README_PLUGIN.md has installation, commands, config, examples, troubleshooting
- [ ] references/ has PATTERNS.md, SECURITY-CHECKS.md, EXAMPLES.md
- [ ] scripts/ has utils.py, search.py, analyze.py with all functions
- [ ] assets/ has example-project.claude.md, search-patterns.json
- [ ] hooks/ has file-change-analysis.js, pre-commit-analysis.js

### Phase 2 - Completion Criteria
- [ ] 7 pattern families implemented in src/comby_skill/patterns/
- [ ] PatternMatcher refactored with registry pattern
- [ ] CLI has --focus, --list-patterns, severity/category filters
- [ ] Tests exist for all new patterns

### Phase 3 - Completion Criteria
- [ ] SQLite schema creates all tables with indexes
- [ ] Embeddings module loads model and finds similar code
- [ ] Graph module tracks dependencies between files
- [ ] Memory API stores and retrieves analysis history

---

*Generated by Clavix /clavix:plan*
*Multi-agent parallel execution enabled*

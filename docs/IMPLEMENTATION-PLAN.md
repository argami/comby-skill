# Implementation Plan: Comby Skill Plugin

## Context

**Project**: Comby Skill - Code pattern analysis tool with Claude AI integration
**Current State**: Functional MVP (70%), partially implemented plugin
**Goal**: Complete plugin to 100% + expand detection patterns

---

## PHASE 1: Complete Claude Code Plugin

**Priority**: High | **Dependencies**: None

### 1.1 Plugin Documentation

#### 1.1.1 Complete README_PLUGIN.md
- [ ] General plugin description
- [ ] Installation instructions
- [ ] Available commands guide
- [ ] Optional configuration
- [ ] Usage examples
- [ ] Troubleshooting

**File**: `README_PLUGIN.md`

#### 1.1.2 Create references/PATTERNS.md
- [ ] Search patterns for Python
- [ ] Search patterns for JavaScript/TypeScript
- [ ] Search patterns for Go
- [ ] Search patterns for Ruby
- [ ] Generic patterns (TODO, secrets, URLs)
- [ ] Examples with flags

**File**: `references/PATTERNS.md`

#### 1.1.3 Create references/SECURITY-CHECKS.md
- [ ] SQL Injection patterns
- [ ] XSS patterns
- [ ] Hardcoded secrets detection
- [ ] Command injection
- [ ] Unsafe deserialization
- [ ] Insecure configurations
- [ ] Remediation suggestions

**File**: `references/SECURITY-CHECKS.md`

#### 1.1.4 Create references/EXAMPLES.md
- [ ] Example: Pre-refactoring analysis
- [ ] Example: Security audit workflow
- [ ] Example: Architecture mapping
- [ ] Example: Code inventory generation
- [ ] Example: CI/CD integration

**File**: `references/EXAMPLES.md`

---

### 1.2 Plugin Logic Scripts

#### 1.2.1 Create scripts/utils.py
- [ ] `run_comby_command()` - Execute CLI command
- [ ] `parse_json_output()` - Parse JSON output
- [ ] `format_results()` - Format results for Claude
- [ ] `validate_pattern()` - Validate regex patterns
- [ ] `get_file_info()` - Get file information

**File**: `scripts/utils.py`

#### 1.2.2 Create scripts/search.py
- [ ] `search_pattern()` - Search wrapper
- [ ] `search_functions()` - Find function definitions
- [ ] `search_classes()` - Find class definitions
- [ ] `search_imports()` - Find imports
- [ ] `search_security_patterns()` - Find security patterns
- [ ] Integration with `scripts/utils.py`

**File**: `scripts/search.py`

#### 1.2.3 Create scripts/analyze.py
- [ ] `analyze_file()` - Single file analysis
- [ ] `analyze_directory()` - Recursive analysis
- [ ] `check_security()` - Security checks
- [ ] `check_quality()` - Quality checks
- [ ] `generate_report()` - Generate report
- [ ] Integration with `scripts/utils.py`

**File**: `scripts/analyze.py`

---

### 1.3 Plugin Assets

#### 1.3.1 Create assets/example-project.claude.md
- [ ] Example template for users
- [ ] Recommended configuration
- [ ] Suggested exclusion patterns
- [ ] Recommended hooks

**File**: `assets/example-project.claude.md`

#### 1.3.2 Create assets/search-patterns.json
- [ ] Predefined patterns by language
- [ ] Common security patterns
- [ ] Quality patterns
- [ ] Metadata (severity, category, description)

**File**: `assets/search-patterns.json`

---

### 1.4 Optional Hooks

#### 1.4.1 Create hooks/file-change-analysis.js
- [ ] Implement `onFileChange()` handler
- [ ] Detect modified file type
- [ ] Trigger automatic analysis if relevant
- [ ] Rate limiting to avoid overload

**File**: `hooks/file-change-analysis.js`

#### 1.4.2 Create hooks/pre-commit-analysis.js
- [ ] Implement `onPreCommit()` handler
- [ ] Get staged files
- [ ] Execute security analysis
- [ ] Report found issues
- [ ] Block or warn option

**File**: `hooks/pre-commit-analysis.js`

---

## PHASE 2: Expand Pattern Families

**Priority**: Medium | **Dependencies**: Phase 1 completed

### 2.1 High Priority Patterns

#### 2.1.1 DATABASE_ACCESS Pattern Family
- [ ] Detect `db.execute()`, `cursor.execute()`
- [ ] Detect ORM calls (Django ORM, SQLAlchemy)
- [ ] Detect migrations
- [ ] Detect transactions
- [ ] Classify by type (SELECT, INSERT, UPDATE, DELETE)

**File**: `src/comby_skill/patterns/database_access.py`

#### 2.1.2 HTTP_ENDPOINTS Pattern Family
- [ ] Detect Flask routes (`@app.route`)
- [ ] Detect FastAPI routes (`@router.get`, `@router.post`)
- [ ] Detect Django URLs
- [ ] Detect Express.js routes
- [ ] Extract HTTP method and path

**File**: `src/comby_skill/patterns/http_endpoints.py`

#### 2.1.3 AUTH_BOUNDARIES Pattern Family
- [ ] Detect auth decorators (`@login_required`, `@auth`)
- [ ] Detect auth middleware
- [ ] Detect permission checks
- [ ] Detect JWT handling
- [ ] Detect password handling

**File**: `src/comby_skill/patterns/auth_boundaries.py`

#### 2.1.4 EXTERNAL_DEPENDENCIES Pattern Family
- [ ] Detect `requests.get/post`, `fetch()`
- [ ] Detect HTTP client usage
- [ ] Detect external service calls
- [ ] Classify by service (AWS, Stripe, etc.)
- [ ] Detect retries and error handling

**File**: `src/comby_skill/patterns/external_deps.py`

---

### 2.2 Medium Priority Patterns

#### 2.2.1 CODE_COMPLEXITY Pattern Family
- [ ] Calculate cyclomatic complexity
- [ ] Detect long functions (>50 lines)
- [ ] Detect nested depth (>4 levels)
- [ ] Detect parameter count (>5 params)
- [ ] Complexity score

**File**: `src/comby_skill/patterns/complexity.py`

#### 2.2.2 CODE_DUPLICATION Pattern Family
- [ ] Detect exact duplicate blocks
- [ ] Detect structural similarity
- [ ] Configurable similarity threshold
- [ ] Suggest function extraction
- [ ] Duplication score

**File**: `src/comby_skill/patterns/duplication.py`

#### 2.2.3 ERROR_HANDLING Pattern Family
- [ ] Detect `try/except` blocks
- [ ] Detect bare `except:`
- [ ] Detect swallowed exceptions
- [ ] Detect error logging
- [ ] Error handling score

**File**: `src/comby_skill/patterns/error_handling.py`

---

### 2.3 Pattern Integration

#### 2.3.1 Update PatternMatcher
- [ ] Refactor to support pattern families
- [ ] Pattern registration system
- [ ] Category-based configuration
- [ ] Unified output

**File**: `src/comby_skill/pattern_matcher.py`

#### 2.3.2 Update CLI
- [ ] Add `--focus` flag for pattern families
- [ ] Add `--list-patterns` command
- [ ] Output by severity
- [ ] Category filters

**File**: `src/comby_skill/cli.py`

#### 2.3.3 Tests for New Patterns
- [ ] Tests for DATABASE_ACCESS
- [ ] Tests for HTTP_ENDPOINTS
- [ ] Tests for AUTH_BOUNDARIES
- [ ] Tests for EXTERNAL_DEPENDENCIES
- [ ] Tests for CODE_COMPLEXITY
- [ ] Tests for CODE_DUPLICATION
- [ ] Tests for ERROR_HANDLING

**Directory**: `spec/`

---

## PHASE 3: Memory Layer (Optional)

**Priority**: Low | **Dependencies**: Phases 1 and 2

### 3.1 SQLite Schema
- [ ] `analysis_results` table
- [ ] `patterns_found` table
- [ ] `files_indexed` table
- [ ] `snapshots` table
- [ ] Optimized indexes

**File**: `src/comby_skill/memory/schema.sql`

### 3.2 Vector Embeddings
- [ ] Integrate sentence-transformers or similar
- [ ] Code embeddings
- [ ] Similarity search
- [ ] Embedding cache

**File**: `src/comby_skill/memory/embeddings.py`

### 3.3 Graph Relations
- [ ] Relationship model between patterns
- [ ] Dependencies between files
- [ ] Basic call graphs
- [ ] Visualization

**File**: `src/comby_skill/memory/graph.py`

### 3.4 Memory API
- [ ] `store_analysis()` - Save analysis
- [ ] `query_similar()` - Similarity search
- [ ] `get_history()` - Analysis history
- [ ] `create_snapshot()` - Create snapshot

**File**: `src/comby_skill/memory/api.py`

---

## Dependency Summary

```
PHASE 1 (Complete Plugin)
├── 1.1 Documentation (no dependencies)
├── 1.2 Scripts (depends on 1.1 partially)
├── 1.3 Assets (no dependencies)
└── 1.4 Optional hooks (depends on 1.2)

PHASE 2 (Pattern Families)
├── 2.1 High priority (depends on Phase 1)
├── 2.2 Medium priority (depends on 2.1)
└── 2.3 Integration (depends on 2.1 and 2.2)

PHASE 3 (Memory Layer)
└── Everything depends on Phases 1 and 2 completed
```

---

## Effort Estimation

| Phase | Tasks | New Files | Modified Files |
|-------|-------|-----------|----------------|
| 1.1   | 4     | 4         | 1              |
| 1.2   | 3     | 3         | 0              |
| 1.3   | 2     | 2         | 0              |
| 1.4   | 2     | 2         | 0              |
| 2.1   | 4     | 4         | 0              |
| 2.2   | 3     | 3         | 0              |
| 2.3   | 3     | 0         | 3              |
| 3.x   | 4     | 4         | 0              |

**Total**: 25 tasks, 22 new files, 4 modified files

---

## Verification

### Phase 1 - Completion Criteria
- [ ] `README_PLUGIN.md` with complete documentation
- [ ] `scripts/` with 3 functional Python files
- [ ] `references/` with 3 Markdown files
- [ ] `assets/` with 2 example files
- [ ] Optional hooks implemented
- [ ] Plugin installable and functional

### Phase 2 - Completion Criteria
- [ ] 7 pattern families implemented
- [ ] Tests for each pattern family
- [ ] CLI updated with new flags
- [ ] Documentation updated

### Phase 3 - Completion Criteria
- [ ] SQLite schema implemented
- [ ] Embeddings functional
- [ ] Basic graph relations
- [ ] Memory API documented

---

## Immediate Next Steps

1. **Start with 1.1.1** - Complete `README_PLUGIN.md`
2. **Parallelize 1.1.x** - Documentation can be done in parallel
3. **Then 1.2.x** - Logic scripts
4. **Finally 1.3.x and 1.4.x** - Assets and optional hooks

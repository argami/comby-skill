# Memory Layer Summary - Quick Reference

> 📖 **Para comparativa detallada** (antes/después con grep/rg vs Comby), consulta [Workflow Comparison](../01-GETTING-STARTED/WORKFLOW_COMPARISON.md) con 4 casos reales.

## What is the Memory Layer?

A **persistent, embedded knowledge system** that remembers patterns detected across analyses of a single repository.

**Key insight**: Instead of re-analyzing the same code repeatedly, build a growing database of insights that helps developers understand patterns, relationships, and evolution over time.

---

## The 3 Core Capabilities

### 1. **Storage & History** 💾

```
Analysis 1 (2026-01-15)        Analysis 2 (2026-01-20)        Analysis 3 (2026-01-30)
├─ 5 SQL_INJECTION            ├─ 4 SQL_INJECTION (1 fixed)   ├─ 3 SQL_INJECTION
├─ 8 MISSING_TYPE_HINTS       ├─ 7 MISSING_TYPE_HINTS        ├─ 6 MISSING_TYPE_HINTS
└─ Total: 13 patterns         └─ Total: 11 patterns          └─ Total: 9 patterns

Evolution: 13 → 11 → 9 (steady improvement)
```

**Use cases**:
- "What patterns are still in this file?"
- "How many critical issues were fixed since last week?"
- "Show me the evolution of src/auth.py"

### 2. **Vector Search** 🔍

```
Query: "SQL injection using user input"
       ↓
       [Search similar patterns by code semantics]
       ↓
Results:
├─ src/auth.py:42 (95% similar) - "query = ... + user_id"
├─ src/api.py:156 (87% similar) - "f\"SELECT ... {username}\""
├─ src/user.py:85 (81% similar) - "\"DELETE...\" + id"
└─ [Enables refactoring opportunities]
```

**Use cases**:
- "Find all SQL injections like the one in line 42"
- "Show me similar patterns across the codebase"
- "Extract repeated patterns into a single fix"

### 3. **Relationship Graph** 🕸️

```
Pattern 5 (SQL_INJECTION @ auth.py:42)
   ├─ [depends_on] → Pattern 10 (INPUT_VALIDATION @ auth.py:38)
   │                 [confidence: 95%]
   │
   ├─ [same_file] → Pattern 8 (MISSING_TYPE_HINTS @ auth.py:15)
   │
   ├─ [related_to] → Pattern 12 (SQL_INJECTION @ api.py:156)
   │                 [confidence: 89%]
   │
   └─ [conflicts_with] → Pattern 3 (AUTH_BOUNDARIES @ auth.py:50)
                        [confidence: 72%]
```

**Use cases**:
- "What patterns are related to this one?"
- "Which patterns must I fix first (critical path)?"
- "What's the impact of fixing this one?"
- "Are there conflicting fixes?"

---

## Architecture at a Glance

```
┌──────────────────────────────────────────────────┐
│ Comby Skill Memory Layer                         │
├──────────────────────────────────────────────────┤
│                                                  │
│ 1. VECTOR DB (Embeddings)                        │
│    ├─ Store 768-dim vectors per pattern          │
│    ├─ Enable similarity search (cosine)          │
│    └─ Fast: <50ms per query                      │
│                                                  │
│ 2. GRAPH DB (Relationships)                      │
│    ├─ Nodes: Detected patterns                   │
│    ├─ Edges: Relations (depends_on, related, etc│
│    └─ Enable: context, dependencies, clusters   │
│                                                  │
│ 3. TIMESERIES (History)                          │
│    ├─ Snapshots: Analysis results over time      │
│    ├─ File evolution: Pattern changes per file   │
│    └─ Enable: tracking improvements              │
│                                                  │
│ 4. STORAGE (SQLite)                              │
│    ├─ Single .comby/memory.db file               │
│    ├─ ~5KB per pattern                           │
│    ├─ Scales to 10K+ patterns easily             │
│    └─ Zero external dependencies                 │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Database | SQLite | Embedded, single file, no server |
| Vector Store | sqlite-vec extension | Native SQL, HNSW indexing, fast |
| Embeddings | Deterministic hashing | Lightweight, no ML models required |
| Relations | SQL normalization | ACID, declarative queries, scalable |
| Integration | Minimal Python layer | MemoryManager class, simple API |

---

## API Usage (Simple)

```python
# Initialize
from comby_skill.memory import MemoryManager
memory = MemoryManager("/path/to/repo")

# Save analysis
patterns = matcher.detect_sql_injection(code)
memory.save_analysis_results("src/auth.py", patterns)

# Query
similar = memory.find_similar_patterns(pattern_id=5)
context = memory.get_pattern_context(pattern_id=5)

# Analyze
analysis = memory.analyze_dependencies()
evolution = memory.get_evolution("src/auth.py")
```

---

## CLI Commands (New)

```bash
# See all patterns of a type
$ comby-skill memory patterns --type SQL_INJECTION --severity CRITICAL

# Find similar patterns
$ comby-skill memory similar --pattern-id 42

# Understand relationships
$ comby-skill memory context --pattern-id 42

# Analyze critical path
$ comby-skill memory analyze

# Track file evolution
$ comby-skill memory history --file src/auth.py

# Compare snapshots
$ comby-skill memory compare --snapshot-1 5 --snapshot-2 8

# Annotate for collaboration
$ comby-skill memory annotate --pattern-id 42 --tag "urgent" --note "Production issue"

# Search by description
$ comby-skill memory search "user input in database"

# View statistics
$ comby-skill memory stats
```

---

## Data Model (Simplified)

### Tables

1. **patterns** (detected code issues)
   - id, file_path, line_number, pattern_type, code_snippet, severity
   - embedding (768-dim vector)
   - detected_at (timestamp)

2. **pattern_relations** (graph edges)
   - source_pattern_id, target_pattern_id
   - relation_type (depends_on, same_file, related_to, etc)
   - confidence (0.0-1.0)

3. **file_snapshots** (analysis results per file)
   - file_path, file_hash
   - total_patterns, critical_count, medium_count
   - analyzed_at (timestamp)

4. **analysis_history** (complete analysis runs)
   - repo_state_hash, total_files, total_patterns
   - critical_patterns, analysis_duration
   - analyzed_at (timestamp)

5. **annotations** (user notes)
   - pattern_id, tag, note
   - created_at (timestamp)

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **SQLite** | Zero dependencies, embedded, single file, ACID |
| **Single repo focus** | Avoid multi-repo complexity for now |
| **Deterministic embeddings** | No ML models, reproducible, explainable |
| **Automatic relations** | Build graph automatically during save |
| **Local storage** | No cloud dependencies, works offline |
| **Optional integration** | Can be used without memory layer |

---

## Use Case Scenarios

### Scenario 1: Finding Duplication
```
Dev: "I fixed a SQL injection in auth.py line 42. Are there similar ones?"
→ memory.find_similar_patterns(42)
→ Shows 7 other SQL injections with >80% code similarity
→ Dev can fix all at once or refactor into shared function
```

### Scenario 2: Understanding Risk
```
Dev: "Is this pattern safe to ignore?"
→ memory.get_pattern_context(42)
→ Shows: depends_on INPUT_VALIDATION, same_file as AUTH_BOUNDARIES
→ Dev can see if dependencies are satisfied
```

### Scenario 3: Prioritization
```
Team Lead: "What should we fix first?"
→ memory.analyze_dependencies()
→ Shows critical path: [Pattern 5 → 12 → 8]
→ Team can fix in order to minimize rework
```

### Scenario 4: Tracking Progress
```
Dev: "Have we improved?"
→ memory.get_evolution("src/auth.py")
→ Shows: 8 CRITICAL (3 weeks ago) → 5 CRITICAL (last week) → 2 CRITICAL (today)
→ Clear evidence of improvement
```

### Scenario 5: Collaboration
```
Team: "Who looked at this pattern?"
→ memory.get_annotations(pattern_id=42)
→ Shows: ["false_positive" by @alice, "urgent" by @bob]
→ Shared understanding across team
```

---

## Metrics & Performance

| Metric | Value | Notes |
|--------|-------|-------|
| Size per pattern | ~5 KB | Including embedding (768 floats) |
| Storage for 1K patterns | ~5 MB | Single SQLite file |
| Storage for 10K patterns | ~50 MB | Still very manageable |
| Lookup speed | <10 ms | Indexed, simple queries |
| Similarity search | <50 ms | HNSW vector index |
| Graph traversal | <100 ms | Depth 2-3 typical |
| Embedding generation | <1 ms | Deterministic, no ML |

---

## Roadmap

### Phase 1: Core Memory (MVP)
- ✓ SQLite schema with 5 tables
- ✓ Save/retrieve patterns
- ✓ Deterministic embeddings
- ✓ Basic similarity search
- Estimated: 2-3 weeks

### Phase 2: Relationships (Graph)
- ✓ Pattern relations table
- ✓ Automatic graph building
- ✓ Graph query functions
- ✓ Dependency analysis
- Estimated: 2 weeks

### Phase 3: History & Annotations
- ✓ File snapshots table
- ✓ Analysis history tracking
- ✓ Annotations support
- ✓ Evolution queries
- Estimated: 1-2 weeks

### Phase 4: Advanced (Future)
- [ ] Claude embeddings integration
- [ ] Semantic search improvements
- [ ] Visual reports
- [ ] Export/sync features

---

## Integration Points

### Minimal Changes to Existing Code

```python
# Only changes needed in pattern_matcher.py and cli.py

# 1. Accept optional MemoryManager in constructor
def __init__(self, memory_manager: Optional[MemoryManager] = None):
    self.memory = memory_manager

# 2. Generate embeddings if memory available
if self.memory:
    for match in matches:
        match['embedding'] = self.memory.embed_code(match['code'])

# 3. Save results to memory
memory.save_analysis_results(file_path, patterns)
```

**No breaking changes** to existing API. Memory layer is completely optional.

---

## Storage Location

```
my-project/
├── src/
│   ├── auth.py
│   ├── api.py
│   └── ...
├── .git/
├── .gitignore  ← Add .comby/memory.db
│
└── .comby/          (NEW)
    ├── memory.db    (Embedded database, ~5-50 MB)
    └── config.json  (Optional configuration)
```

**Note**: `.comby/memory.db` is local-only, not committed to Git. Each developer/environment has its own memory database.

---

## Security & Privacy

- ✅ **No external calls**: All storage is local
- ✅ **No API keys required**: Works completely offline
- ✅ **No code sent anywhere**: Everything stays in repo
- ✅ **User-controlled retention**: Can clear anytime
- ✅ **Exportable**: Can back up as JSON

---

## Next Steps

This is a **design only** - no implementation yet. The proposal includes:

1. ✅ **MEMORY_LAYER_DESIGN.md** - Complete technical architecture
2. ✅ **MEMORY_IMPLEMENTATION_EXAMPLES.md** - Concrete usage examples
3. ✅ **MEMORY_LAYER_SUMMARY.md** - This document

**When ready to implement**:
- Start with Phase 1 (SQLite schema + MemoryManager)
- Integrate with PatternMatcher incrementally
- Add CLI commands progressively
- Test with Ivoire BDD specs

---

## Summary

The Memory Layer transforms Comby Skill from a **one-time scanner** into a **learning system** that:

1. **Remembers** patterns across analyses
2. **Understands** relationships and dependencies
3. **Tracks** improvement over time
4. **Helps** developers find similar issues
5. **Enables** collaboration through annotations

All while remaining:
- **Lightweight**: Single file database, ~5KB per pattern
- **Embedded**: No external dependencies or servers
- **Focused**: Single repository at a time (no multi-repo complexity)
- **Private**: Everything stays local

This design enables future capabilities like semantic search, automated refactoring suggestions, and team collaboration without adding unnecessary complexity upfront.

---

**Status**: ✅ Design Complete | ⏳ Ready for Implementation Approval

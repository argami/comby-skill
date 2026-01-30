# Comby Skill: Pattern Families Summary

## Quick Reference: 13 Pattern Families (3 Phases)

### 🎯 Phase 1: MVP Extended (Weeks 1-3) - 6 Families

| # | Family | What It Does | Example | Why? |
|---|--------|-------------|---------|------|
| **1** | **DATABASE_ACCESS** 🗄️ | Find all database calls (queries, ORM, migrations) | `cursor.execute()`, `User.query.filter_by()` | Understand data flow, catch SQL injection, identify N+1 queries |
| **2** | **HTTP_ENDPOINTS** 🌐 | Map all HTTP request handlers | `@app.route()`, `async def handler(req)`, `@Post()` | Find attack surfaces, understand API contract, ensure auth |
| **3** | **EXTERNAL_DEPENDENCIES** 🔗 | Show all outbound API/service calls | `requests.get()`, `stripe.Charge.create()`, `fetch()` | Identify reliability risks, spot missing timeouts/error handling |
| **4** | **AUTH_BOUNDARIES** 🔐 | Locate authentication & permission checks | `@login_required`, `if !user.hasPermission()` | Verify access controls, catch missing auth, security audit |
| **5** | **CODE_COMPLEXITY** 📏 | Flag long/complex functions (>50 lines, >5 params, deep nesting) | `def process(...): # 70 lines` | Identify refactoring targets, testing difficulty |
| **6** | **CODE_DUPLICATION** 🔁 | Find repeated code blocks (>6 lines, 70%+ match) | Identical validation appearing 3x | Extract to shared function, reduce maintenance burden |

**Phase 1 Impact**:
- ✅ Accelerates code comprehension (instant map of architecture)
- ✅ Supports refactoring (clear targets for improvement)
- ✅ Detects security issues (injection, missing auth, external risks)

---

### 📊 Phase 2: Extended Patterns (Weeks 4-6) - 4 Families

| # | Family | What It Does | Example |
|---|--------|-------------|---------|
| **7** | **LOGGING_POINTS** 📊 | Map observable/logged decisions | `logger.info()`, `console.log()` |
| **8** | **INPUT_VALIDATION** ✅ | Find where user input is validated | `validate_email()`, schema validation |
| **9** | **ERROR_HANDLING** 🚨 | Identify error catching & handling | `try/except`, error recovery |
| **10** | **PERFORMANCE_HOTSPOTS** ⚡ | Flag slow patterns (N+1 queries, loop inefficiency) | Queries in loops, expensive operations |

---

### 🚀 Phase 3: Advanced Patterns (Month 2+) - 3 Families

| # | Family | What It Does |
|---|--------|-------------|
| **11** | **TYPE_SAFETY** 📝 | Missing type hints, implicit any |
| **12** | **STATE_MUTATIONS** 🔒 | Direct mutations of shared state |
| **13** | **SECRETS_AND_CONFIG** 🔑 | Hardcoded API keys, credentials |

---

## Why This Order?

### Phase 1 Rationale (Do First)

**Highest Impact + Lowest Complexity**:
- DATABASE_ACCESS & HTTP_ENDPOINTS = **code architecture** (how is the app structured?)
- EXTERNAL_DEPENDENCIES & AUTH_BOUNDARIES = **security & reliability** (what breaks the system?)
- CODE_COMPLEXITY & CODE_DUPLICATION = **maintainability** (can we refactor easily?)

**Clear ROI**:
- Each match is almost always useful (high signal-to-noise)
- Developers immediately understand what to do
- Supports all 3 goals: speed, refactoring, security

### Phase 2 Rationale (Do Next)

**More Specific Insights**:
- Build on Phase 1 foundation
- Slightly higher complexity, still valuable
- Address operational/production concerns

### Phase 3 Rationale (Do Later)

**Advanced/Specialized**:
- Require AST analysis (more complex)
- Valuable for specific teams/codebases
- Less universally applicable

---

## Implementation Complexity: Quick Estimate

```
Phase 1 Total: 4-6 weeks of development
├─ DATABASE_ACCESS:         1 week (regex + ORM patterns)
├─ HTTP_ENDPOINTS:          1 week (framework decorators)
├─ EXTERNAL_DEPENDENCIES:   1 week (common libraries)
├─ AUTH_BOUNDARIES:         1 week (guard/decorator patterns)
├─ CODE_COMPLEXITY:         3-4 days (line counting + nesting)
└─ CODE_DUPLICATION:        1-2 weeks (fuzzy matching or AST)

Phase 2 Total: 2-4 weeks
Phase 3 Total: 3-4 weeks (more complex AST work)
```

---

## How Patterns Help: The 3 Objectives

### 1. **Accelerate Code Comprehension** (Read less code, understand more)

```
Traditional: "What does this app do?"
└─ Read 500 lines to find all database calls
└─ Read 300 lines to find API endpoints
└─ 30-45 minutes to build mental model

With Patterns: "Show me the architecture"
└─ DATABASE_ACCESS: [list of 12 queries]
└─ HTTP_ENDPOINTS: [list of 8 endpoints]
└─ EXTERNAL_DEPENDENCIES: [list of 3 external services]
└─ AUTH_BOUNDARIES: [list of 5 auth checks]
└─ 5-10 minutes to build mental model
```

**Time Saved**: 20-35 minutes per codebase review

---

### 2. **Support Refactoring** (Clear targets, measurable progress)

```
Before: "This function is bad. Where do we start?"
├─ CODE_COMPLEXITY flags: 8 functions >50 lines
├─ CODE_DUPLICATION flags: 3 code blocks to extract
└─ Clear priority: tackle the longest function first

After refactoring:
└─ Measure: "Reduced longest function from 87→42 lines"
└─ Verify: All specs still pass
```

**Clarity**: Objective metrics for refactoring decisions

---

### 3. **Detect Security/Quality Issues** (Prevent problems)

```
Security Wins:
├─ DATABASE_ACCESS catches SQL injection (string concat)
├─ HTTP_ENDPOINTS identifies missing @login_required
├─ INPUT_VALIDATION finds user input used without checks
└─ AUTH_BOUNDARIES flags permission gaps

Quality Wins:
├─ CODE_COMPLEXITY identifies hard-to-test functions
├─ CODE_DUPLICATION reduces maintenance burden
├─ ERROR_HANDLING spots silent failures
└─ PERFORMANCE_HOTSPOTS catches N+1 queries
```

**Risk Reduction**: Catch issues before production

---

## Recommendation: Start With Phase 1

**Why Phase 1 First?**

✅ **6 families = complete picture of code structure**
- DATABASE_ACCESS: "Where does data flow?"
- HTTP_ENDPOINTS: "What's the API?"
- EXTERNAL_DEPENDENCIES: "What could break?"
- AUTH_BOUNDARIES: "Where's security checked?"
- CODE_COMPLEXITY: "What's hard to maintain?"
- CODE_DUPLICATION: "What's repeated?"

✅ **Each family is independent** - can implement in any order

✅ **Low implementation risk** - mostly regex + pattern matching

✅ **High user value** - developers see value immediately

✅ **Foundation for Phase 2** - patterns build naturally

---

## Next: Approval & Prioritization

**Questions to confirm scope**:

1. **Language priority**: Python-first, then JS/TS? Both simultaneously?
2. **Phase 1 order**: Which family to implement first?
   - Suggested: DATABASE_ACCESS → HTTP_ENDPOINTS → EXTERNAL_DEPENDENCIES → AUTH_BOUNDARIES → CODE_COMPLEXITY → CODE_DUPLICATION
3. **Output format**:
   - Text report (what we have)?
   - JSON output?
   - HTML dashboard?
   - Interactive CLI?
4. **Confidence settings**:
   - Show ALL matches or filter by severity?
   - Which patterns are "warnings" vs "info"?


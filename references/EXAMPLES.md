# Usage Examples

Real-world examples of how to use Comby Skill for various workflows.

---

## Example 1: Pre-Refactoring Analysis

**Scenario**: You're planning to migrate from Django ORM to SQLAlchemy. First, find all database calls.

### Step 1: Find all Django ORM calls

```bash
comby-skill search "\.filter\(|\.get\(|\.create\(" --include "*.py" --format json
```

### Step 2: Find raw SQL queries

```bash
comby-skill search "cursor\.execute|\.execute\(" --include "*.py" --format json
```

### Step 3: Find model definitions

```bash
comby-skill search "class.*\(models\.Model\)" --include "*.py" --format json
```

### Combined Report

```bash
comby-skill analyze --focus database --format json > db-analysis.json
```

---

## Example 2: Security Audit

**Scenario**: Run a comprehensive security scan on your codebase before release.

### Quick Security Scan

```bash
comby-skill analyze --focus security --severity critical
```

### Full Security Report

```bash
# Generate comprehensive security report
comby-skill analyze --focus security --format json > security-report.json

# Generate human-readable report
comby-skill analyze --focus security --format default
```

### Check for Specific Vulnerabilities

```bash
# SQL Injection patterns
comby-skill search "execute\(|\.query\(" --include "*.py" --format json

# Hardcoded secrets
comby-skill search "(api_key|secret|password).*=" --include "*.py" -i

# Command injection
comby-skill search "os\.system\(|subprocess\." --format json
```

---

## Example 3: Architecture Mapping

**Scenario**: Understand the architecture of an unfamiliar codebase.

### Find all HTTP Endpoints

```bash
# Flask routes
comby-skill search "@app\.route\(|@router\." --include "*.py"

# Django URLs
comby-skill search "path\(|re_path\(" --include "*.py"

# Express routes
comby-skill search "app\.(get|post|put|delete)\(" --include "*.js"
```

### Find all API Controllers

```bash
comby-skill search "class.*Controller|class.*View" --include "*.py"
```

### Find all External Service Calls

```bash
# HTTP calls
comby-skill search "requests\.(get|post|put|delete)" --include "*.py"

# AWS SDK
comby-skill search "boto3\.|aws-sdk" --include "*.py"

# Database connections
comby-skill search "connect\(|Connection\(" --include "*.py"
```

### Generate Architecture Inventory

```bash
comby-skill inventory --type endpoints,controllers --format json > architecture.json
```

---

## Example 4: Code Inventory

**Scenario**: Generate a complete inventory of your codebase for documentation.

### All Functions

```bash
comby-skill inventory --type functions --format json > functions.json

# Python only
comby-skill search "def\s+\w+\(" --include "*.py" --format json
```

### All Classes

```bash
comby-skill inventory --type classes --format json > classes.json
```

### All Imports

```bash
comby-skill inventory --type imports --format json > imports.json
```

### Complete Report

```bash
comby-skill inventory --type functions,classes,imports --format markdown > inventory.md
```

---

## Example 5: CI/CD Integration

**Scenario**: Add automated security scanning to your CI/CD pipeline.

### GitHub Actions Example

```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run security analysis
        run: |
          pip install comby-skill
          comby-skill analyze --focus security --format json > security-results.json

      - name: Upload security results
        uses: actions/upload-artifact@v3
        with:
          name: security-results
          path: security-results.json

      - name: Fail on critical issues
        run: |
          CRITICAL=$(jq '.issues[] | select(.severity == "critical")' security-results.json | wc -l)
          if [ $CRITICAL -gt 0 ]; then
            echo "Found $CRITICAL critical security issues!"
            exit 1
          fi
```

### GitLab CI Example

```yaml
security_scan:
  stage: test
  script:
    - pip install comby-skill
    - comby-skill analyze --focus security --format json | tee security-results.json
  artifacts:
    reports:
      json: security-results.json
  allow_failure: true  # Don't block merge, but show warnings
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/comby-skill/comby-skill
    rev: v1.0.0
    hooks:
      - id: security-scan
        args: ['--focus', 'security', '--severity', 'critical']
```

---

## Example 6: Finding Code Duplication

**Scenario**: Identify duplicated code that should be refactored.

### Find Exact Duplicates

```bash
# This requires the CODE_DUPLICATION pattern (Phase 2)
comby-skill analyze --focus duplication
```

### Manual Search for Common Patterns

```bash
# Find similar error handling
comby-skill search "try:.*except:" --include "*.py" -A 3
```

---

## Example 7: Complexity Analysis

**Scenario**: Find functions that are too complex and need refactoring.

### Find Long Functions

```bash
# Find functions over 50 lines (requires complexity pattern)
comby-skill analyze --focus complexity --severity medium
```

### Manual Search

```bash
# Find large Python functions
comby-skill search "def\s+\w+.*:" --include "*.py" --context 20
```

---

## Example 8: Authentication Analysis

**Scenario**: Audit authentication and authorization implementation.

### Find Auth Decorators

```bash
# Python decorators
comby-skill search "@login_required|@auth_required|@requires_auth" --include "*.py"

# Express middleware
comby-skill search "authenticate|authorize" --include "*.js"
```

### Find JWT Usage

```bash
comby-skill search "jwt\.decode|jwt\.encode|JWT" --include "*.py"
```

### Find Password Handling

```bash
comby-skill search "bcrypt|hashpw|check_password" --include "*.py"
```

---

## Example 9: Dependency Analysis

**Scenario**: Map all external dependencies and API calls.

### Find External API Calls

```bash
# Python requests
comby-skill search "requests\.(get|post|put|delete|patch)" --include "*.py"

# HTTP clients
comby-skill search "http\.Client|fetch\(|axios\." --include "*.js"
```

### Find Third-Party Libraries

```bash
# Python imports
comby-skill search "^import\s+(?!os|sys|re|json)" --include "*.py"
```

### Find Environment Variables

```bash
comby-skill search "os\.environ|os\.getenv" --include "*.py"
```

---

## Example 10: Custom Pattern Creation

**Scenario**: Create a custom pattern for your specific codebase.

### Using the Python API

```python
from comby_skill import SearchEngine

# Create custom pattern
engine = SearchEngine(r"my_custom_pattern")

# Search with custom pattern
results = engine.search(
    root_path="src/",
    include_pattern="*.py",
    context_lines=2
)

# Process results
for result in results:
    print(f"{result.file_path}:{result.line_number}: {result.matched_text}")
```

### Integration with Claude Code

```bash
# Use in Claude Code conversation
/comby-search "pattern" --format json
```


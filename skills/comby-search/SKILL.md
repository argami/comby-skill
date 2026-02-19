---
name: comby-search
description: Pattern matching and code search skill. Searches code for patterns using regex, finds all instances of functions/classes, and generates code inventories. Use for refactoring analysis, security scanning, and code exploration.
compatibility: Requires Python >= 3.10. Works with any programming language.
metadata:
  author: argami
  version: "1.0.0"
  category: analysis
  tags: [search, patterns, inventory, refactoring]
---

# Comby Pattern Search Skill

## Overview

The Comby Search Skill provides pattern matching and code search capabilities integrated with Claude Code. Use it to:

- **Search for patterns**: Find all instances of a pattern in your codebase using regex
- **Analyze code**: Scan for potential vulnerabilities, security issues, and code smells
- **Generate inventories**: Create machine-readable JSON exports of all matches
- **Refactoring support**: Understand the scope and impact of code changes before refactoring
- **Code exploration**: Map architecture, find dependencies, understand code relationships

## When to Use This Skill

- **Before refactoring**: Understand how many instances of a function exist across the codebase
- **Security audits**: Search for hardcoded credentials, SQL injection patterns, unsafe code
- **Code review**: Find similar patterns across the codebase to ensure consistency
- **Inventory generation**: Create structured data exports for analysis
- **Architecture mapping**: Understand which modules depend on which functions
- **Vulnerability scanning**: Detect security-related patterns before deployment

## Basic Commands

### Search for patterns
```bash
comby-search "pattern" path/to/search --include "*.py"
comby-search -i "def function_name" src/ --context 2
comby-search "import.*django" . --include "*.py"
```

### Analyze file for issues
```bash
comby-analyze path/to/file.py --focus security
comby-analyze src/ --security-strict
```

### Export as JSON (programmatic)
```bash
comby-search "pattern" src/ --output json > results.json
comby-search "TODO|FIXME" . -f json --exclude "*test*"
```

## Common Use Cases

### Use Case 1: Pre-Refactoring Analysis

Before renaming a function, understand its usage:

```bash
comby-search -i "def old_function" src/
# Output:
# src/module1.py:45 - def old_function(...):
# src/module1.py:120 - old_function()
# src/module2.py:34 - old_function()
# src/module2.py:78 - old_function()
# src/module3.py:12 - old_function()
# Total: 5 instances found
```

Helps Claude plan the refactoring scope accurately.

### Use Case 2: Security Audit

Find potential vulnerabilities:

```bash
comby-analyze src/ --security
# Scans for:
# - Hardcoded secrets (password, api_key, secret)
# - SQL injection patterns (SELECT...FROM, INSERT...INTO)
# - XSS vulnerabilities (innerHTML, dangerouslySetInnerHTML)
# - Unsafe deserialization
# - Missing input validation
```

### Use Case 3: Code Inventory

Export all API endpoints in structured format:

```bash
comby-search "@app.route|@router" src/ --output json
# Output: JSON array with all endpoints for programmatic analysis
```

### Use Case 4: Finding Dead Code

Identify functions that might not be used:

```bash
comby-search "def unused_function" src/
comby-search "unused_function" src/
# If second search returns no results, function is dead code
```

### Use Case 5: Consistency Check

Verify all database calls follow the same pattern:

```bash
comby-search "db.execute|query|fetch" src/ --output json
# Ensure all follow organization's standards
```

## Advanced Features

### Case-Insensitive Search
```bash
comby-search -i "TODO|FIXME|XXX" .
```

### File Type Filtering
```bash
comby-search "pattern" src/ --include "*.py"
comby-search "pattern" . --include "*.{ts,tsx,js}"
```

### Exclude Patterns
```bash
comby-search "pattern" src/ --exclude "*test*" --exclude "*spec*"
```

### Context Lines
```bash
comby-search "import" src/ --context 3
# Shows 3 lines before and after each match
```

### Output Formats
```bash
# Human readable (default)
comby-search "pattern" src/

# JSON (for programmatic use)
comby-search "pattern" src/ -f json

# CSV (for spreadsheet import)
comby-search "pattern" src/ -f csv
```

## Integration with Claude Code Workflow

Once you have pattern search results, Claude can:

1. **Analyze the results** - Understand the scope and distribution
2. **Propose refactoring strategies** - Based on actual usage patterns
3. **Generate code changes** - Systematically update all instances
4. **Create test cases** - For validating the changes
5. **Verify completeness** - Ensure no instances were missed

Example workflow:
```
You: "Find all uses of the getUserData function"
→ Claude runs: comby-search "def getUserData|getUserData(" src/ --output json
→ Claude analyzes results and proposes refactoring plan
→ You approve
→ Claude generates code changes and tests
```

## Tips & Tricks

- **Use `-i` flag** for case-insensitive matching when patterns vary
- **Use `--exclude`** to skip test files and avoid false positives
- **Use `-f json`** when you need to process results programmatically
- **Use `--context`** to see surrounding code and understand usage
- **Combine with Claude's analysis** for deeper insights beyond pattern matching
- **Use inventory exports** to generate metrics and reports

## Common Search Patterns

### Python
```bash
# All function definitions
comby-search "def \w+\(" src/ --include "*.py"

# All imports
comby-search "^import |^from .* import" src/ --include "*.py" -i

# Hardcoded strings (potential secrets)
comby-search '"(password|secret|api_key|token)"\s*=' src/ --include "*.py" -i

# TODO/FIXME comments
comby-search "# (TODO|FIXME|XXX|HACK)" src/ --include "*.py"
```

### JavaScript/TypeScript
```bash
# All function declarations
comby-search "function \w+\(|const \w+ = \(" src/ --include "*.{js,ts}"

# React component definitions
comby-search "function \w+.*return.*<|const \w+ = \(.*\) => <" src/ --include "*.{jsx,tsx}"

# console.log statements
comby-search "console\.log\(" src/ --include "*.{js,ts}"

# Unused variables (prefixed with _)
comby-search "const _\w+|let _\w+|var _\w+" src/ --include "*.{js,ts}"
```

### General
```bash
# Hardcoded URLs
comby-search "https?://[^\s\"']+" .

# TODO markers across any language
comby-search "TODO|FIXME|XXX|HACK|BUG" . -i

# Database calls
comby-search "query|execute|fetch|SELECT|INSERT|UPDATE|DELETE" src/ -i

# API endpoint definitions
comby-search "@(app\.|router\.)route|@(post|get|put|delete|patch)" src/ -i
```

## Customization

See the plugin configuration section to customize:

- Excluded patterns (skip certain directories/file types)
- Security focus level (strict, standard, lenient)
- Analysis depth (quick, standard, comprehensive)

Configuration options are available in Claude Code plugin settings.

## See Also

- Related Skill: **comby-analyze** - Deeper analysis for specific issues
- Command: **/comby-search** - Direct access from Claude Code
- Command: **/comby-inventory** - Generate code structure inventory

## Examples

### Example 1: Refactoring a Database Function

```
Goal: Rename database.connection to database.pool

Step 1: Find all instances
comby-search "database\.connection" src/ --output json

Step 2: Analyze distribution
→ Found in 12 files, 47 total instances

Step 3: Plan refactoring
→ Identify core modules vs dependent code

Step 4: Execute
→ Claude generates systematic replacements

Step 5: Verify
→ Run tests to confirm no breaking changes
```

### Example 2: Security Audit

```
Goal: Find potential hardcoded secrets

Step 1: Search for credential patterns
comby-analyze src/ --security

Step 2: Review results
→ Found 3 potential hardcoded passwords
→ Found 5 API keys in config files

Step 3: Remediate
→ Move to environment variables
→ Use secrets management system

Step 4: Prevent regression
→ Add pre-commit hook to prevent future hardcoding
```

### Example 3: Architecture Mapping

```
Goal: Understand dependencies between modules

Step 1: Find all imports of a core module
comby-search "from core_module import|import core_module" src/ --output json

Step 2: Analyze dependency graph
→ Core module used by 8 modules
→ 3 modules depend on each other (circular dependency detected)

Step 3: Plan refactoring
→ Break circular dependency by extracting shared code

Step 4: Execute with confidence
→ Know exactly what will be affected
```

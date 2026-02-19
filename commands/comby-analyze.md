# Comby Analyze Command

Analyze code files for vulnerabilities, security issues, and code quality problems.

## Usage

```
/comby-analyze <file-or-path> [options]
```

## Examples

### Basic analysis
```
/comby-analyze src/main.py
/comby-analyze src/ --recursive
```

### Security-focused analysis
```
/comby-analyze src/ --focus security
/comby-analyze config.py --security-strict
```

### Specific checks
```
/comby-analyze src/ --check hardcoded-secrets
/comby-analyze src/ --check sql-injection,xss
```

### Export results
```
/comby-analyze src/ --output json > results.json
/comby-analyze src/ --output html > report.html
```

## Options

| Option | Description |
|--------|-------------|
| `--recursive` | Analyze all files in directory recursively |
| `--focus [type]` | Focus on specific area: security, quality, performance |
| `--security-strict` | Use strict security analysis rules |
| `--check [list]` | Comma-separated list of specific checks |
| `--output [format]` | Output format: json, html, text (default) |
| `--severity [level]` | Filter by severity: critical, high, medium, low |
| `--exclude [pattern]` | Exclude files matching pattern |

## Checks Performed

### Security Checks
- Hardcoded secrets (passwords, API keys, tokens)
- SQL injection vulnerabilities
- Cross-site scripting (XSS) patterns
- Unsafe deserialization
- Missing input validation
- Insecure random number generation
- Command injection vulnerabilities

### Code Quality Checks
- Unused variables and imports
- Complex functions (cyclomatic complexity)
- Code duplication
- Missing error handling
- Inconsistent naming conventions

### Performance Checks
- N+1 queries
- Inefficient loops
- Memory leaks (potential)
- Blocking operations

## Output

**Text output (default)**:
```
Analyzing src/main.py...

🔴 CRITICAL: Hardcoded API key found
  Line 23: api_key = "sk-..."
  File: src/main.py
  Severity: Critical

🟡 HIGH: Missing input validation
  Line 45: process_user_input(request.data)
  File: src/handlers.py
  Severity: High

✅ Analysis complete: 2 issues found
```

**JSON output** (`--output json`):
```json
{
  "file": "src/main.py",
  "issues": [
    {
      "type": "hardcoded-secret",
      "severity": "critical",
      "line": 23,
      "message": "Hardcoded API key found",
      "suggestion": "Move to environment variable or secrets manager"
    }
  ],
  "total": 2
}
```

## Tips

- Start with `--focus security` for security audits
- Use `--severity critical,high` to focus on major issues
- Use `--output json` to integrate with other tools
- Run on modified files only before commits
- Use in CI/CD pipelines for automated checks

## Related Commands

- `/comby-search` - Pattern matching and code search
- `/comby-inventory` - Generate code structure inventory

## See Also

- **Documentation**: `references/SECURITY-CHECKS.md` for detailed security patterns
- **Skill**: comby-search (for targeted pattern analysis)

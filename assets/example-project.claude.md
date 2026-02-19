# Example Claude Code Project Configuration

This file provides an example configuration for using Comby Skill in your Claude Code projects.

## Basic Configuration

Add to your project's `CLAUDE.md` or `.claude/settings.json`:

```json
{
  "comby": {
    "hooks": {
      "fileChangeAnalysis": false,
      "preCommitAnalysis": false
    },
    "analysis": {
      "securityFocus": true,
      "excludePatterns": [
        "*test*",
        "*spec*",
        "node_modules",
        ".git",
        "__pycache__",
        "*.pyc",
        "vendor",
        "dist",
        "build"
      ]
    }
  }
}
```

## Recommended Exclusion Patterns

For different project types:

### Python Projects
```json
{
  "comby.analysis.excludePatterns": [
    "*test*.py",
    "*spec*.py",
    "venv/",
    "env/",
    "__pycache__/",
    "*.pyc",
    ".pytest_cache/",
    "*.egg-info/"
  ]
}
```

### JavaScript/TypeScript Projects
```json
{
  "comby.analysis.excludePatterns": [
    "node_modules/",
    "dist/",
    "build/",
    "coverage/",
    "*.min.js",
    "*.bundle.js"
  ]
}
```

## Hook Configuration

### Enable File Change Analysis

```json
{
  "comby.hooks.fileChangeAnalysis": true
}
```

This triggers analysis automatically when files change.

### Enable Pre-Commit Analysis

```json
{
  "comby.hooks.preCommitAnalysis": true
}
```

This runs security analysis before git commits.

## Custom Pattern Sets

### For Security-Focused Projects

```json
{
  "comby.analysis.securityFocus": true,
  "comby.analysis.customPatterns": [
    "sql_injection",
    "xss",
    "command_injection",
    "hardcoded_secrets"
  ]
}
```

### For Refactoring Projects

```json
{
  "comby.analysis.securityFocus": false,
  "comby.analysis.customPatterns": [
    "database_access",
    "http_endpoints",
    "code_complexity"
  ]
}
```

## Usage Examples

### Search for Functions
```
/comby-search "def\s+\w+\(" --include "*.py"
```

### Security Analysis
```
/comby-analyze --focus security --severity critical
```

### Code Inventory
```
/comby-inventory --type functions,classes
```

## Environment Variables

For CI/CD integration:

```bash
export COMBY_FORMAT=json
export COMBY_EXCLUDE="*test*,node_modules"
export COMBY_SECURITY_FOCUS=true
```

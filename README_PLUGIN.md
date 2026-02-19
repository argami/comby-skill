# Comby Skill Plugin

A Claude Code plugin for pattern matching and code analysis. Search code patterns, analyze for vulnerabilities, and generate code inventories.

## Features

- **Grep-compatible search interface** - Search with 5 output formats (default, JSON, CSV, lines, count)
- **Pattern families** - Pre-built patterns for common code patterns (DATABASE_ACCESS, HTTP_ENDPOINTS, AUTH_BOUNDARIES, etc.)
- **Vulnerability detection** - Security patterns for SQL injection, XSS, hardcoded secrets, and more
- **Claude Code integration** - Seamless workflow with pre/post-tool-use hooks
- **Memory layer** - SQLite-based persistence with vector embeddings for similarity search (planned)

## Installation

The plugin is automatically loaded by Claude Code when installed in your Claude Code plugins directory.

## Commands

### /comby-search

Search for patterns in your codebase.

```
/comby-search "function_name" --format json
/comby-search "TODO" --include "*.py" --context 2
```

**Options:**
- `--format` - Output format: default, json, csv, lines, count
- `--include` - File patterns to include (e.g., "*.py", "*.js")
- `--exclude` - File patterns to exclude
- `--context` - Number of context lines to show
- `--case-insensitive` - Case-insensitive search

### /comby-analyze

Analyze code for vulnerabilities and patterns.

```
/comby-analyze src/
/comby-analyze --focus security
```

**Options:**
- `--focus` - Analysis focus: security, quality, database, http, auth
- `--severity` - Filter by severity: critical, high, medium, low
- `--format` - Output format: default, json, csv

### /comby-inventory

Generate a code inventory of your project.

```
/comby-inventory
/comby-inventory --type functions,classes
```

**Options:**
- `--type` - Types to inventory: functions, classes, imports, endpoints
- `--format` - Output format: default, json, csv, markdown

## Configuration

The plugin can be configured in your Claude Code settings:

```json
{
  "comby.hooks.fileChangeAnalysis": false,
  "comby.hooks.preCommitAnalysis": false,
  "comby.analysis.securityFocus": true,
  "comby.analysis.excludePatterns": ["*test*", "node_modules", ".git"]
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `comby.hooks.fileChangeAnalysis` | boolean | false | Auto-analyze when files change |
| `comby.hooks.preCommitAnalysis` | boolean | false | Run security analysis before git commits |
| `comby.analysis.securityFocus` | boolean | true | Focus analysis on security patterns |
| `comby.analysis.excludePatterns` | array | ["*test*", "*spec*", "node_modules", ".git"] | Patterns to exclude |

## Usage Examples

### Pre-refactoring Analysis

Find all database calls before migrating:
```
/comby-search "execute\(|cursor.execute" --include "*.py"
```

### Security Audit

Scan for vulnerabilities:
```
/comby-analyze --focus security --severity critical
```

### Architecture Mapping

List all HTTP endpoints:
```
/comby-inventory --type endpoints
```

### Code Inventory

Generate function/class list:
```
/comby-inventory --type functions,classes
```

## Supported Languages

- Python (priority)
- Go
- Ruby
- Rust
- PHP
- JavaScript/TypeScript

## Pattern Families

### High Priority
- **DATABASE_ACCESS** - Find all DB calls (queries, ORM, migrations)
- **HTTP_ENDPOINTS** - Map all HTTP request handlers
- **EXTERNAL_DEPENDENCIES** - Show outbound API/service calls
- **AUTH_BOUNDARIES** - Locate authentication & permission checks

### Medium Priority
- **CODE_COMPLEXITY** - Flag long/complex functions
- **CODE_DUPLICATION** - Find repeated code blocks
- **ERROR_HANDLING** - Detect try/except patterns

## Troubleshooting

### No results found
- Check that your include/exclude patterns are correct
- Try case-insensitive search with `--case-insensitive`
- Verify the path exists

### Plugin not loading
- Ensure Claude Code is installed
- Check plugin manifest is valid JSON
- Restart Claude Code

### Performance issues
- Use `--exclude` to skip large directories (node_modules, .git)
- Limit search scope with specific file patterns
- Use `--format json` for machine-readable output

## License

MIT

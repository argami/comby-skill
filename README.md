# Comby Skill

Code pattern analysis tool with Claude AI integration.

**Repository**: https://github.com/argami/comby-skill

## Quick Start

### Installation

```bash
pip install -e ".[dev]"
```

### Running Specs

```bash
ivoire spec/
```

### Using the CLI

#### Search Mode (grep-like interface)

Search for patterns in your codebase:

```bash
# Basic pattern search (recursive by default)
comby-skill search "SELECT.*FROM" src/

# Case-insensitive search
comby-skill search -i "import.*json" .

# Search only Python files
comby-skill search --include "*.py" "def " src/

# Exclude specific patterns
comby-skill search --exclude "*test*" "TODO" src/

# Show context lines around matches
comby-skill search -C 2 "database" src/

# Output as JSON (for programmatic use)
comby-skill search -f json "error" src/

# Output as CSV
comby-skill search -f csv "warning" src/

# Count total matches
comby-skill search -c "TODO" src/

# Limit results
comby-skill search -m 10 "pattern" src/
```

#### Analyze Mode (vulnerability detection)

Analyze a file for vulnerabilities:

```bash
comby-skill analyze example_vulnerable.py
```

## Development

This project uses:
- **Ivoire** - BDD testing framework
- **Ruff** - Linting and formatting
- **TDD** - Test-driven development approach
- **GitHub Actions** - Automated testing on push/PR

### Workflow

1. Write spec (BDD style with Ivoire)
2. Run specs (RED state - should fail)
3. Implement minimal code (GREEN state - specs pass)
4. Refactor if needed (CLEAN)
5. Commit with descriptive message
6. Push to GitHub (triggers CI/CD automatically)
7. Repeat

### CI/CD

Specs run automatically on:
- **Push to main**: GitHub Actions runs the test workflow
- **Pull Requests**: All PRs must pass specs before merging
- **Python versions**: Tests run on Python 3.10, 3.11, and 3.12

View workflow status: [GitHub Actions](https://github.com/argami/comby-skill/actions)

## Architecture

```
comby-skill/
├── spec/                      # Ivoire specs (BDD)
│   ├── cli_spec.py            # Analyze command tests
│   ├── search_spec.py         # Search command tests
│   └── pattern_matcher_spec.py
├── src/comby_skill/
│   ├── __init__.py
│   ├── cli.py                 # CLI interface (search + analyze commands)
│   ├── pattern_matcher.py     # Vulnerability pattern detection
│   ├── search_engine.py       # Grep-like search implementation
│   └── config.py              # Configuration
└── example_vulnerable.py      # Demo file
```

## Quick Demo

Try the CLI on the example vulnerable file:

```bash
comby-skill analyze example_vulnerable.py
```

This will output:
- 🔴 **CRITICAL** issues: SQL injection vulnerabilities
- 🟡 **MEDIUM** issues: Missing type hints

## Features

### Search Command (Grep-Compatible)
- Regex pattern matching with full Python `re` module support
- Recursive directory traversal with glob filtering
- Multiple output formats (default, JSON, CSV, lines)
- Context lines support (`-C` option)
- Case-insensitive search (`-i` option)
- File inclusion/exclusion patterns (`--include`, `--exclude`)
- Result limiting and counting
- **Perfect for agent workflows**: Parse JSON output programmatically

### Analyze Command (Vulnerability Detection)
- **SQL Injection** - String concatenation in SQL queries (CRITICAL)
- **Missing Type Hints** - Functions without return type annotations (MEDIUM)
- *More patterns coming in next iterations...*

## Project Status

✅ **Phase 1 (MVP) Complete**:
- **Grep-like search interface** with 5 output formats
- SearchEngine class with regex pattern matching
- PatternMatcher class with 2 vulnerability detectors
- CLI with `search` and `analyze` commands
- 14 search tests + 1 analyzer test (all passing)
- Full Ivoire BDD test suite
- Working GitHub Actions CI/CD pipeline

🚀 **Next**: Pattern expansion (11 more patterns), memory layer with SQLite + embeddings, graph integration

## Documentation

Full documentation available in `docs/`:
- **[OVERVIEW](./docs/01-GETTING-STARTED/OVERVIEW.md)** - What is Comby Skill?
- **[WORKFLOW_COMPARISON](./docs/01-GETTING-STARTED/WORKFLOW_COMPARISON.md)** - See 4-22x improvements over grep
- **[ARCHITECTURE](./docs/02-ARCHITECTURE/)** - System design and pattern families
- **[IMPLEMENTATION](./docs/03-IMPLEMENTATION/)** - Usage examples and code samples
- **[REFERENCE](./docs/04-REFERENCE/)** - Quick reference guide

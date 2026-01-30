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
│   ├── pattern_matcher_spec.py
│   └── cli_spec.py
├── src/comby_skill/
│   ├── __init__.py
│   ├── pattern_matcher.py     # Pattern detection logic
│   ├── cli.py                 # CLI interface
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

## Patterns Supported

- **SQL Injection** - String concatenation in SQL queries (CRITICAL)
- **Missing Type Hints** - Functions without return type annotations (MEDIUM)
- *More patterns coming in next iterations...*

## Project Status

✅ **Phase 1 (MVP) Complete**:
- PatternMatcher class with 2 pattern detectors
- CLI tool with `analyze` command
- Full test coverage with Ivoire BDD specs
- Working E2E demo

🚀 **Ready for**: Early feedback, pattern expansion, integration with Claude

# Comby Skill

Code pattern analysis tool with Claude AI integration.

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

### Workflow

1. Write spec (BDD style with Ivoire)
2. Run specs (RED state - should fail)
3. Implement minimal code (GREEN state - specs pass)
4. Refactor if needed (CLEAN)
5. Commit with descriptive message
6. Repeat

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

## Patterns Supported

- **SQL Injection** - String concatenation in SQL queries
- **Missing Type Hints** - Functions without type annotations
- **Collections Import** - Deprecated collections imports
- *More coming...*

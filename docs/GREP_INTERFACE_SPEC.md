# Comby Skill: grep-like Interface Specification

## Overview

Comby Skill provides a grep-like CLI interface for recursive pattern searching across codebases. This is the primary interface for use as a drop-in grep replacement within agent workflows.

## Command Line Interface

### Basic Syntax

```bash
comby-skill search [OPTIONS] PATTERN [PATH]
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `PATTERN` | Yes | - | Regex pattern to search for |
| `PATH` | No | `.` | Root directory to search (current dir if omitted) |

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--recursive` | `-r` | Bool | `true` | Recursively search subdirectories |
| `--case-insensitive` | `-i` | Bool | `false` | Case-insensitive matching |
| `--include` | - | Glob | `*` | File glob to include (e.g., `*.py`, `*.js`) |
| `--exclude` | - | Glob | - | File glob to exclude (e.g., `*.test.js`) |
| `--format` | `-f` | Choice | `default` | Output format: `default`, `json`, `csv`, `lines` |
| `--context` | `-C` | Int | `0` | Lines of context before/after match |
| `--max-results` | `-m` | Int | `100` | Maximum results to return |
| `--count` | `-c` | Bool | `false` | Count matches instead of listing them |

### Output Formats

#### 1. Default (Human-Readable)
```
path/to/file.py:42: matched text here
path/to/file.py:45: another match
---
Total: 2 matches in 1 file
```

#### 2. JSON
```json
{
  "matches": [
    {
      "file": "path/to/file.py",
      "line": 42,
      "column": 15,
      "text": "matched text here",
      "context_before": ["line 41 content"],
      "context_after": ["line 43 content"]
    }
  ],
  "total_matches": 2,
  "files_with_matches": 1,
  "execution_time_ms": 45
}
```

#### 3. CSV
```csv
file,line,column,text
path/to/file.py,42,15,matched text here
path/to/file.py,45,8,another match
```

#### 4. Lines (One result per line)
```
path/to/file.py:42: matched text here
path/to/file.py:45: another match
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Successful execution (may have 0 matches) |
| `1` | Invalid arguments or invalid regex pattern |
| `2` | Error reading files or accessing paths |
| `3` | No matches found (only if `--fail-no-match` flag used) |

## Usage Examples

### Basic search
```bash
comby-skill search "SELECT.*FROM" ./src
```

### Case-insensitive search
```bash
comby-skill search -i "def.*user" . --recursive
```

### Search Python files only
```bash
comby-skill search "TODO" ./src --include "*.py"
```

### JSON output for parsing
```bash
comby-skill search -f json "import.*requests" ./src
```

### Count matches
```bash
comby-skill search -c "TODO|FIXME" . --recursive
```

### With context
```bash
comby-skill search -C 2 "function.*error" ./src --format default
```

## Implementation Notes

### Performance Considerations
- Respect `.gitignore` by default (can be disabled with `--no-gitignore`)
- Use efficient regex compilation
- Lazy evaluation for large result sets
- Parallel file scanning for large directories

### Security
- Validate regex patterns to prevent ReDoS attacks
- Sanitize file paths to prevent directory traversal
- Respect permission restrictions on files

### Compatibility
- Drop-in replacement for grep: `grep -r "pattern" . ≈ comby-skill search "pattern" .`
- Exit codes compatible with standard grep
- Output easily parseable for scripts and other tools

## Integration with Agents

Agents can call Comby Skill as a subprocess:

```python
import subprocess
import json

result = subprocess.run(
    ["comby-skill", "search", "-f", "json", "pattern", "/path"],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)
for match in data['matches']:
    print(f"{match['file']}:{match['line']}: {match['text']}")
```

## Future Enhancements

- Replace pattern (like `sed -i`)
- Multi-pattern OR search
- Highlighting in output
- Performance metrics per file
- Database integration (for persistent results)
- Graph-based pattern relationships


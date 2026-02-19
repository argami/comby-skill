# Comby Search Command

Search your codebase for specific patterns using regex.

## Usage

```
/comby-search <pattern> [path] [options]
```

## Examples

### Basic search
```
/comby-search "import " src/ --include "*.py"
/comby-search "function.*handler" src/ -i
/comby-search "TODO|FIXME" . --output json
```

### Finding functions
```
/comby-search "def getUserData" src/ --include "*.py"
/comby-search -i "const.*=.*\(" src/ --include "*.js"
```

### Security patterns
```
/comby-search "password|api_key|secret" . -i
/comby-search "SELECT.*FROM|INSERT.*INTO" src/
```

### API endpoints
```
/comby-search "@app.route|@router" src/ --include "*.py"
/comby-search "@(get|post|put|delete)" src/ -i
```

## Options

| Option | Description |
|--------|-------------|
| `--include "*.ext"` | Only search files matching pattern |
| `--exclude "*test*"` | Skip files matching pattern |
| `-i` | Case insensitive search |
| `-f json`, `--output json` | Output as JSON |
| `-f csv`, `--output csv` | Output as CSV |
| `--context N` | Show N lines before/after match |
| `--max-results N` | Limit results to N matches |
| `--only-files` | Only show file paths, not matches |

## Output

**Default output**:
```
src/module.py:45 - pattern match
src/module.py:78 - another match
Total: 2 matches found
```

**JSON output** (`-f json`):
```json
{
  "pattern": "search pattern",
  "matches": [
    {
      "file": "src/module.py",
      "line": 45,
      "content": "matched line content",
      "context": ["line before", "matched line", "line after"]
    }
  ],
  "total": 2
}
```

## Tips

- Use quotes for multi-word patterns: `"/comby-search \"multi word pattern\""`
- Use `-i` for case-insensitive matching
- Use `--output json` for programmatic processing
- Use `--context 3` to see surrounding code
- Combine `--include` and `--exclude` for precise filtering

## Related Commands

- `/comby-analyze` - Analyze files for security and quality issues
- `/comby-inventory` - Generate code structure inventory

## See Also

- **Skill**: comby-search (automatic pattern detection)
- **Documentation**: `references/PATTERNS.md` for common search patterns

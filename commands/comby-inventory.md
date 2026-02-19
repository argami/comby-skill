# Comby Inventory Command

Generate a machine-readable inventory of code structure, patterns, and components.

## Usage

```
/comby-inventory <path> [options]
```

## Examples

### Generate full inventory
```
/comby-inventory src/
/comby-inventory . --recursive
```

### Specific inventories
```
/comby-inventory src/ --focus functions
/comby-inventory src/ --focus imports
/comby-inventory src/ --focus classes
```

### Export formats
```
/comby-inventory src/ --output json > inventory.json
/comby-inventory src/ --output csv > inventory.csv
/comby-inventory src/ --output html > inventory.html
```

## Options

| Option | Description |
|--------|-------------|
| `--focus [type]` | Type of inventory: functions, classes, imports, exports, api-endpoints |
| `--recursive` | Include all files in subdirectories |
| `--output [format]` | Format: json, csv, html, text (default) |
| `--include [pattern]` | Only include files matching pattern |
| `--exclude [pattern]` | Exclude files matching pattern |
| `--with-locations` | Include file paths and line numbers |
| `--with-docs` | Include docstrings/comments |

## Inventory Types

### Functions Inventory
```
/comby-inventory src/ --focus functions --output json
```
Returns: All function definitions with signatures and locations

### Classes Inventory
```
/comby-inventory src/ --focus classes
```
Returns: All class definitions with methods and properties

### Imports Inventory
```
/comby-inventory src/ --focus imports
```
Returns: All imports and external dependencies

### API Endpoints Inventory
```
/comby-inventory src/ --focus api-endpoints
```
Returns: All API routes, methods, and parameters (for web frameworks)

### Exports Inventory
```
/comby-inventory src/ --focus exports
```
Returns: All exported symbols and public API

## Output Formats

### JSON Format (Recommended)
```bash
/comby-inventory src/ --focus functions --output json
```

**Sample output**:
```json
{
  "type": "functions",
  "path": "src/",
  "items": [
    {
      "name": "getUserData",
      "file": "src/handlers.py",
      "line": 45,
      "signature": "def getUserData(user_id: int) -> dict",
      "complexity": 3,
      "docstring": "Get user data from database"
    },
    {
      "name": "processRequest",
      "file": "src/middleware.py",
      "line": 12,
      "signature": "def processRequest(request: Request) -> Response",
      "complexity": 5,
      "docstring": "Process incoming HTTP request"
    }
  ],
  "total": 47,
  "timestamp": "2025-01-30T12:34:56Z"
}
```

### CSV Format
```bash
/comby-inventory src/ --focus functions --output csv > functions.csv
```

**Output columns**:
- `name` - Function/class name
- `file` - File path
- `line` - Line number
- `type` - Type (function, class, method)
- `complexity` - Cyclomatic complexity
- `size` - Lines of code

### HTML Format (Report)
```bash
/comby-inventory src/ --output html > report.html
```
Generates an interactive HTML report with charts and statistics.

## Use Cases

### Use Case 1: API Documentation
```bash
/comby-inventory src/ --focus api-endpoints --output json
# Automatically generate API documentation
```

### Use Case 2: Code Coverage Analysis
```bash
/comby-inventory src/ --focus functions --output json
# Count total functions for testing coverage analysis
```

### Use Case 3: Refactoring Planning
```bash
/comby-inventory src/ --focus functions --with-locations
# Find all functions to understand scope of changes
```

### Use Case 4: Dependency Analysis
```bash
/comby-inventory src/ --focus imports --output json
# Analyze external dependencies
```

### Use Case 5: Code Metrics
```bash
/comby-inventory src/ --focus classes --output json
# Generate complexity and size metrics
```

## Tips

- Use `--output json` for machine processing
- Use `--with-locations` to get precise file and line references
- Use `--with-docs` to include documentation in inventory
- Combine with `/comby-search` for targeted pattern analysis
- Export to JSON and process with your own tools

## Related Commands

- `/comby-search` - Find specific patterns
- `/comby-analyze` - Analyze for issues and vulnerabilities

## See Also

- **Documentation**: `references/EXAMPLES.md` for detailed examples
- **Skill**: comby-search (for pattern-based exploration)

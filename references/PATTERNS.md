# Search Patterns Reference

Comprehensive reference of search patterns for various languages supported by Comby Skill.

## Python Patterns

### Function Definitions
```
def\s+(\w+)\s*\(
```

### Class Definitions
```
class\s+(\w+)(?:\(.*?\))?:
```

### Imports
```
^(?:from\s+(\S+)\s+import|import\s+(\S+))
```

### TODO Comments
```
#\s*(TODO|FIXME|HACK|XXX):?\s*(.*)
```

### Function Calls
```
(\w+)\s*\(.*?\)
```

### Async Functions
```
async\s+def\s+(\w+)
```

### Decorators
```
@\w+
```

---

## JavaScript/TypeScript Patterns

### Function Declarations
```
function\s+(\w+)\s*\(
```

### Arrow Functions
```
(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=])\s*=>
```

### Class Definitions
```
class\s+(\w+)(?:\s+extends\s+\w+)?\s*\{
```

### Import Statements
```
import\s+(?:(?:\{[^}]*\}|\*\s+as\s+\w+|\w+)\s+from\s+)?['"]([^'"]+)['"]
```

### Export Statements
```
export\s+(?:default\s+)?(?:const|let|var|function|class|interface|type)
```

### Async/Await
```
(?:async\s+)?(?:function\s+)?(?:\([^)]*\)|[^=])\s*=>|await\s+
```

---

## Go Patterns

### Function Definitions
```
func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(
```

### Struct Definitions
```
type\s+(\w+)\s+struct\s*\{
```

### Interface Definitions
```
type\s+(\w+)\s+interface\s*\{
```

### Import Statements
```
import\s+(?:\(\s*)?(?:\s*["\'](\S+)["\'])?
```

### Package Declarations
```
^package\s+(\w+)
```

---

## Ruby Patterns

### Method Definitions
```
def\s+(\w+)
```

### Class Definitions
```
class\s+(\w+)(?:\s*<\s*\w+)?
```

### Module Definitions
```
module\s+(\w+)
```

### Require Statements
```
require(?:_relative)?\s+['"]([^'"]+)['"]
```

### Attr Attributes
```
attr_(?:reader|writer|accessor)\s+(:\w+|\w+)
```

---

## Rust Patterns

### Function Definitions
```
fn\s+(\w+)\s*(?:<[^>]*>)?\s*\(
```

### Struct Definitions
```
struct\s+(\w+)(?:\s*<[^>]*>)?\s*\{?
```

### Enum Definitions
```
enum\s+(\w+)\s*\{?
```

### Impl Blocks
```
impl(?:\s+<\w+>)?\s+(?:\w+\s+for\s+)?(\w+)
```

### Use Statements
```
use\s+(\w+(?:::\w+)*)
```

---

## PHP Patterns

### Function Definitions
```
function\s+(\w+)\s*\(
```

### Class Definitions
```
class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w,\s]+)?
```

### Method Definitions
```
(?:public|private|protected|static)?\s*function\s+(\w+)\s*\(
```

### Use Statements
```
use\s+(\w+(?:\\\\\w+)*)
```

### Namespace Declarations
```
namespace\s+(\w+(?:\\\\\w+)*)
```

---

## Generic Patterns

### URLs
```
https?://[^\s]+
```

### Email Addresses
```
[\w.-]+@[\w.-]+\.\w+
```

### IP Addresses
```
\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}
```

### API Keys / Secrets (High Sensitivity!)
```
(?:api[_-]?key|secret|token|password|pwd)\s*[=:]\s*['"]?[\w-]{8,}['"]?
```

### TODO Comments
```
//\s*(TODO|FIXME|HACK|XXX):?\s*.*
#\s*(TODO|FIXME|HACK|XXX):?\s*.*
```

### File Paths
```
(?:/[\w.-]+)+/?|\w:\\(?:[\w.-]+\\)*[\w.-]+
```

---

## CLI Flag Examples

### Case-insensitive Search
```bash
comby-skill search "function" -i
```

### Show Context Lines
```bash
comby-skill search "def.*" -C 3
```

### JSON Output
```bash
comby-skill search "TODO" --format json
```

### Include/Exclude Patterns
```bash
comby-skill search "class" --include "*.py" --exclude "*test*"
```

### Count Only
```bash
comby-skill search "import" --format count
```

---

## Performance Tips

1. **Use `--exclude`** to skip large directories (node_modules, .git, __pycache__)
2. **Be specific** with patterns - avoid overly broad regex
3. **Use `--format json`** for programmatic parsing
4. **Limit scope** with specific paths instead of searching entire codebase
5. **Use word boundaries** where possible (`\bword\b` instead of `word`)

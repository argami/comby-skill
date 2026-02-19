# Security Checks Reference

Comprehensive reference of security patterns detected by Comby Skill.

## SQL Injection

### Detection Patterns
```
execute\s*\(\s*['"]|\.execute\(|\.exec\(|\.query\(|cursor\.execute
```

### Risk
Critical - Allows attackers to manipulate database queries

### Example Vulnerable Code
```python
# VULNERABLE
user_id = request.GET['id']
db.execute(f"SELECT * FROM users WHERE id = {user_id}")

# VULNERABLE
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)
```

### Remediation
```python
# SAFE - Use parameterized queries
db.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# SAFE - Use ORM
User.objects.get(id=user_id)
```

---

## Cross-Site Scripting (XSS)

### Detection Patterns
```
innerHTML|outerHTML|document\.write|\.html\(|v-html
```

### Risk
High - Allows attackers to inject malicious scripts

### Example Vulnerable Code
```javascript
// VULNERABLE
element.innerHTML = userInput;

// VULNERABLE - Vue.js
<div v-html="userContent"></div>
```

### Remediation
```javascript
// SAFE - Use textContent
element.textContent = userInput;

// SAFE - Vue.js
<div v-text="userContent"></div>
```

---

## Hardcoded Secrets

### Detection Patterns
```
(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)
|password|passwd|pwd|private[_-]?key
|(aws[_-]?)?secret|stripe[_-]?key|github[_-]?token
```

### Risk
Critical - Exposes credentials publicly

### Example Vulnerable Code
```python
# VULNERABLE
API_KEY = "sk-1234567890abcdef"
SECRET_KEY = "my_secret_key_12345"

# VULNERABLE
config = {
    "api_key": "sk_live_abc123"
}
```

### Remediation
```python
# SAFE - Use environment variables
import os
API_KEY = os.environ.get('API_KEY')

# SAFE - Use config management
from keyring import get_password
api_key = get_password("myapp", "api_key")
```

---

## Command Injection

### Detection Patterns
```
os\.system\(|os\.popen\(|subprocess\.call\(|subprocess\.run\(
|subprocess\.Popen\(|shell=True|\.communicate\(
```

### Risk
Critical - Allows arbitrary command execution

### Example Vulnerable Code
```python
# VULNERABLE
os.system(f"ping {user_input}")

# VULNERABLE
subprocess.run(f"ls -la {directory}", shell=True)
```

### Remediation
```python
# SAFE - Use list args
subprocess.run(["ping", user_input], shell=False)

# SAFE - Use shlex.quote
import shlex
cmd = f"ping {shlex.quote(user_input)}"
```

---

## Unsafe Deserialization

### Detection Patterns
```
pickle\.loads\(|pickle\.load\(|yaml\.load\(|yaml\.unsafe_load
|marshal\.loads\(|eval\(|exec\(
```

### Risk
Critical - Can lead to remote code execution

### Example Vulnerable Code
```python
# VULNERABLE
data = pickle.loads(user_data)

# VULNERABLE
config = yaml.load(user_yaml)

# VULNERABLE
eval(user_code)
```

### Remediation
```python
# SAFE - Use json for data
import json
data = json.loads(user_data)

# SAFE - Use safe_load
config = yaml.safe_load(user_yaml)

# SAFE - Avoid eval/exec, use AST
import ast
tree = ast.parse(user_code)
```

---

## Path Traversal

### Detection Patterns
```
open\(|file\(|Path\(|os\.path\.join\(|os\.path\.abspath
```

### Risk
High - Allows access to unauthorized files

### Example Vulnerable Code
```python
# VULNERABLE
filename = request.GET['file']
with open(f"/var/www/uploads/{filename}") as f:
    return f.read()
```

### Remediation
```python
# SAFE - Validate and sanitize
import os
filename = request.GET['file']
if '..' in filename or '/' in filename:
    raise ValueError("Invalid filename")
safe_path = os.path.join(UPLOAD_DIR, filename)
```

---

## Insufficient Authentication

### Detection Patterns
```
login|authenticate|signin|credential|@login_required
|@auth_required|is_authenticated
```

### Risk
High - Unauthorized access to sensitive resources

### Example Vulnerable Code
```python
# VULNERABLE - Missing auth check
@app.route('/admin/delete')
def delete_user(user_id):
    User.objects.get(id=user_id).delete()
```

### Remediation
```python
# SAFE - Add authentication
@app.route('/admin/delete')
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
    User.objects.get(id=user_id).delete()
```

---

## Weak Cryptography

### Detection Patterns
```
md5\(|hashlib\.md5|sha1\(|hashlib\.sha1|\.decrypt\(
|DES\.new\(|RC4\.new\(|\.encode\('rot13'
```

### Risk
Medium - Weak encryption can be broken

### Example Vulnerable Code
```python
# VULNERABLE
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()
```

### Remediation
```python
# SAFE - Use strong hashing
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# SAFE - Use SHA-256 or better
import hashlib
password_hash = hashlib.sha256(password.encode()).hexdigest()
```

---

## SQL Injection (ORM)

### Detection Patterns
```
\.raw\(|\.extra\(|Model\.objects\.raw|\.execute\(.*\+
```

### Risk
High - Even ORM queries can be vulnerable

### Example Vulnerable Code
```python
# VULNERABLE
User.objects.raw(f"SELECT * FROM auth_user WHERE username = {username}")
```

### Remediation
```python
# SAFE - Use parameterized ORM
User.objects.get(username=username)

# SAFE - Use query builder
User.objects.filter(username=username)
```

---

## Severity Levels

| Severity | Pattern Types | Action Required |
|----------|---------------|-----------------|
| Critical | SQL Injection, Command Injection, Unsafe Deserialization | Immediate fix required |
| High | XSS, Path Traversal, Hardcoded Secrets | Fix within 24-48 hours |
| Medium | Weak Cryptography, Insufficient Auth | Fix within 1 week |
| Low | TODO comments, Code Quality | Address during refactoring |

---

## Running Security Scans

### Full Security Scan
```bash
comby-skill analyze --focus security
```

### Critical Issues Only
```bash
comby-skill analyze --focus security --severity critical
```

### JSON Output for CI/CD
```bash
comby-skill analyze --focus security --format json
```

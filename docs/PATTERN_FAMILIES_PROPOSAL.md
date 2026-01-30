# Comby Skill: Pattern Families Proposal

**Objective**: Build a comprehensive pattern detection system that accelerates code comprehension, supports refactoring, and identifies security/quality risks.

**Evaluation Criteria for Each Family**:
1. **Comprehension Speed**: How much does this reduce time to understand critical code paths?
2. **Refactoring Support**: How clearly does this guide refactoring decisions?
3. **Risk Detection**: Does this catch security vulnerabilities or quality issues?
4. **Signal-to-Noise Ratio**: How likely are matches to be valuable vs. false positives?
5. **Implementation Complexity**: Effort vs. value tradeoff

---

## Phase 1: MVP Extended (Next 2-3 weeks)

These patterns have the highest impact with manageable implementation complexity. Each builds on existing infrastructure.

### 1. **Database Interaction Points** 🗄️
**Family Name**: `DATABASE_ACCESS`

**Primary Objective**: Rapidly identify all code touching databases (reads, writes, schema changes)

**Why It Matters**:
- Developers need to understand data flow, queries, mutations quickly
- Easy to miss query vulnerabilities if you don't know where database calls happen
- Critical for refactoring (N+1 queries, transaction scoping, connection pooling)

**Python Examples**:
```python
# Pattern 1: Direct query execution
cursor.execute("SELECT * FROM users WHERE id = " + user_id)  # ⚠️ Also SQL injection

# Pattern 2: ORM calls
user = User.query.filter_by(email=email).first()

# Pattern 3: Connection/session usage
with db.connection() as conn:
    result = conn.execute("SELECT ...")

# Pattern 4: Raw SQL in strings
query = """
    SELECT id, name FROM users
    WHERE created_at > %s
"""

# Pattern 5: Bulk operations
User.objects.bulk_create([user1, user2])
```

**JavaScript/TypeScript Examples**:
```typescript
// Pattern 1: Query builder
db.query('SELECT * FROM users WHERE id = ?', [userId])

// Pattern 2: ORM
const user = await User.findOne({ where: { email } })

// Pattern 3: Parameterized
db.prepare('SELECT * FROM users WHERE id = ?').get(id)

// Pattern 4: Migration/schema
db.schema.createTable('users', t => { t.increments() })
```

**Detects**:
- ✅ Where data is being accessed
- ⚠️ Potential SQL injection (string concatenation in queries)
- ✅ Database I/O hotspots (refactoring targets)
- ✅ Lack of parameterized queries

**Signal-to-Noise**: HIGH (most matches are genuine database calls)
**Implementation Complexity**: MEDIUM (regex + common ORM patterns)
**Security Value**: HIGH (catches injection vulnerabilities)

---

### 2. **HTTP Entry Points** 🌐
**Family Name**: `HTTP_ENDPOINTS`

**Primary Objective**: Map all external request handlers (REST endpoints, webhooks, form receivers)

**Why It Matters**:
- These are attack surfaces—must validate all inputs
- Helps understand API contract and data flow
- Identifies where authentication/authorization decisions happen
- Essential for security review and refactoring

**Python Examples**:
```python
# Pattern 1: Flask route
@app.route('/users/<user_id>', methods=['GET', 'POST'])
def get_user(user_id):
    pass

# Pattern 2: FastAPI endpoint
@app.post('/users')
async def create_user(user: UserSchema):
    pass

# Pattern 3: Django view
def user_detail(request, user_id):
    pass

# Pattern 4: Class-based view
class UserListView(APIView):
    def get(self, request):
        pass

# Pattern 5: Manual request handler
def handle_webhook(request):
    data = request.json
```

**JavaScript/TypeScript Examples**:
```typescript
// Pattern 1: Express route
app.post('/api/users', (req, res) => {
    const { email } = req.body  // ⚠️ Input validation?
})

// Pattern 2: NestJS controller
@Post('/users')
async createUser(@Body() user: CreateUserDto) {}

// Pattern 3: Next.js API route
export default function handler(req, res) {
    if (req.method === 'POST') {
        const data = req.body
    }
}

// Pattern 4: Fastify route
app.post('/users', async (request, reply) => {})
```

**Detects**:
- ✅ All HTTP endpoints
- ⚠️ Missing input validation (no guard before req.body usage)
- ✅ Authentication decorator presence
- ⚠️ Potential CSRF/CORS issues
- ✅ API versioning patterns

**Signal-to-Noise**: VERY HIGH (each match is an endpoint)
**Implementation Complexity**: MEDIUM (framework-specific decorators/functions)
**Security Value**: VERY HIGH (attack surfaces)

---

### 3. **External API/Service Calls** 🔗
**Family Name**: `EXTERNAL_DEPENDENCIES`

**Primary Objective**: Show all outbound calls to external services (APIs, webhooks, payment processors)

**Why It Matters**:
- Reduces time to understand third-party integrations
- Identifies reliability risks (external API failures = system risk)
- Helps prioritize where error handling + timeouts matter
- Critical for refactoring (caching, retry logic, fallbacks)

**Python Examples**:
```python
# Pattern 1: Requests library
response = requests.get('https://api.example.com/users')

# Pattern 2: HTTPX
async with httpx.AsyncClient() as client:
    response = await client.get('https://api.example.com')

# Pattern 3: Third-party client
stripe.Charge.create(amount=1000, currency='usd')

# Pattern 4: urllib
from urllib.request import urlopen
urlopen('https://api.example.com/data')

# Pattern 5: Webhook posting
requests.post(webhook_url, json=event_data)
```

**JavaScript/TypeScript Examples**:
```typescript
// Pattern 1: Fetch
const response = await fetch('https://api.example.com/users')

// Pattern 2: Axios
const response = await axios.get('https://api.example.com/users')

// Pattern 3: Third-party SDK
const charge = await stripe.charges.create({...})

// Pattern 4: GraphQL client
const result = await client.query(QUERY)

// Pattern 5: WebSocket
const ws = new WebSocket('wss://api.example.com/stream')
```

**Detects**:
- ✅ All external API calls
- ⚠️ Missing error handling (try/catch?)
- ⚠️ Missing timeouts
- ✅ API credentials usage
- ✅ Third-party service dependencies

**Signal-to-Noise**: VERY HIGH (each match is an external call)
**Implementation Complexity**: MEDIUM (common libraries: requests, httpx, fetch, axios)
**Reliability Value**: HIGH (external failures are top risk)

---

### 4. **Authentication & Authorization Checks** 🔐
**Family Name**: `AUTH_BOUNDARIES`

**Primary Objective**: Identify where permission decisions happen

**Why It Matters**:
- Developers need to verify access controls are correct
- Rapidly spot missing auth checks
- Essential for security audit
- Helps refactor auth logic to centralized location

**Python Examples**:
```python
# Pattern 1: Decorator-based
@login_required
def protected_view(request):
    pass

# Pattern 2: Manual check
if not request.user.is_authenticated:
    raise PermissionError()

# Pattern 3: Permission check
if not user.has_permission('edit_post'):
    return False

# Pattern 4: Role check
if user.role != 'admin':
    raise Forbidden()

# Pattern 5: Token validation
token = request.headers.get('Authorization')
if not validate_token(token):
    raise Unauthorized()
```

**JavaScript/TypeScript Examples**:
```typescript
// Pattern 1: Middleware check
app.use(authMiddleware)

// Pattern 2: NestJS guard
@UseGuards(JwtAuthGuard)
async deleteUser() {}

// Pattern 3: Manual check
if (!user || user.id !== resourceOwnerId) {
    throw new ForbiddenException()
}

// Pattern 4: Role-based
if (user.roles.includes('admin')) {
    // allow
}

// Pattern 5: Token verification
const decoded = jwt.verify(token, SECRET)
```

**Detects**:
- ✅ Where auth checks happen
- ⚠️ Endpoints missing auth decorators
- ✅ Authorization logic patterns
- ⚠️ Weak permission checks
- ✅ Token/credential usage

**Signal-to-Noise**: HIGH (when found, almost always security-critical)
**Implementation Complexity**: MEDIUM (framework patterns)
**Security Value**: CRITICAL (prevents unauthorized access)

---

### 5. **Long Functions / Complex Methods** 📏
**Family Name**: `CODE_COMPLEXITY`

**Primary Objective**: Flag functions that are candidates for refactoring (hard to test, understand, maintain)

**Why It Matters**:
- Long functions = hard to understand quickly
- Harder to test (fewer unit tests)
- Higher bug risk
- Direct refactoring target: break into smaller pieces

**Detection Strategy**:
```python
# Flag functions > 50 lines (or > 10 parameters)
def process_user_order(user, cart, shipping_address, billing_address,
                       payment_method, coupon, tax_calculator,
                       inventory_service, email_service):
    # 60+ lines of logic
    pass

# Flag methods with high nesting depth (> 3 levels)
if condition1:
    if condition2:
        if condition3:
            for item in items:
                # Hard to follow
                pass
```

**Metrics**:
- **Line count**: > 50 lines
- **Parameters**: > 5 parameters
- **Nesting depth**: > 3 levels
- **Cyclomatic complexity**: Implicit in nested conditions

**Python Examples**:
```python
# Example: Long function (refactoring candidate)
def create_subscription(user, plan, auto_renew, payment_details,
                        promo_code, billing_cycle, cancellation_policy):
    # Line 1-20: Validate inputs
    # Line 21-35: Check payment
    # Line 36-50: Create subscription
    # Line 51-65: Send notifications
    # Line 66+: Handle edge cases
    pass
```

**JavaScript/TypeScript Examples**:
```typescript
// Candidate for refactoring
async function handleUserRegistration(req, res) {
    // 70+ lines mixing:
    // - Input validation
    // - Database operations
    // - Email sending
    // - Session creation
    // - Analytics tracking
}
```

**Detects**:
- ✅ Functions needing refactoring
- ✅ Testing difficulty indicators
- ✅ Maintenance burden
- ✅ Potential bug hotspots

**Signal-to-Noise**: HIGH (rarely false positives)
**Implementation Complexity**: LOW (line/parameter counting)
**Refactoring Value**: VERY HIGH (clear action: split function)

---

### 6. **Duplicate Code Detection** 🔁
**Family Name**: `CODE_DUPLICATION`

**Primary Objective**: Identify repeated code patterns that should be extracted to shared function

**Why It Matters**:
- Duplication = bugs appearing in multiple places
- Maintenance nightmare (fix bug once, fix it 5 times)
- Refactoring opportunity: create helper/utility
- Reduces cognitive load (read logic once)

**Detection Strategy**:
```python
# Flag identical or near-identical code blocks (6+ lines)
def get_user_by_email(email):
    if not email or not isinstance(email, str):
        raise ValueError("Invalid email")
    email = email.strip().lower()
    user = db.query(User).filter_by(email=email).first()
    if not user:
        raise NotFound("User not found")
    return user

def get_admin_by_email(email):
    if not email or not isinstance(email, str):
        raise ValueError("Invalid email")  # DUPLICATE
    email = email.strip().lower()           # DUPLICATE
    admin = db.query(Admin).filter_by(email=email).first()
    if not admin:                           # DUPLICATE
        raise NotFound("User not found")    # DUPLICATE
    return admin
```

**Python Examples**:
```python
# Pattern 1: Duplicated validation
def validate_email(email):
    if not email or not isinstance(email, str):
        raise ValueError("Invalid email")
    return email.strip().lower()

# This validation appears in 3+ functions → extract to helper

# Pattern 2: Duplicated database logic
user = db.query(User).filter_by(id=user_id).first()
# vs
product = db.query(Product).filter_by(id=product_id).first()
# → Extract: find_by_id(model, id)

# Pattern 3: Duplicated error handling
try:
    # operation
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return None
```

**JavaScript/TypeScript Examples**:
```typescript
// Duplicated check appears in multiple endpoints
function validateUserRequest(req) {
    if (!req.body.email) throw new Error('Email required')
    if (!req.body.password) throw new Error('Password required')
    return true
}

// Better: middleware or shared validator
```

**Detects**:
- ✅ Copy-pasted code blocks
- ✅ Similar logic patterns (different variable names)
- ⚠️ Inconsistent error handling
- ✅ Refactoring opportunities

**Signal-to-Noise**: MEDIUM-HIGH (some false positives with legitimately similar code)
**Implementation Complexity**: MEDIUM-HIGH (requires AST analysis or fuzzy matching)
**Refactoring Value**: VERY HIGH (extract to function)

---

## Phase 2: Extended Patterns (Weeks 4-6)

These patterns add more detailed insights but require more implementation complexity.

### 7. **Logging & Observability** 📊
**Family Name**: `LOGGING_POINTS`

**Primary Objective**: Map where application state/decisions are being recorded

**Why It Matters**:
- Understand what's observable in production
- Identify gaps in observability (no logging at key points)
- Security: trace where sensitive data might be logged
- Debugging: quickly find where to add logs

**Python Examples**:
```python
logger.info(f"User {user.id} logged in")  # ✅ Observable
logger.error(f"Payment failed: {error}")  # ✅ Tracked
# vs
# Missing: db.save() with no logging = silent failures

# Pattern: Missing logging at critical points
def process_payment(order):
    result = payment_gateway.charge(order.amount)  # ⚠️ No log
    if result.failed:                              # ⚠️ No log
        return False
```

**JavaScript Examples**:
```typescript
console.log(`User ${userId} requested access`)
logger.warn(`Retry attempt ${retries}`)
// Missing logs at failures, state changes
```

**Detects**:
- ✅ All logging statements
- ⚠️ Missing logs at error paths
- ⚠️ Sensitive data in logs (passwords, tokens)
- ✅ Inconsistent log levels

**Refactoring Value**: MEDIUM (improve observability)
**Security Value**: MEDIUM (prevent data leaks)

---

### 8. **Input Validation & Sanitization** ✅
**Family Name**: `INPUT_VALIDATION`

**Primary Objective**: Identify where user input is validated before use

**Why It Matters**:
- Missing validation = XSS, injection, buffer overflow risks
- Shows data trust boundaries
- Indicates where refactoring to centralized validation would help

**Python Examples**:
```python
# Pattern 1: Validated input
email = validate_email(request.form.get('email'))

# Pattern 2: No validation
username = request.form.get('username')  # ⚠️ Used directly?
```

**Detects**:
- ⚠️ req.body/request.form used without validation
- ✅ Validation function calls
- ✅ Schema validation (Pydantic, etc.)

**Security Value**: HIGH (prevents injection)

---

### 9. **Error Handling Patterns** 🚨
**Family Name**: `ERROR_HANDLING`

**Primary Objective**: Identify how errors are caught and handled

**Why It Matters**:
- Shows resilience of application
- Identifies silent failures (no error handling)
- Security: error messages revealing system info
- Refactoring: centralize error handling

**Python Examples**:
```python
try:
    operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    return None
except Exception:                      # ⚠️ Too broad
    pass                               # ⚠️ Silent failure
```

**Detects**:
- ⚠️ Bare except clauses
- ⚠️ Silent failures (no log/re-raise)
- ✅ Proper error handling
- ⚠️ Generic exceptions (too broad)

**Reliability Value**: HIGH (improves uptime)

---

### 10. **Performance-Sensitive Operations** ⚡
**Family Name**: `PERFORMANCE_HOTSPOTS`

**Primary Objective**: Flag operations known to be slow or heavy

**Why It Matters**:
- Identifies N+1 queries, inefficient loops
- Shows where caching/optimization matters
- Refactoring target: optimize loop-heavy operations

**Python Examples**:
```python
# Pattern 1: N+1 query
for user in users:
    print(user.profile.bio)  # ⚠️ Query per user

# Pattern 2: Inefficient loop
for user in users:
    if user.email == target_email:  # ⚠️ O(n) search
        return user

# Better: Use dict/set for O(1) lookup

# Pattern 3: Serialization in loop
for user in users:
    json.dumps(user)  # ⚠️ Serializing in loop
```

**JavaScript Examples**:
```typescript
// N+1 pattern
const users = await User.find()
for (const user of users) {
    const posts = await Post.find({ userId: user.id })  // ⚠️ N queries
}
```

**Detects**:
- ⚠️ Loop with DB queries
- ⚠️ Inefficient data structure usage
- ⚠️ Heavy operations in loops

**Performance Value**: HIGH (catches bottlenecks)

---

## Phase 3: Advanced Patterns (Month 2+)

### 11. **Type Safety Gaps** 📝
**Family Name**: `TYPE_SAFETY`

**Python Examples**:
```python
def process_user(user):  # ⚠️ No type hint
    return user.name
```

**TypeScript Examples**:
```typescript
// ⚠️ Implicit any
function process(data) {
    return data.value
}
```

**Detects**: Missing types, implicit any, untyped parameters

---

### 12. **State Mutation & Immutability** 🔒
**Family Name**: `STATE_MUTATIONS`

**Detects**: Direct mutations of shared state that could cause bugs

---

### 13. **Configuration & Secrets** 🔑
**Family Name**: `SECRETS_AND_CONFIG`

**Detects**: Hardcoded API keys, passwords, config values

---

---

## Priority Matrix & Recommendations

| Family | Phase | Complexity | Impact | Security | Priority |
|--------|-------|-----------|--------|----------|----------|
| **DATABASE_ACCESS** | 1 | MEDIUM | ⭐⭐⭐⭐⭐ | CRITICAL | **#1** |
| **HTTP_ENDPOINTS** | 1 | MEDIUM | ⭐⭐⭐⭐⭐ | CRITICAL | **#2** |
| **EXTERNAL_DEPENDENCIES** | 1 | MEDIUM | ⭐⭐⭐⭐ | HIGH | **#3** |
| **AUTH_BOUNDARIES** | 1 | MEDIUM | ⭐⭐⭐⭐⭐ | CRITICAL | **#4** |
| **CODE_COMPLEXITY** | 1 | LOW | ⭐⭐⭐⭐ | N/A | **#5** |
| **CODE_DUPLICATION** | 1 | MEDIUM-HIGH | ⭐⭐⭐⭐ | N/A | **#6** |
| LOGGING_POINTS | 2 | MEDIUM | ⭐⭐⭐ | MEDIUM | #7 |
| INPUT_VALIDATION | 2 | MEDIUM | ⭐⭐⭐⭐ | CRITICAL | #8 |
| ERROR_HANDLING | 2 | MEDIUM | ⭐⭐⭐⭐ | MEDIUM | #9 |
| PERFORMANCE_HOTSPOTS | 2 | MEDIUM-HIGH | ⭐⭐⭐ | N/A | #10 |

---

## MVP Extended Scope (Phase 1)

**Recommended Focus for Next 2-3 weeks**:

1. ✅ **DATABASE_ACCESS** - Builds on current SQL injection detection
2. ✅ **HTTP_ENDPOINTS** - New: framework-specific patterns
3. ✅ **EXTERNAL_DEPENDENCIES** - New: service call mapping
4. ✅ **AUTH_BOUNDARIES** - New: security-critical checks
5. ✅ **CODE_COMPLEXITY** - New: refactoring guidance
6. ✅ **CODE_DUPLICATION** - New: DRY principle enforcement

**Why This Scope**:
- **High signal-to-noise ratio**: Most matches are valuable
- **Clear actionability**: Developers know what to do
- **Progressive complexity**: Start simple, increase sophistication
- **Covers all three objectives**: Comprehension, refactoring, security
- **Manageable**: 6 families ≈ 4-6 weeks of focused work

---

## Implementation Strategy

### Pattern Detection Approach

```python
class PatternFamily:
    name: str                    # "DATABASE_ACCESS"
    severity: str               # "INFO", "WARNING", "CRITICAL"
    detectors: List[Detector]   # List of regex/AST patterns
    languages: List[str]        # ["python", "javascript"]

    def detect(code: str) -> List[Match]:
        # Find all matches for this family
        pass

class Match:
    family: str
    pattern: str               # "direct_query_execution"
    line_number: int
    code: str
    severity: str
    explanation: str          # Why this matters
    refactoring_hint: str     # How to improve it
```

### CLI Output Evolution

```bash
$ comby-skill analyze myapp.py

📊 PATTERN ANALYSIS REPORT
═══════════════════════════

🗄️  DATABASE_ACCESS (6 matches)
  • Line 45: cursor.execute() - Direct query
  • Line 78: User.query.filter_by() - ORM call
  • Line 120: db.connection() - Raw connection

🌐 HTTP_ENDPOINTS (3 matches)
  • Line 12: @app.route('/users', methods=['GET', 'POST'])
  • Line 28: @app.post('/users')
  • Line 156: class UserListView - API endpoint

🔐 AUTH_BOUNDARIES (1 match - ⚠️ WARNING)
  • Line 12: Missing @login_required on /users GET endpoint!

📏 CODE_COMPLEXITY (2 matches)
  • Line 156: process_order() - 68 lines (refactoring candidate)
  • Line 200: handle_webhook() - 5+ levels deep nesting

🔁 CODE_DUPLICATION (1 match)
  • Lines 45-50 similar to lines 120-125 (70% match)

═══════════════════════════
Total: 13 patterns found | 1 security warning
```

---

## Next Steps

1. **Approve Phase 1 pattern families** (above)
2. **Specify language priorities**: Python-first, then JS/TS?
3. **Confirm implementation order**: Database → HTTP → External → Auth → Complexity → Duplication?
4. **Discuss output format**: Text, JSON, HTML report?
5. **Begin Phase 1 implementation**: Start with DATABASE_ACCESS


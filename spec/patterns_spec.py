"""BDD tests for pattern families."""

import pytest
from io import StringIO
import sys


class DescribeDatabaseAccessPatterns:
    """Tests for DATABASE_ACCESS pattern family."""

    def it_detects_raw_sql_execute(self):
        """Should detect cursor.execute with SQL string."""
        from comby_skill.patterns.database_access import detect_database_access

        code = """
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()
"""
        results = detect_database_access("test.py", "python", code)
        assert len(results) > 0
        assert any(r.operation_type.value == "select" for r in results)

    def it_detects_sqlalchemy_orm(self):
        """Should detect SQLAlchemy ORM queries."""
        from comby_skill.patterns.database_access import detect_database_access

        code = """
def get_users():
    return session.query(User).filter(User.active == True).all()
"""
        results = detect_database_access("test.py", "python", code)
        assert len(results) > 0
        assert any(r.is_orm for r in results)

    def it_classifies_database_usage(self):
        """Should classify database operations."""
        from comby_skill.patterns.database_access import (
            detect_database_access,
            classify_database_usage,
        )

        code = """
cursor.execute("INSERT INTO logs VALUES (?, ?)", (user_id, action))
session.commit()
"""
        results = detect_database_access("test.py", "python", code)
        classification = classify_database_usage(results)

        assert classification["total_operations"] >= 2


class DescribeHTTPEndpointsPatterns:
    """Tests for HTTP_ENDPOINTS pattern family."""

    def it_detects_flask_routes(self):
        """Should detect Flask route decorators."""
        from comby_skill.patterns.http_endpoints import detect_http_endpoints

        code = """
@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(users)
"""
        results = detect_http_endpoints("app.py", "python", code)
        assert len(results) > 0
        assert any(r.path == "/api/users" for r in results)

    def it_detects_fastapi_routes(self):
        """Should detect FastAPI route decorators."""
        from comby_skill.patterns.http_endpoints import detect_http_endpoints

        code = """
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
"""
        results = detect_http_endpoints("app.py", "python", code)
        assert len(results) > 0

    def it_classifies_endpoints(self):
        """Should classify HTTP endpoints."""
        from comby_skill.patterns.http_endpoints import (
            detect_http_endpoints,
            classify_endpoints,
        )

        code = """
@app.get('/api/users')
@app.post('/api/users')
@app.delete('/api/users/1')
"""
        results = detect_http_endpoints("app.py", "python", code)
        classification = classify_endpoints(results)

        assert classification["total_endpoints"] >= 3


class DescribeAuthBoundariesPatterns:
    """Tests for AUTH_BOUNDARIES pattern family."""

    def it_detects_login_required_decorator(self):
        """Should detect login_required decorator."""
        from comby_skill.patterns.auth_boundaries import detect_auth_boundaries

        code = """
@login_required
def dashboard():
    return render_template('dashboard.html')
"""
        results = detect_auth_boundaries("views.py", "python", code)
        assert len(results) > 0
        assert any(r.auth_type.value == "decorator" for r in results)

    def it_detects_jwt_handling(self):
        """Should detect JWT token handling."""
        from comby_skill.patterns.auth_boundaries import detect_auth_boundaries

        code = """
def create_token(user_id):
    return jwt.encode({'user_id': user_id}, SECRET_KEY, algorithm='HS256')
"""
        results = detect_auth_boundaries("auth.py", "python", code)
        assert len(results) > 0
        assert any(r.auth_type.value == "jwt_handler" for r in results)

    def it_detects_password_hashing(self):
        """Should detect password hashing with bcrypt."""
        from comby_skill.patterns.auth_boundaries import detect_auth_boundaries

        code = """
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
"""
        results = detect_auth_boundaries("auth.py", "python", code)
        assert len(results) > 0
        assert any(r.is_secure for r in results)


class DescribeExternalDependenciesPatterns:
    """Tests for EXTERNAL_DEPENDENCIES pattern family."""

    def it_detects_requests_library(self):
        """Should detect requests library HTTP calls."""
        from comby_skill.patterns.external_deps import detect_external_dependencies

        code = """
def fetch_data(url):
    response = requests.get(url)
    return response.json()
"""
        results = detect_external_dependencies("api.py", "python", code)
        assert len(results) > 0

    def it_detects_aws_boto3(self):
        """Should detect AWS boto3 usage."""
        from comby_skill.patterns.external_deps import detect_external_dependencies

        code = """
s3 = boto3.client('s3')
s3.upload_fileobj(file, bucket, key)
"""
        results = detect_external_dependencies("s3.py", "python", code)
        assert len(results) > 0


class DescribeComplexityPatterns:
    """Tests for CODE_COMPLEXITY pattern family."""

    def it_calculates_cyclomatic_complexity(self):
        """Should calculate cyclomatic complexity."""
        from comby_skill.patterns.complexity import analyze_complexity

        code = """
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                return x + y + z
    return 0
"""
        results = analyze_complexity("test.py", "python", code)
        assert len(results) > 0
        assert results[0].cyclomatic_complexity >= 3

    def it_classifies_complexity(self):
        """Should classify complexity metrics."""
        from comby_skill.patterns.complexity import (
            analyze_complexity,
            classify_complexity,
        )

        code = """
def simple():
    return 1
"""
        results = analyze_complexity("test.py", "python", code)
        classification = classify_complexity(results)

        assert "complexity_distribution" in classification


class DescribeErrorHandlingPatterns:
    """Tests for ERROR_HANDLING pattern family."""

    def it_detects_try_except(self):
        """Should detect try/except blocks."""
        from comby_skill.patterns.error_handling import detect_error_handling

        code = """
try:
    result = divide(x, y)
except ZeroDivisionError:
    print("Cannot divide by zero")
"""
        results = detect_error_handling("test.py", "python", code)
        assert len(results) > 0
        assert any(r.pattern.value in ("try_catch", "try_except") for r in results)

    def it_detects_bare_except(self):
        """Should detect bare except clauses."""
        from comby_skill.patterns.error_handling import detect_error_handling

        code = """
try:
    process()
except:
    pass
"""
        results = detect_error_handling("test.py", "python", code)
        assert len(results) > 0
        assert any(r.is_swallowed for r in results)

    def it_classifies_error_handling(self):
        """Should classify error handling quality."""
        from comby_skill.patterns.error_handling import (
            detect_error_handling,
            classify_error_handling,
        )

        code = """
try:
    do_something()
except Exception as e:
    logger.error(str(e))
"""
        results = detect_error_handling("test.py", "python", code)
        classification = classify_error_handling(results)

        assert "quality" in classification

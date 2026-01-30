"""Example file with vulnerable code for demonstration purposes.

This file intentionally contains security vulnerabilities to demonstrate
the pattern matching capabilities of Comby Skill.

IMPORTANT: This is example code only. Never use these patterns in production!
"""


def find_user_by_email(email: str):
    """Find user by email - VULNERABLE to SQL injection.

    This function is vulnerable because it concatenates user input
    directly into a SQL query.
    """
    query = "SELECT * FROM users WHERE email = '" + email + "'"
    return db.execute(query)


def find_user_by_username(username: str):
    """Find user by username - VULNERABLE to SQL injection via f-string.

    This function uses f-string interpolation, which is also vulnerable
    to SQL injection when user input is directly embedded.
    """
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)


def execute_api_query(table_name, filter_column, filter_value):
    """Execute API query - CRITICAL: Multiple injection points.

    This function has multiple injection points:
    1. table_name can select different tables
    2. filter_column can change query logic
    3. filter_value uses string concatenation
    """
    query = (
        f"SELECT * FROM {table_name} "
        f"WHERE {filter_column} = '{filter_value}'"
    )
    return db.execute(query)


def update_user_role(user_id, role):
    """Update user role - VULNERABLE to SQL injection.

    Another example of vulnerable SQL construction through string concatenation.
    """
    query = "UPDATE users SET role = '" + role + "' WHERE id = " + str(user_id)
    return db.execute(query)


def delete_user_by_id(user_id: int):
    """Delete user - VULNERABLE to SQL injection.

    Even with type hints on parameters, the query construction is still vulnerable.
    """
    query = "DELETE FROM users WHERE id = '" + str(user_id) + "'"
    return db.execute(query)


def helper_function_missing_hints(param1, param2):
    """Helper function missing type hints and return type.

    Functions should have type hints for parameters and return type.
    """
    return param1 + param2


def another_unsafe_function(data):
    """Another function without complete type information."""
    return {"result": data}


# Safe examples (for reference - these won't trigger warnings)

def safe_find_user(email: str) -> dict:
    """Find user safely using parameterized queries.

    This is the CORRECT way to query databases.
    """
    query = "SELECT * FROM users WHERE email = ?"
    return db.execute(query, (email,))


def safe_update_role(user_id: int, role: str) -> bool:
    """Update user role safely.

    This uses parameterized queries to prevent SQL injection.
    """
    query = "UPDATE users SET role = ? WHERE id = ?"
    return db.execute(query, (role, user_id))

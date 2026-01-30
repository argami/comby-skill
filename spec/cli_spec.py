"""Specs for CLI module using Ivoire BDD"""

import subprocess
import tempfile
import os
from ivoire import describe, context, it
from ivoire.assertions import expect

describe("CLI"):
    context("analyze command"):
        it("can analyze a file and output matches"):
            # Create temporary file with vulnerable code
            vulnerable_code = 'query = "SELECT * FROM users WHERE id = \'" + user_id + "\'"'

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(vulnerable_code)
                temp_file = f.name

            try:
                # Run CLI command
                result = subprocess.run(
                    ["python", "-m", "comby_skill.cli", "analyze", temp_file],
                    capture_output=True,
                    text=True,
                    cwd="/Users/argami/Documents/workspace/AI/comby-skill",
                )

                # Validate output
                expect(result.returncode).to(equal(0))
                expect(result.stdout).to(contain("SQL_INJECTION"))
                expect(result.stdout).to(contain("SELECT"))
            finally:
                os.unlink(temp_file)

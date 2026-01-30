"""Specs for CLI module using Ivoire BDD"""

import subprocess
import tempfile
import os
from ivoire import describe

with describe("CLI") as it:
    with it("analyze command - can analyze a file and output matches") as test:
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
            test.assertEqual(result.returncode, 0)
            test.assertIn("SQL_INJECTION", result.stdout)
            test.assertIn("SELECT", result.stdout)
        finally:
            os.unlink(temp_file)

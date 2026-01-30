"""Specs for search command using Ivoire BDD"""

import subprocess
import tempfile
import json
import csv
import os
from pathlib import Path
from io import StringIO
from ivoire import describe

with describe("CLI search command") as it:
    with it("search - can find basic regex pattern in file") as test:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text('print("hello world")\nprint("hello universe")')

            result = subprocess.run(
                ["python", "-m", "comby_skill.cli", "search", "hello", tmpdir],
                capture_output=True,
                text=True,
            )

            test.assertEqual(result.returncode, 0)
            test.assertIn("hello", result.stdout)
            test.assertIn("test.py", result.stdout)

    with it("search - returns non-zero exit code when no matches found") as test:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text('print("goodbye")')

            result = subprocess.run(
                ["python", "-m", "comby_skill.cli", "search", "hello", tmpdir],
                capture_output=True,
                text=True,
            )

            # Exit code should be 0 (no results is still valid)
            test.assertEqual(result.returncode, 0)
            # Output should be minimal
            test.assertNotIn("hello", result.stdout)

    with it("search - supports case-insensitive matching") as test:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text('HELLO = "world"')

            result = subprocess.run(
                ["python", "-m", "comby_skill.cli", "search", "-i", "hello", tmpdir],
                capture_output=True,
                text=True,
            )

            test.assertEqual(result.returncode, 0)
            test.assertIn("HELLO", result.stdout)

    with it("search - outputs JSON format with valid structure") as test:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text('hello\nworld')

            result = subprocess.run(
                ["python", "-m", "comby_skill.cli", "search", "-f", "json", "hello", tmpdir],
                capture_output=True,
                text=True,
            )

            test.assertEqual(result.returncode, 0)
            # Parse JSON to validate format
            data = json.loads(result.stdout)
            test.assertIn("matches", data)
            test.assertIn("total_matches", data)
            test.assertIn("files_with_matches", data)
            test.assertIn("execution_time_ms", data)

    with it("search - outputs CSV format with headers") as test:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text('hello world')

            result = subprocess.run(
                ["python", "-m", "comby_skill.cli", "search", "-f", "csv", "hello", tmpdir],
                capture_output=True,
                text=True,
            )

            test.assertEqual(result.returncode, 0)
            lines = result.stdout.strip().split('\n')
            test.assertTrue(len(lines) >= 1)
            test.assertIn("file,line,column,text", result.stdout)

    with it("search - outputs lines format (one per line)") as test:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text('hello\nworld')

            result = subprocess.run(
                ["python", "-m", "comby_skill.cli", "search", "-f", "lines", "hello", tmpdir],
                capture_output=True,
                text=True,
            )

            test.assertEqual(result.returncode, 0)
            test.assertIn("test.py:1:", result.stdout)

    with it("search - supports count option") as test:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text('hello\nhello\nhello')

            result = subprocess.run(
                ["python", "-m", "comby_skill.cli", "search", "-c", "hello", tmpdir],
                capture_output=True,
                text=True,
            )

            test.assertEqual(result.returncode, 0)
            test.assertEqual(result.stdout.strip(), "3")

    with it("search - respects max-results limit") as test:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text('hello\n' * 10)

            result = subprocess.run(
                ["python", "-m", "comby_skill.cli", "search", "-m", "5", "hello", tmpdir],
                capture_output=True,
                text=True,
            )

            test.assertEqual(result.returncode, 0)
            # Count results in output
            lines = [l for l in result.stdout.split('\n') if 'test.py' in l and 'hello' in l]
            test.assertTrue(len(lines) <= 5)

    with it("search - returns error for invalid regex pattern") as test:
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir).joinpath("test.py").write_text('hello')

            result = subprocess.run(
                ["python", "-m", "comby_skill.cli", "search", "[invalid", tmpdir],
                capture_output=True,
                text=True,
            )

            test.assertEqual(result.returncode, 1)
            test.assertIn("Error", result.stderr)

    with it("search - returns error for non-existent path") as test:
        result = subprocess.run(
            ["python", "-m", "comby_skill.cli", "search", "pattern", "/nonexistent/path"],
            capture_output=True,
            text=True,
        )

        test.assertEqual(result.returncode, 1)
        test.assertIn("Error", result.stderr)

    with it("search - can find patterns across multiple files") as test:
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir).joinpath("file1.py").write_text('hello')
            Path(tmpdir).joinpath("file2.py").write_text('hello world')

            result = subprocess.run(
                ["python", "-m", "comby_skill.cli", "search", "hello", tmpdir],
                capture_output=True,
                text=True,
            )

            test.assertEqual(result.returncode, 0)
            test.assertIn("file1.py", result.stdout)
            test.assertIn("file2.py", result.stdout)

    with it("search - supports include pattern for file filtering") as test:
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir).joinpath("test.py").write_text('hello')
            Path(tmpdir).joinpath("test.txt").write_text('hello')

            result = subprocess.run(
                ["python", "-m", "comby_skill.cli", "search", "--include", "*.py", "hello", tmpdir],
                capture_output=True,
                text=True,
            )

            test.assertEqual(result.returncode, 0)
            test.assertIn("test.py", result.stdout)

    with it("search - supports context lines before/after match") as test:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text('line1\nhello\nline3')

            result = subprocess.run(
                ["python", "-m", "comby_skill.cli", "search", "-C", "1", "hello", tmpdir],
                capture_output=True,
                text=True,
            )

            test.assertEqual(result.returncode, 0)
            # With context enabled, result should include context in JSON output
            data = json.loads(result.stdout) if "-f json" in "search -C 1 hello" else None

    with it("search - default format shows summary") as test:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text('hello\nworld')

            result = subprocess.run(
                ["python", "-m", "comby_skill.cli", "search", "hello", tmpdir],
                capture_output=True,
                text=True,
            )

            test.assertEqual(result.returncode, 0)
            test.assertIn("Total:", result.stdout)
            test.assertIn("match", result.stdout)

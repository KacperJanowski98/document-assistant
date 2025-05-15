#!/usr/bin/env python
"""
Utility script to run code quality checks.
"""
import subprocess
import sys
from pathlib import Path


def print_header(title, char="="):
    """Print a section header."""
    header = char * len(title)
    print(f"\n{header}")
    print(title)
    print(f"{header}\n")


def run_command(command, description):
    """Run a command and print its output."""
    print_header(description)
    print(f"Running: {' '.join(command)}\n")
    
    process = subprocess.run(command, capture_output=True, text=True)
    
    if process.returncode == 0:
        print("✅ Success!")
        if process.stdout.strip():
            print("\nOutput:")
            print(process.stdout)
    else:
        print("❌ Failed!")
        if process.stderr.strip():
            print("\nError:")
            print(process.stderr)
        if process.stdout.strip():
            print("\nOutput:")
            print(process.stdout)
    
    return process.returncode == 0


def main():
    """Run all code quality checks."""
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    tests_dir = project_root / "tests"
    
    all_checks_passed = True
    
    # Ruff linting
    all_checks_passed &= run_command(
        ["python", "-m", "ruff", "check", str(src_dir), str(tests_dir)],
        "Ruff Linting Check"
    )
    
    # Ruff formatting
    all_checks_passed &= run_command(
        ["python", "-m", "ruff", "format", "--check", str(src_dir), str(tests_dir)],
        "Ruff Format Check"
    )
    
    # Run tests
    all_checks_passed &= run_command(
        ["python", "-m", "pytest", "-v", "--cov=src", "tests/"],
        "Running Tests with Coverage"
    )
    
    # Final summary
    print_header("Summary")
    if all_checks_passed:
        print("✅ All checks passed!")
    else:
        print("❌ Some checks failed. Please fix the issues before committing.")
    
    return 0 if all_checks_passed else 1


if __name__ == "__main__":
    sys.exit(main())

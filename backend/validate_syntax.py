#!/usr/bin/env python
"""
Validate Python code syntax
"""
import sys
import py_compile
from pathlib import Path

def validate_file(filepath):
    """Check if Python file has valid syntax"""
    try:
        py_compile.compile(str(filepath), doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("PYTHON CODE VALIDATION")
    print("=" * 60)
    
    # Find all Python files
    app_dir = Path("app")
    py_files = list(app_dir.rglob("*.py"))
    
    print(f"\nChecking {len(py_files)} files...\n")
    
    errors = []
    for py_file in sorted(py_files):
        success, error = validate_file(py_file)
        status = "✅" if success else "❌"
        print(f"{status} {py_file}")
        
        if not success:
            errors.append((py_file, error))
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Total: {len(py_files)} files")
    print(f"Valid: {len(py_files) - len(errors)}")
    print(f"Errors: {len(errors)}")
    print("=" * 60)
    
    if errors:
        print("\nERRORS:\n")
        for filepath, error in errors:
            print(f"❌ {filepath}")
            print(f"   {error}\n")
        return 1
    else:
        print("\n✅ All files have valid syntax!")
        return 0

if __name__ == "__main__":
    sys.exit(main())

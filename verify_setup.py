#!/usr/bin/env python3
"""
System Verification & Setup Script

Checks that all components are properly installed and working.
Run this before using the system: python verify_setup.py
"""

import sys
import subprocess

def check_module(module_name, display_name):
    """Check if a Python module is installed."""
    try:
        __import__(module_name)
        print(f"✅ {display_name:20} installed")
        return True
    except ImportError:
        print(f"❌ {display_name:20} NOT installed")
        return False


def main():
    print("\n" + "="*70)
    print("CONTEXT-WINDOW-AWARE RAG SYSTEM - SETUP VERIFICATION")
    print("="*70 + "\n")
    
    # Check Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"Python Version: {py_version}")
    if sys.version_info.major >= 3 and sys.version_info.minor >= 8:
        print("✅ Python 3.8+ detected\n")
    else:
        print("❌ Python 3.8+ required\n")
        return False
    
    # Check required packages
    print("Checking Required Packages:")
    print("-" * 70)
    
    checks = [
        ("tiktoken", "Tiktoken (Token Counter)"),
        ("streamlit", "Streamlit (Web UI)"),
        ("requests", "Requests (HTTP Client)"),
    ]
    
    all_good = True
    for module, display in checks:
        if not check_module(module, display):
            all_good = False
    
    print("\n" + "="*70)
    
    if not all_good:
        print("❌ Some packages are missing. Installing...\n")
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements.txt"
        ])
        print("\n✅ Installation complete!\n")
    
    # Verify core files
    print("Checking Core Files:")
    print("-" * 70)
    
    import os
    files = [
        "rag_core.py",
        "assembler.py",
        "app.py",
        "cli.py",
        "test_demo.py",
    ]
    
    for filename in files:
        if os.path.exists(filename):
            size_kb = os.path.getsize(filename) / 1024
            print(f"✅ {filename:20} ({size_kb:6.1f} KB)")
        else:
            print(f"❌ {filename:20} MISSING")
            all_good = False
    
    print("\n" + "="*70)
    
    if all_good:
        print("\n✅ ALL CHECKS PASSED - System is ready to use!\n")
        print("Quick Start Commands:")
        print("-" * 70)
        print("  python test_demo.py              # Run comprehensive tests")
        print("  python cli.py                    # Interactive CLI mode")
        print("  python cli.py --budget           # Show budget configuration")
        print("  python -m streamlit run app.py   # Web dashboard\n")
        return True
    else:
        print("\n❌ SETUP INCOMPLETE - Please fix issues above\n")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

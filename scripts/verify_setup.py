#!/usr/bin/env python3
"""
Verification script to check that all dependencies are properly installed.
"""

import sys
import importlib

def check_import(module_name, package_name=None):
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name} - FAILED: {e}")
        return False

def main():
    """Main verification function."""
    print("🔍 Verifying project setup...\n")
    
    # Core dependencies
    print("📦 Core Dependencies:")
    core_deps = [
        ("requests", "requests"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
    ]
    
    core_success = all(check_import(module, name) for module, name in core_deps)
    
    # Development dependencies
    print("\n🛠️  Development Dependencies:")
    dev_deps = [
        ("pytest", "pytest"),
        ("black", "black"),
        ("flake8", "flake8"),
    ]
    
    dev_success = all(check_import(module, name) for module, name in dev_deps)
    
    # AISafetyLab dependency
    print("\n🔬 AISafetyLab Dependency:")
    aisafetylab_success = check_import("aisafetylab", "AISafetyLab")
    
    # Summary
    print("\n" + "="*50)
    print("📊 SUMMARY:")
    print(f"Core dependencies: {'✅ All OK' if core_success else '❌ Some failed'}")
    print(f"Dev dependencies: {'✅ All OK' if dev_success else '❌ Some failed'}")
    print(f"AISafetyLab: {'✅ OK' if aisafetylab_success else '❌ Failed'}")
    
    if all([core_success, dev_success, aisafetylab_success]):
        print("\n🎉 All dependencies are properly installed!")
        return 0
    else:
        print("\n⚠️  Some dependencies failed to import. Please check the installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
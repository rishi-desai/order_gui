#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build Script for OSR Order GUI Zipapp
=====================================

This script creates a self-contained executable .pyz file that can be run
directly with Python.

Usage:
    python build.py                # Build order_gui.pyz
    python build.py --output myapp.pyz  # Custom output name
    python build.py --clean-only   # Just clean, don't build
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_cleanup(prepare_zipapp=True):
    """Run the cleanup script to prepare for zipapp."""
    print("🧹 Cleaning up project...")

    cmd = [sys.executable, "cleanup.py"]
    if prepare_zipapp:
        cmd.append("--prepare-zipapp")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Cleanup failed: {result.stderr}")
        return False

    print("✅ Cleanup completed")
    return True


def create_zipapp(source_dir, output_file):
    """Create a zipapp from the source directory."""
    print(f"📦 Creating zipapp: {output_file}")

    # Use Python's zipapp module
    cmd = [
        sys.executable,
        "-m",
        "zipapp",
        str(source_dir),
        "-o",
        output_file,
        "-p",
        "/usr/bin/env python3",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Zipapp creation failed: {result.stderr}")
        return False

    print(f"✅ Successfully created {output_file}")
    return True


def make_executable(file_path):
    """Make the zipapp executable on Unix systems."""
    if os.name != "nt":  # Not Windows
        try:
            os.chmod(file_path, 0o755)
            print(f"✅ Made {file_path} executable")
        except OSError as e:
            print(f"⚠️  Could not make executable: {e}")


def test_zipapp(zipapp_path):
    """Test the created zipapp."""
    print(f"🧪 Testing {zipapp_path}...")

    cmd = [sys.executable, zipapp_path, "--test-imports"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Zipapp test passed")
        return True
    else:
        print(f"❌ Zipapp test failed: {result.stderr}")
        return False


def main():
    """Main build function."""
    parser = argparse.ArgumentParser(
        description="Build OSR Order GUI as a zipapp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                     # Build order_gui.pyz  
  python build.py -o my_app.pyz       # Custom output name
  python build.py --clean-only        # Just clean, don't build
  python build.py --no-test           # Skip testing after build
        """,
    )

    parser.add_argument(
        "-o",
        "--output",
        default="order_gui.pyz",
        help="Output zipapp filename (default: order_gui.pyz)",
    )

    parser.add_argument(
        "--clean-only", action="store_true", help="Only run cleanup, don't build zipapp"
    )

    parser.add_argument(
        "--no-test", action="store_true", help="Skip testing the built zipapp"
    )

    parser.add_argument(
        "--keep-readme",
        action="store_true",
        help="Keep README.md in the zipapp (default: always kept now)",
    )

    args = parser.parse_args()

    print("OSR Order GUI - Build Script")
    print("=" * 40)

    # Get current directory
    current_dir = Path.cwd()

    # Run cleanup (always keep documentation files)
    if not run_cleanup(prepare_zipapp=True):
        sys.exit(1)

    if args.clean_only:
        print("🎉 Cleanup completed. Exiting as requested.")
        return

    # Create zipapp
    if not create_zipapp(current_dir, args.output):
        sys.exit(1)

    # Make executable
    make_executable(args.output)

    # Test zipapp
    if not args.no_test:
        if not test_zipapp(args.output):
            print("⚠️  Zipapp was created but failed testing")
            sys.exit(1)

    # Final success message
    file_size = os.path.getsize(args.output) / 1024  # KB
    print(f"\n🎉 Build completed successfully!")
    print(f"📁 Output: {args.output} ({file_size:.1f} KB)")
    print(f"🚀 Run with: ./{args.output} or python {args.output}")


if __name__ == "__main__":
    main()

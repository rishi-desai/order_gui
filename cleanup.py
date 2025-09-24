#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cleanup Script for OSR Order GUI
================================

This script removes __pycache__ folders and .pyc files to prepare
the application for sharing or deployment.

Usage:
    python cleanup.py
"""

import os
import shutil
import sys


def remove_pycache_folders(root_dir, prepare_zipapp=False):
    """
    Recursively remove all __pycache__ folders and .pyc files.

    Args:
        root_dir (str): Root directory to start cleanup from
        prepare_zipapp (bool): If True, also remove files not needed for zipapp
    """
    removed_folders = []
    removed_files = []

    # Additional files to clean up
    temp_extensions = [".pyc", ".pyo", ".pyd", "~", ".bak", ".swp", ".tmp"]
    temp_dirs = ["__pycache__", ".pytest_cache", ".coverage", "htmlcov"]

    # Files to remove when preparing for zipapp (only temp files, keep documentation)
    zipapp_unwanted = [] if prepare_zipapp else []

    for root, dirs, files in os.walk(root_dir, topdown=False):
        # Remove temporary files
        for file in files:
            file_path = os.path.join(root, file)

            # Check for temp extensions
            if any(file.endswith(ext) for ext in temp_extensions):
                try:
                    os.remove(file_path)
                    removed_files.append(file_path)
                except OSError as e:
                    print(f"Warning: Could not remove {file_path}: {e}")

            # Remove editor backup files
            elif file.startswith(".#") or file.endswith("#"):
                try:
                    os.remove(file_path)
                    removed_files.append(file_path)
                except OSError as e:
                    print(f"Warning: Could not remove {file_path}: {e}")
            # Remove zipapp-unwanted files
            elif file in zipapp_unwanted:
                try:
                    os.remove(file_path)
                    removed_files.append(file_path)
                except OSError as e:
                    print(f"Warning: Could not remove {file_path}: {e}")

        # Remove temporary directories
        for temp_dir in temp_dirs:
            if temp_dir in dirs:
                temp_path = os.path.join(root, temp_dir)
                try:
                    shutil.rmtree(temp_path)
                    removed_folders.append(temp_path)
                except OSError as e:
                    print(f"Warning: Could not remove {temp_path}: {e}")

    return removed_folders, removed_files


def main():
    """Main cleanup function."""
    import argparse

    parser = argparse.ArgumentParser(description="Clean up OSR Order GUI directory")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually removing",
    )
    parser.add_argument(
        "--prepare-zipapp",
        action="store_true",
        help="Prepare for zipapp packaging (removes temporary files only)",
    )
    args = parser.parse_args()

    print("OSR Order GUI - Cleanup Script")
    print("=" * 40)

    if args.dry_run:
        print("DRY RUN MODE - No files will be actually removed")
        print("-" * 40)

    if args.prepare_zipapp:
        print("ZIPAPP PREPARATION MODE - Removing temporary files only")
        print("-" * 40)

    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"Cleaning up directory: {script_dir}")
    print("Removing temporary files and cache directories...")

    try:
        if args.dry_run:
            # Just show what would be removed
            removed_folders, removed_files = simulate_cleanup(
                script_dir, args.prepare_zipapp
            )
            print(f"\nWould remove {len(removed_folders)} directories")
            print(f"Would remove {len(removed_files)} files")
        else:
            removed_folders, removed_files = remove_pycache_folders(
                script_dir, args.prepare_zipapp
            )
            print(f"\nCleanup completed successfully!")
            print(f"Removed {len(removed_folders)} directories")
            print(f"Removed {len(removed_files)} files")

        if removed_folders:
            print("\nDirectories removed:")
            for folder in removed_folders:
                rel_path = os.path.relpath(folder, script_dir)
                print(f"  - {rel_path}")

        if removed_files and len(removed_files) <= 20:  # Don't spam if too many files
            print(f"\nFiles removed:")
            for file in removed_files:
                rel_path = os.path.relpath(file, script_dir)
                print(f"  - {rel_path}")
        elif removed_files:
            print(f"\nRemoved {len(removed_files)} files (too many to list)")

        if not args.dry_run:
            if args.prepare_zipapp:
                print("\nThe application is now ready for zipapp packaging!")
                print("Run: python -m zipapp . -o order_gui.pyz")
            else:
                print("\nThe application is now clean and ready for sharing!")

    except Exception as e:
        print(f"Error during cleanup: {e}")
        sys.exit(1)


def simulate_cleanup(root_dir, prepare_zipapp=False):
    """Simulate cleanup without actually removing files."""
    would_remove_folders = []
    would_remove_files = []

    temp_extensions = [".pyc", ".pyo", ".pyd", "~", ".bak", ".swp", ".tmp"]
    zipapp_unwanted = [] if prepare_zipapp else []

    temp_dirs = ["__pycache__", ".pytest_cache", ".coverage", "htmlcov"]

    for root, dirs, files in os.walk(root_dir, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            if (
                any(file.endswith(ext) for ext in temp_extensions)
                or file.startswith(".#")
                or file.endswith("#")
                or file in zipapp_unwanted
            ):
                would_remove_files.append(file_path)

        for temp_dir in temp_dirs:
            if temp_dir in dirs:
                temp_path = os.path.join(root, temp_dir)
                would_remove_folders.append(temp_path)

    return would_remove_folders, would_remove_files


if __name__ == "__main__":
    main()

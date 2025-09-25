#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OSR Order GUI - Main Entry Point

Terminal-based GUI for OSR order management.
See README.md for full documentation.
"""

import sys
import os
import argparse
import curses
import traceback

from utils.cli_tools import (
    test_imports,
    cleanup_history,
    clean_files,
    build_zipapp,
    test_system_connections,
    show_server_info,
)

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


def parse_arguments():
    """Parse and return command line arguments."""
    parser = argparse.ArgumentParser(
        description="OSR Order GUI v1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    ./order_gui.pyz                       # Normal operation
    ./order_gui.pyz --full-test           # Run full test suite
    ./order_gui.pyz --dry-run             # Test mode (no orders sent)
    ./order_gui.pyz --cleanup 1w          # Clean orders older than 1 week
    ./order_gui.pyz --cleanup 2023-12-01  # Clean orders before specific date
        """,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in test mode - no actual orders will be sent",
    )
    parser.add_argument(
        "--full-test", action="store_true", help="Run full test suite and exit"
    )
    parser.add_argument(
        "--cleanup",
        type=str,
        metavar="TIMEFRAME",
        help="Clean up order history (1d, 1w, 2w, 1m, all, or YYYY-MM-DD)",
    )
    parser.add_argument("--version", action="version", version="OSR Order GUI v1.0")
    parser.add_argument(
        "--server-info",
        action="store_true",
        help="Display server and environment information",
    )
    parser.add_argument(
        "--test-imports", action="store_true", help="Test all imports and exit"
    )
    parser.add_argument(
        "--test-system",
        action="store_true",
        help="Test database and system connections",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Build zipapp package (developer mode)",
    )
    parser.add_argument(
        "--clean-files",
        action="store_true",
        help="Clean temporary files and cache (developer mode)",
    )

    return parser.parse_args()


def main():
    """Application entry point."""
    try:
        args = parse_arguments()

        if args.full_test:
            test1 = test_imports()
            print("\n")
            test2 = test_system_connections()
            success = test1 and test2
            sys.exit(0 if success else 1)

        if args.test_imports:
            success = test_imports()
            sys.exit(0 if success else 1)

        if args.cleanup:
            success = cleanup_history(args.cleanup)
            sys.exit(0 if success else 1)

        if args.build:
            success = build_zipapp()
            sys.exit(0 if success else 1)

        if args.clean_files:
            success = clean_files()
            sys.exit(0 if success else 1)

        if args.test_system:
            success = test_system_connections()
            sys.exit(0 if success else 1)

        if args.server_info:
            success = show_server_info()
            sys.exit(0 if success else 1)

        try:
            from controllers.main_controller import MainController
            from config.constants import APP_NAME, APP_VERSION
        except ImportError as e:
            print(f"Error: Failed to import required modules: {e}")
            print("Make sure you're running this script from the order_gui directory")
            print("or that all required Python modules are installed.")
            print("\nTry running: python main.py --test-imports")
            sys.exit(1)

        controller = MainController(dry_run=args.dry_run)
        curses.wrapper(controller.run)

    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

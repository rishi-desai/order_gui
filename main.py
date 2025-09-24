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

# Add the current directory to Python path so imports work when run from anywhere
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


def parse_arguments():
    """Parse and return command line arguments."""
    parser = argparse.ArgumentParser(
        description="OSR Order GUI v1.0 - OSR Order Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Normal operation
  python main.py --dry-run          # Test mode (no orders sent)
  python main.py --config my.json   # Use custom config file
  python main.py --readme           # Display README documentation
  python main.py --cleanup 1w       # Clean orders older than 1 week
  python main.py --cleanup 2023-12-01  # Clean orders before specific date
        """,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in test mode - no actual orders will be sent",
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to custom configuration file (default: config.json)",
    )

    parser.add_argument(
        "--test-imports", action="store_true", help="Test all imports and exit"
    )

    parser.add_argument(
        "--readme", action="store_true", help="Display README documentation and exit"
    )

    parser.add_argument(
        "--cleanup",
        type=str,
        metavar="TIMEFRAME",
        help="Clean up order history (1d, 1w, 2w, 1m, all, or YYYY-MM-DD)",
    )

    parser.add_argument("--version", action="version", version="OSR Order GUI v1.0")

    return parser.parse_args()


def test_imports():
    """Test module imports and return success status."""
    print("Testing imports...")

    try:
        print("  ✓ Config modules...", end=" ")
        from config import constants, defaults

        print("OK")

        print("  ✓ UI modules...", end=" ")
        from ui import utils, dialog, menu, form

        print("OK")

        print("  ✓ Model modules...", end=" ")
        from models import config, database, history, order_sender, xml_generator

        print("OK")

        print("  ✓ Controller modules...", end=" ")
        from controllers import main_controller, order_controller, history_controller

        print("OK")

        print("  ✓ Utility modules...", end=" ")
        from utils import exceptions

        print("OK")

        print("\n✅ All imports successful!")
        return True

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def show_readme():
    """Display README content from the application."""
    try:
        # Try different methods to find README.md
        readme_content = None

        # Method 1: Try to read from archive using pkgutil
        try:
            import pkgutil

            readme_data = pkgutil.get_data(
                __name__.split(".")[0] if "." in __name__ else __name__, "README.md"
            )
            if readme_data:
                readme_content = readme_data.decode("utf-8")
        except (ImportError, FileNotFoundError, AttributeError):
            pass

        # Method 2: Try to read from current directory (for source execution)
        if not readme_content:
            readme_path = os.path.join(os.path.dirname(__file__), "README.md")
            if os.path.exists(readme_path):
                with open(readme_path, "r", encoding="utf-8") as f:
                    readme_content = f.read()

        # Method 3: Try to read from one directory up (common case)
        if not readme_content:
            readme_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "README.md"
            )
            if os.path.exists(readme_path):
                with open(readme_path, "r", encoding="utf-8") as f:
                    readme_content = f.read()

        if readme_content:
            print("=" * 60)
            print("OSR ORDER GUI - README")
            print("=" * 60)
            print(readme_content)
            print("=" * 60)
            return True
        else:
            print("README.md not found in the application directory.")
            print("This usually means you're running from source code.")
            print("Try: cat README.md")
            return False

    except Exception as e:
        print(f"Error reading README: {e}")
        return False


def cleanup_history(timeframe):
    """Clean up order history based on timeframe."""
    import json
    from datetime import datetime, timedelta

    try:
        # Import constants to get the history file path
        from config.constants import ORDERS_HISTORY_FILE

        if not os.path.exists(ORDERS_HISTORY_FILE):
            print("No order history file found. Nothing to clean.")
            return True

        # Load existing history
        with open(ORDERS_HISTORY_FILE, "r") as f:
            history = json.load(f)

        original_count = len(history.get("orders", []))

        if original_count == 0:
            print("Order history is already empty.")
            return True

        # Calculate cutoff date
        now = datetime.now()

        if timeframe == "all":
            cutoff_date = now  # Remove everything
        elif timeframe == "1d":
            cutoff_date = now - timedelta(days=1)
        elif timeframe == "1w":
            cutoff_date = now - timedelta(weeks=1)
        elif timeframe == "2w":
            cutoff_date = now - timedelta(weeks=2)
        elif timeframe == "1m":
            cutoff_date = now - timedelta(days=30)
        else:
            # Try to parse as date (YYYY-MM-DD)
            try:
                cutoff_date = datetime.strptime(timeframe, "%Y-%m-%d")
            except ValueError:
                print(f"Invalid timeframe: {timeframe}")
                print("Valid options: 1d, 1w, 2w, 1m, all, or YYYY-MM-DD")
                return False

        # Filter orders
        if timeframe == "all":
            filtered_orders = []
        else:
            filtered_orders = []
            for order in history.get("orders", []):
                order_time = datetime.fromisoformat(order.get("timestamp", ""))
                if order_time >= cutoff_date:
                    filtered_orders.append(order)

        # Update history
        history["orders"] = filtered_orders
        removed_count = original_count - len(filtered_orders)

        # Save updated history
        with open(ORDERS_HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)

        print(f"Order History Cleanup Complete")
        print(f"Original orders: {original_count}")
        print(f"Removed: {removed_count}")
        print(f"Remaining: {len(filtered_orders)}")

        if timeframe == "all":
            print("All order history has been cleared.")
        else:
            print(f"Removed orders older than {timeframe}")

        return True

    except ImportError:
        print(
            "Error: Could not import configuration. Run from the application directory."
        )
        return False
    except Exception as e:
        print(f"Error cleaning up history: {e}")
        return False


def main():
    """Application entry point."""
    try:
        # Parse command line arguments
        args = parse_arguments()

        # Test imports if requested
        if args.test_imports:
            success = test_imports()
            sys.exit(0 if success else 1)

        # Show README if requested
        if args.readme:
            success = show_readme()
            sys.exit(0 if success else 1)

        # Clean up history if requested
        if args.cleanup:
            success = cleanup_history(args.cleanup)
            sys.exit(0 if success else 1)

        # Try to import the main controller
        try:
            from controllers.main_controller import MainController
            from config.constants import APP_NAME, APP_VERSION
        except ImportError as e:
            print(f"Error: Failed to import required modules: {e}")
            print("Make sure you're running this script from the order_gui directory")
            print("or that all required Python modules are installed.")
            print("\nTry running: python main.py --test-imports")
            sys.exit(1)

        # Initialize and run the main controller
        controller = MainController(dry_run=args.dry_run, config_file=args.config)

        # Start the application with curses wrapper
        import curses

        curses.wrapper(controller.run)

    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
CLI Tools and Utilities

Common functionality for command-line operations including:
- Import testing
- File cleanup
- System diagnostics
- Build operations
"""

import sys
import os
import json
import shutil
import subprocess
import platform
import socket
from pathlib import Path
from datetime import datetime, timedelta


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


def cleanup_history(timeframe):
    """Clean up order history based on timeframe."""
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


def clean_files():
    """Clean temporary files and cache directories."""
    print("🧹 Cleaning temporary files...")

    removed_folders = []
    removed_files = []

    # File extensions to remove
    temp_extensions = [".pyc", ".pyo", ".pyd", "~", ".bak", ".swp", ".tmp"]

    # Directories to remove
    temp_dirs = ["__pycache__", ".pytest_cache", ".coverage", "htmlcov"]

    # Get the application root directory (one level up from utils)
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for root, dirs, files in os.walk(script_dir, topdown=False):
        # Remove temporary files
        for file in files:
            file_path = os.path.join(root, file)

            if (
                any(file.endswith(ext) for ext in temp_extensions)
                or file.startswith(".#")
                or file.endswith("#")
            ):
                try:
                    os.remove(file_path)
                    removed_files.append(os.path.relpath(file_path, script_dir))
                except OSError as e:
                    print(f"Warning: Could not remove {file_path}: {e}")

        # Remove temporary directories
        for temp_dir in temp_dirs:
            if temp_dir in dirs:
                temp_path = os.path.join(root, temp_dir)
                try:
                    shutil.rmtree(temp_path)
                    removed_folders.append(os.path.relpath(temp_path, script_dir))
                except OSError as e:
                    print(f"Warning: Could not remove {temp_path}: {e}")

    print(
        f"""
        🗑️ Removed {len(removed_folders)} directories: {removed_folders}
        🗑️ Removed {len(removed_files)} files: {removed_files}
        """
    )
    return True


def build_zipapp(output_file="order_gui.pyz"):
    """Build zipapp package."""
    print("📦 Building zipapp...")

    # Clean files first
    if not clean_files():
        return False

    # Get the application root directory
    current_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_path = current_dir / output_file

    # Remove existing zipapp file if it exists
    if output_path.exists():
        try:
            output_path.unlink()
            print(f"🗑️  Removed existing {output_file}")
        except OSError as e:
            print(f"❌ Failed to remove existing {output_file}: {e}")
            return False

    # Create zipapp
    cmd = [
        sys.executable,
        "-m",
        "zipapp",
        str(current_dir),
        "-o",
        str(output_path),
        "-p",
        "/usr/bin/env python3",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Zipapp creation failed: {result.stderr}")
        return False

    output_path = current_dir / output_file

    # Make executable on Unix systems
    if os.name != "nt":
        try:
            os.chmod(output_path, 0o755)
        except OSError:
            pass

    # Test the zipapp
    test_cmd = [sys.executable, str(output_path), "--test-imports"]
    test_result = subprocess.run(test_cmd, capture_output=True, text=True)

    if test_result.returncode == 0:
        file_size = os.path.getsize(output_path) / 1024
        print(f"✅ Successfully built {output_file} ({file_size:.1f} KB)")
        print(f"🚀 Run with: ./{output_file} or python3 {output_file}")
        return True
    else:
        print(f"❌ Zipapp test failed: {test_result.stderr}")
        return False


def test_system_connections():
    """Test database and system connections."""
    print("🔍 Testing system connections...")

    # Connection test results
    connection_results = {"database": False, "corba": False, "overall": False}

    # Test Oracle database connection
    try:
        print("  📊 Testing Oracle database availability...", end=" ")

        # Check if oracle module is available
        try:
            import oracle

            print("✅ Oracle module available")

            # Test database connection with a test OSRID
            from models.database import Database

            test_osrid = "osr1"  # Use a test OSRID
            db = Database(
                test_osrid, retries=1, delay=1
            )  # Quick test with minimal retries

            print("  📊 Testing database connection...", end=" ")
            # Try to establish connection (this will fail gracefully if no DB available)
            try:
                connection = db.connect()
                if connection:
                    connection.close()  # Close test connection
                print("✅ Database connection successful")
                connection_results["database"] = True
            except Exception as conn_e:
                print(f"⚠️  Database connection failed: {conn_e}")

        except ImportError:
            print("❌ Oracle module not available")

    except ImportError as e:
        print(f"❌ Database module import failed: {e}")
    except Exception as e:
        print(f"❌ Database test failed: {e}")

    # Test CORBA/ORB connection
    try:
        print("  🔌 Testing CORBA ORB availability...", end=" ")

        # Check if CORBA modules are available
        from models.order_sender import CORBA_AVAILABLE

        if CORBA_AVAILABLE:
            print("✅ CORBA modules available")

            print("  🔌 Testing CORBA ORB initialization...", end=" ")
            try:
                from omniORB import CORBA

                # Try to initialize ORB (this is a basic test)
                orb = CORBA.ORB_init([], CORBA.ORB_ID)
                if orb:
                    print("✅ CORBA ORB initialization successful")
                    connection_results["corba"] = True
                else:
                    print("⚠️  CORBA ORB initialization failed")

            except Exception as orb_e:
                print(f"⚠️  CORBA ORB test failed: {orb_e}")
        else:
            print("❌ CORBA modules not available")

    except ImportError as e:
        print(f"❌ CORBA module import failed: {e}")
    except Exception as e:
        print(f"❌ CORBA test failed: {e}")

    # Test network connectivity (basic)
    try:
        print("  🌐 Testing network connectivity...", end=" ")
        import socket

        # Test basic network connectivity by trying to resolve a hostname
        socket.gethostbyname(socket.gethostname())
        print("✅ Network connectivity OK")

    except Exception as e:
        print(f"⚠️  Network connectivity issue: {e}")

    # Test environment variables
    try:
        print("  🌍 Checking environment variables...", end=" ")

        required_env_vars = ["PATH"]  # Basic required env var
        optional_env_vars = ["OSR_ID", "ORACLE_HOME", "LD_LIBRARY_PATH"]

        missing_required = [var for var in required_env_vars if not os.environ.get(var)]
        if missing_required:
            print(f"❌ Missing required env vars: {missing_required}")
        else:
            print("✅ Required environment variables OK")

        # Report on optional vars
        for var in optional_env_vars:
            value = os.environ.get(var)
            if value:
                print(f"    ✓ {var}: {value[:50]}{'...' if len(value) > 50 else ''}")
            else:
                print(f"    - {var}: Not set")

    except Exception as e:
        print(f"❌ Environment variable check failed: {e}")

    # Summary
    print("\n📋 Connection Test Summary:")
    print(
        f"  Database: {'✅ Ready' if connection_results['database'] else '❌ Not available'}"
    )
    print(
        f"  CORBA:    {'✅ Ready' if connection_results['corba'] else '❌ Not available'}"
    )

    # Determine overall status
    connection_results["overall"] = (
        connection_results["database"] or connection_results["corba"]
    )

    if connection_results["overall"]:
        print(
            "✅ System connection test completed - At least one connection type is available"
        )
    else:
        print(
            "⚠️  System connection test completed - No connections are fully available"
        )
        print("   Note: This may be expected in development environments")

    return connection_results["overall"]


def show_server_info():
    """Display server and environment information."""
    print("🖥️  Server Information")
    print("=" * 50)

    # Basic system info
    print(f"Hostname: {socket.gethostname()}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {platform.python_version()}")
    print(f"Python Path: {sys.executable}")

    # Current directory info
    print(f"Working Directory: {os.getcwd()}")

    # Check for config files
    print("\n📁 Configuration Files:")
    config_files = [".orders_config.json", ".order_history.json"]

    for config_file in config_files:
        if os.path.exists(config_file):
            size = os.path.getsize(config_file)
            print(f"  ✅ {config_file} ({size} bytes)")
        else:
            print(f"  ❌ {config_file} (not found)")

    return True

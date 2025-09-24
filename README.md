# OSR Order GUI

Terminal-based GUI for creating and managing OSR orders. Please read through the README for setup, usage instructions, and how the application works.

## Quick Start

### Step 1: Setup Application

```bash
# Ensure you are using Python 3.6.8+

# Clone the repository
git clone https://github.com/rishi-desai/order_gui.git

# Change to the project directory
cd order_gui
```

You should now be able to see all the files in the `order_gui` directory. See [Directory Structure](#directory-structure) for details on what each folder / files does.

### Step 2: Build Application

This application is distributed as a single `.pyz` file using Python's zipapp module. Look for `order_gui.pyz` in the directory. If you do not see it, or want to rebuild it, run:

```bash
python3 build.py
# or
./build.py

# If you want to clean up temporary files
python3 cleanup.py
# or
./cleanup.py
```

That should create `order_gui.pyz` in the current directory. You can then delete the source files if you want to only keep the `.pyz` file or keep the source files if you want to implement any new custom features.

### Step 3: Run Application

To run the application on either a test or live server, just copy the `order_gui.pyz` file to the target server and run:

```bash
# Enable permissions if needed
chmod +x order_gui.pyz

# Run the application
./order_gui.pyz                 # Open GUI

# Command line options
./order_gui.pyz --help          # Show help
./order_gui.pyz --readme        # Show README
./order_gui.pyz --version       # Show version
./order_gui.pyz --test-imports  # Test imports and exit
./order_gui.pyz --cleanup 1w    # Clean orders older than 1 week
```

### Step 4: First Run Configuration

When you first run the application, it will take you through a initial setup to configure some necessary settings depending on your environment / project. This will create two files in the current directory:
- `order_gui_config.json` - Application settings
- `order_history.json` - Order tracking data

Then you'll be able to create, save, and send any order type supported by the application to the OSR system.

And that's it! I tried to make the application as user-friendly as possible, but if you run into any issues, please check the [Common Issues](#common-issues) section below. And if you want reach out for support, questions, feature requests, etc., please see the [Support](#support) section.

## Command Line Options

| Option                     | Description                              |
|----------------------------|------------------------------------------|
| `--dry-run`                | Test mode - no actual orders sent to OSR |
| `--test-imports`           | Test module imports and exit             |
| `--cleanup <timeframe>`    | Remove order history                     |
| `--readme`                 | Show README                              |
| `--version`                | Show version information                 |
| `--help`                   | Show detailed help and examples          |

## Features

- **Order Types**: Pick Standard/Manual, Inventory, Goods In/Add
- **Management**: History tracking, cancellation, status monitoring  
- **Integration**: Oracle database lookup, CORBA communication
- **Safety**: Dry-run mode, XML validation
- **Test Server Support**: Sandbox command generation for simulator interaction

## Requirements

- Python 3.6.8+
- Libraries: `curses`, `cx_Oracle`, CORBA libraries

## Navigation

## Directory Structure

```
order_gui/
├── main.py                 # Application entry point
├── __main__.py             # Zipapp entry point
├── build.py                # Build script for creating zipapp
├── cleanup.py              # Cleanup script for temp files
├── config/                 # Configuration and constants
│   ├── __init__.py         # Package initialization
│   ├── constants.py        # Order types, colors, symbols, file paths
│   └── defaults.py         # Default settings and XML templates
├── models/                 # Business logic and data handling
│   ├── __init__.py         # Package initialization
│   ├── config.py           # Settings management (Config class)
│   ├── database.py         # Oracle database operations (Database class)
│   ├── history.py          # Order tracking (History class)
│   ├── order_sender.py     # CORBA order transmission
│   ├── sandbox_commands.py # Test server sandbox command generation
│   └── xml_generator.py    # XML creation (OrderXML class)
├── ui/                     # User interface components
│   ├── __init__.py         # Package initialization
│   ├── dialog.py           # Message dialogs and input prompts
│   ├── form.py             # Field editing forms
│   ├── menu.py             # Menu navigation
│   └── utils.py            # UI utilities (colors, drawing, text)
├── controllers/            # Application flow control
│   ├── __init__.py         # Package initialization
│   ├── config_controller.py    # Settings management
│   ├── history_controller.py   # Order history and cancellation
│   ├── main_controller.py      # Main application flow
│   ├── order_controller.py     # Order creation workflow
│   └── sandbox_controller.py   # Test server sandbox operations
└── utils/                  # Utilities and exceptions
    ├── __init__.py         # Package initialization
    └── exceptions.py       # Custom exception classes
```

## Common Issues

| Problem                    | Solution                                        |
|----------------------------|-------------------------------------------------|
| Import errors              | Ensure `./order_gui.pyz --test-imports` passes  |
| Database connection failed | Verify `cx_Oracle` installation and access      |
| ORB connection failed      | Check `CORBA` libraries and OSR connectivity    |
| Permission denied          | Ensure correct permissions for `order_gui.pyz`  |

## Support

- **Author**: Rishi Desai
- **Contact**: rishi.desai@knapp.com
- **Version**: 1.0

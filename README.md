# OSR Order GUI

Terminal-based GUI for creating and managing OSR orders.

## Quick Start

```bash
# Production (single .pyz file) 
./order_gui.pyz                 # Run anywhere
./order_gui.pyz --help          # Show help
./order_gui.pyz --readme        # Show README
./order_gui.pyz --version       # Show version
./order_gui.pyz --test-imports  # Test imports and exit
./order_gui.pyz --cleanup 1w    # Clean orders older than 1 week
```

## Command Line Options

| Option                     | Description                              |
|----------------------------|------------------------------------------|
| `--dry-run`                | Test mode - no actual orders sent to OSR |
| `--config FILE`            | Use custom configuration file            |
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
- **Distribution**: Single-file zipapp for deployment
- **Test Server Support**: Sandbox command generation for simulator interaction

### Test Server Features

When running on test servers, the application provides additional functionality:

- **Server Type Configuration**: Select between Live and Test server modes
- **Sandbox Command Generation**: Automatically generate simulator commands for carrier insertion
- **Clipboard Integration**: Copy commands to clipboard for easy pasting
- **Order History Integration**: Generate sandbox commands for previously sent orders

#### Sandbox Commands

The application generates commands in the format:
```bash
simosr1 --insert-carrier <element> <carrier> [position]
simosr1 --show-carriers <element>
simosr1 --remove-carrier <element> <carrier>
```

**Element Selection Features:**
- Choose from common workflow elements (input/output stations, shuttles, lifts)
- Enter custom workflow elements
- Save frequently used custom elements for future use
- Default element configuration

**Common Elements:**
- `workflow.input.station.01/02` - Input stations
- `workflow.output.station.01/02` - Output stations  
- `workflow.shuttle.aisle.01/02` - Shuttle aisles
- `workflow.lift.01/02` - Lift systems

These commands can be executed in the sandbox shell as:
- `ssh sandbox@host` - SSH into sandbox user
- `su - sandbox` - Switch to sandbox user (from osr user)  
- `sudo -u sandbox bash -lic 'command'` - Execute as sandbox user

## Requirements

- Python 3.6.8+
- Libraries: `curses`, `cx_Oracle`, CORBA libraries

## Navigation

- **Arrow Keys**: Navigate menus and forms
- **Enter**: Select/confirm 
- **Escape/q**: Back/quit
- **Tab**: Next field in forms

## Build Tools

```bash
# Only when working with the physical files not the zipapp distribution
python main.py --help          # Show help
python main.py --test-imports  # Test imports and exit
python build.py                # Create single-file .pyz distribution
python cleanup.py              # Remove temporary files
```

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

## Configuration

First run creates:
- `order_gui_config.json` - Application settings
- `order_history.json` - Order tracking data

## Common Issues

| Problem                    | Solution                                   |
|----------------------------|--------------------------------------------|
| Import errors              | Run from correct directory with `main.py`  |
| Database connection failed | Verify cx_Oracle installation and access   |
| ORB connection failed      | Check CORBA libraries and OSR connectivity |
| Permission denied          | Ensure write permissions in app directory  |

## Support

- **Author**: Rishi Desai
- **Contact**: rishi.desai@knapp.com
- **Version**: 1.0

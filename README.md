# Stardew Valley Mod Loader

A simple GUI application for managing Stardew Valley mods with drag-and-drop support.

## Features

- 🎯 **Drag & Drop Installation** - Simply drag mod archives into the app
- 📥 **URL Downloads** - Download mods directly from URLs
- 📦 **Archive Support** - Works with ZIP, 7Z, and RAR files
- 🔄 **Mod Management** - Enable/disable/delete mods easily
- 🎮 **Auto-Detection** - Automatically finds your Stardew Valley mods folder
- 💾 **Cross-Platform** - Works on Windows and macOS

## Installation

### Option 1: Run from Source (Requires Python)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

### Option 2: Standalone Executable (No Python Required)

Download the pre-built executable from releases and double-click to run!

## Building Standalone Executable

To create a standalone executable that doesn't require Python:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:

**Windows:**
```bash
pyinstaller --onefile --windowed --name "StardewModLoader" --icon=icon.ico main.py
```

**macOS:**
```bash
pyinstaller --onefile --windowed --name "StardewModLoader" main.py
```

3. Find your executable in the `dist/` folder

The executable will be completely self-contained with all dependencies bundled.

## Usage

1. **Launch the application**
2. **Install mods** by either:
   - Dragging mod archive files into the drop zone
   - Clicking "Browse Files" to select mods
   - Entering a download URL and clicking "Download"
3. **Manage mods** from the installed mods list:
   - Enable/Disable mods
   - Delete unwanted mods
   - Open the mods folder directly

## Supported Archive Formats

- `.zip` - ZIP archives
- `.7z` - 7-Zip archives
- `.rar` - RAR archives

## Configuration

The app automatically detects your Stardew Valley mods folder. If needed, you can:
- Change the mods folder via Settings → Change Mods Folder
- Configuration is saved in `~/.stardew_mod_loader_config.json`

## Requirements (Source Only)

- Python 3.7+
- tkinterdnd2
- requests
- py7zr
- rarfile

## License

Free to use and modify.

## Notes

- Requires SMAPI to be installed for mods to work in Stardew Valley
- Always backup your mods folder before making changes
- Some mods may require additional dependencies

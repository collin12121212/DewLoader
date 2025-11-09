"""
Stardew Valley Mod Loader
A GUI application for managing Stardew Valley mods with drag-and-drop support.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinterdnd2 import DND_FILES, TkinterDnD
import requests
import zipfile
import py7zr
import rarfile
import json
import os
import shutil
import threading
from pathlib import Path
from typing import Optional, List, Dict
import platform
import re


class StardewModLoader:
    def __init__(self, root):
        self.root = root
        self.root.title("Stardew Valley Mod Loader")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Configuration
        self.config_file = Path.home() / ".stardew_mod_loader_config.json"
        self.config = self.load_config()
        
        # Detect or load mods path
        self.mods_path = self.get_mods_path()
        
        # Create UI
        self.create_ui()
        
        # Load installed mods
        self.refresh_mods_list()
        
        # Start auto-refresh
        self.auto_refresh_mods()
    
    def load_config(self) -> dict:
        """Load configuration from JSON file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def get_mods_path(self) -> Path:
        """Auto-detect Stardew Valley Mods folder"""
        # Check if custom path is saved in config
        if 'mods_path' in self.config:
            custom_path = Path(self.config['mods_path'])
            if custom_path.exists():
                return custom_path
        
        # Auto-detect based on OS
        detected_path = self.detect_stardew_mods_folder()
        return detected_path
    
    def detect_stardew_mods_folder(self) -> Path:
        """Detect Stardew Valley Mods folder based on OS"""
        system = platform.system()
        
        if system == "Windows":
            # Check AppData path
            appdata = Path(os.getenv('APPDATA', ''))
            default_path = appdata / "StardewValley" / "Mods"
            
            if default_path.exists():
                return default_path
            
            # Check Steam common locations
            steam_paths = [
                Path("C:/Program Files (x86)/Steam/steamapps/common/Stardew Valley/Mods"),
                Path("C:/Program Files/Steam/steamapps/common/Stardew Valley/Mods"),
            ]
            
            for path in steam_paths:
                if path.exists():
                    return path
                    
        elif system == "Darwin":  # macOS
            home = Path.home()
            
            # Check default path
            default_path = home / ".config" / "StardewValley" / "Mods"
            if default_path.exists():
                return default_path
            
            # Check Steam path
            steam_path = home / "Library" / "Application Support" / "Steam" / "steamapps" / "common" / "Stardew Valley" / "Mods"
            if steam_path.exists():
                return steam_path
        
        # Return default if nothing found
        return Path.home() / "StardewValley" / "Mods"
    
    def get_stardew_game_folder(self) -> Path:
        """Get the Stardew Valley game installation folder"""
        system = platform.system()
        
        if system == "Windows":
            # Check Steam common locations
            steam_paths = [
                Path("C:/Program Files (x86)/Steam/steamapps/common/Stardew Valley"),
                Path("C:/Program Files/Steam/steamapps/common/Stardew Valley"),
            ]
            
            for path in steam_paths:
                if path.exists():
                    return path
                    
        elif system == "Darwin":  # macOS
            home = Path.home()
            steam_path = home / "Library" / "Application Support" / "Steam" / "steamapps" / "common" / "Stardew Valley"
            if steam_path.exists():
                return steam_path
        
        # Fallback to detected mods path parent or home
        mods_path = self.detect_stardew_mods_folder()
        if mods_path.exists() and mods_path.name == "Mods":
            return mods_path.parent
        
        return Path.home()
    
    def create_ui(self):
        """Create the main user interface"""
        # Configure dark theme colors
        self.bg_color = "#1E1E1E"  # Dark background
        self.fg_color = "#D4D4D4"  # Light text
        self.accent_color = "#007ACC"  # Blue accent
        self.bg_secondary = "#252526"  # Secondary background
        self.bg_tertiary = "#2D2D30"  # Tertiary background
        self.border_color = "#3E3E42"  # Border color
        self.highlight_color = "#094771"  # Selection highlight
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure frame styles
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabelframe', background=self.bg_color, foreground=self.fg_color, 
                       bordercolor=self.border_color, relief=tk.FLAT)
        style.configure('TLabelframe.Label', background=self.bg_color, foreground=self.fg_color,
                       font=('Segoe UI', 10, 'bold'))
        
        # Configure label styles
        style.configure('TLabel', background=self.bg_color, foreground=self.fg_color,
                       font=('Segoe UI', 9))
        
        # Configure button styles
        style.configure('TButton', 
                       background=self.bg_tertiary, 
                       foreground=self.fg_color,
                       bordercolor=self.border_color, 
                       focuscolor=self.accent_color,
                       lightcolor=self.bg_tertiary,
                       darkcolor=self.bg_tertiary,
                       font=('Segoe UI', 9), 
                       padding=6)
        style.map('TButton',
                 background=[('active', self.highlight_color), ('pressed', self.accent_color)],
                 foreground=[('active', 'white'), ('!disabled', self.fg_color)],
                 lightcolor=[('pressed', self.accent_color)],
                 darkcolor=[('pressed', self.accent_color)])
        
        # Configure entry styles
        style.configure('TEntry', fieldbackground=self.bg_tertiary, foreground=self.fg_color,
                       bordercolor=self.border_color, insertcolor=self.fg_color,
                       font=('Segoe UI', 9))
        
        # Menu bar
        menubar = tk.Menu(self.root, bg=self.bg_secondary, fg=self.fg_color, 
                         activebackground=self.highlight_color, activeforeground='white',
                         borderwidth=0)
        self.root.config(menu=menubar)
        
        settings_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_secondary, fg=self.fg_color,
                               activebackground=self.highlight_color, activeforeground='white',
                               borderwidth=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Change Mods Folder", command=self.change_mods_path)
        settings_menu.add_separator()
        settings_menu.add_command(label="Exit", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_secondary, fg=self.fg_color,
                           activebackground=self.highlight_color, activeforeground='white',
                           borderwidth=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        secret_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_secondary, fg=self.fg_color,
                             activebackground=self.highlight_color, activeforeground='white',
                             borderwidth=0)
        menubar.add_cascade(label="Secret", menu=secret_menu)
        secret_menu.add_command(label="Click me!", command=self.show_secret)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Mods path display
        path_frame = ttk.LabelFrame(main_frame, text="Mods Directory", padding="8")
        path_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.path_label = ttk.Label(path_frame, text=str(self.mods_path), foreground=self.accent_color,
                                    font=('Segoe UI', 9))
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(path_frame, text="Change", command=self.change_mods_path).pack(side=tk.RIGHT)
        
        # Download section
        download_frame = ttk.LabelFrame(main_frame, text="Download Mod from URL", padding="10")
        download_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(download_frame, text="URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.url_entry = ttk.Entry(download_frame, width=60)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.download_btn = ttk.Button(download_frame, text="Download", command=self.download_mod)
        self.download_btn.grid(row=0, column=2)
        
        download_frame.columnconfigure(1, weight=1)
        
        # Drag and drop section
        dnd_frame = ttk.LabelFrame(main_frame, text="Install Mod from File", padding="10")
        dnd_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.drop_zone = tk.Label(
            dnd_frame,
            text="Drag & Drop mod files here\n(.zip, .7z, .rar)\n\nOr click Browse to select files",
            bg=self.bg_tertiary,
            fg=self.fg_color,
            relief=tk.FLAT,
            borderwidth=2,
            highlightthickness=2,
            highlightbackground=self.border_color,
            highlightcolor=self.accent_color,
            height=6,
            font=("Segoe UI", 11)
        )
        self.drop_zone.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Enable drag and drop
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Browse button
        ttk.Button(dnd_frame, text="Browse Files...", command=self.browse_files).pack(pady=(5, 0))
        
        # Installed mods section
        mods_frame = ttk.LabelFrame(main_frame, text="Installed Mods", padding="10")
        mods_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Mods list with scrollbar
        list_frame = ttk.Frame(mods_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.mods_listbox = tk.Listbox(
            list_frame, 
            yscrollcommand=scrollbar.set, 
            height=10,
            bg=self.bg_tertiary,
            fg=self.fg_color,
            selectbackground=self.highlight_color,
            selectforeground='white',
            highlightthickness=1,
            highlightbackground=self.border_color,
            highlightcolor=self.accent_color,
            borderwidth=0,
            font=('Segoe UI', 9),
            activestyle='none'  # Prevents default selection style conflicts
        )
        self.mods_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.mods_listbox.yview)
        
        # Store mod data for color coding
        self.mod_data = []
        
        # Mod action buttons
        btn_frame = tk.Frame(mods_frame, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Create buttons with explicit styling (removed Refresh button - now auto-refreshes)
        toggle_btn = tk.Button(
            btn_frame, text="Enable/Disable", command=self.toggle_mod,
            bg=self.bg_tertiary, fg=self.fg_color, activebackground=self.highlight_color,
            activeforeground='white', relief=tk.FLAT, borderwidth=0, padx=12, pady=6,
            font=('Segoe UI', 9), cursor='hand2'
        )
        toggle_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        delete_btn = tk.Button(
            btn_frame, text="Delete", command=self.delete_mod,
            bg=self.bg_tertiary, fg=self.fg_color, activebackground=self.highlight_color,
            activeforeground='white', relief=tk.FLAT, borderwidth=0, padx=12, pady=6,
            font=('Segoe UI', 9), cursor='hand2'
        )
        delete_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        open_btn = tk.Button(
            btn_frame, text="Open Mods Folder", command=self.open_mods_folder,
            bg=self.bg_tertiary, fg=self.fg_color, activebackground=self.highlight_color,
            activeforeground='white', relief=tk.FLAT, borderwidth=0, padx=12, pady=6,
            font=('Segoe UI', 9), cursor='hand2'
        )
        open_btn.pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            main_frame, 
            textvariable=self.status_var, 
            relief=tk.FLAT, 
            anchor=tk.W,
            bg=self.bg_secondary,
            fg=self.fg_color,
            font=('Segoe UI', 9),
            padx=8,
            pady=4
        )
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
    
    def change_mods_path(self):
        """Allow user to manually select mods directory"""
        # Get Stardew Valley game folder as starting directory
        initial_dir = self.get_stardew_game_folder()
        
        new_path = filedialog.askdirectory(
            title="Select Stardew Valley Mods Folder",
            initialdir=initial_dir
        )
        
        if new_path:
            self.mods_path = Path(new_path)
            self.config['mods_path'] = str(self.mods_path)
            self.save_config()
            self.path_label.config(text=str(self.mods_path))
            self.refresh_mods_list()
            self.status_var.set(f"Mods path changed to: {self.mods_path}")
    
    def browse_files(self):
        """Open file browser to select mod files"""
        # Get Downloads folder (cross-platform)
        downloads_folder = Path.home() / "Downloads"
        if not downloads_folder.exists():
            downloads_folder = Path.home()
        
        files = filedialog.askopenfilenames(
            title="Select Mod Archive(s)",
            initialdir=downloads_folder,
            filetypes=[
                ("Archive files", "*.zip *.7z *.rar"),
                ("ZIP files", "*.zip"),
                ("7Z files", "*.7z"),
                ("RAR files", "*.rar"),
                ("All files", "*.*")
            ]
        )
        
        if files:
            for file_path in files:
                self.install_mod(file_path)
    
    def handle_drop(self, event):
        """Handle drag and drop events"""
        files = self.parse_drop_files(event.data)
        
        for file_path in files:
            if os.path.isfile(file_path):
                self.install_mod(file_path)
    
    def parse_drop_files(self, data: str) -> List[str]:
        """Parse dropped file paths (handles spaces and special characters)"""
        # Handle both Windows and Unix path formats
        files = []
        
        # Remove curly braces if present
        data = data.strip('{}')
        
        # Split by spaces but respect quoted paths
        pattern = r'[^\s"]+|"[^"]*"'
        matches = re.findall(pattern, data)
        
        for match in matches:
            path = match.strip('"').strip()
            if path:
                files.append(path)
        
        return files
    
    def install_mod(self, file_path: str):
        """Install a mod from an archive file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            messagebox.showerror("Error", f"File not found: {file_path}")
            return
        
        self.status_var.set(f"Installing {file_path.name}...")
        self.root.update()
        
        try:
            # Create mods directory if it doesn't exist
            self.mods_path.mkdir(parents=True, exist_ok=True)
            
            # Extract archive
            if file_path.suffix.lower() == '.zip':
                self.extract_zip(file_path)
            elif file_path.suffix.lower() == '.7z':
                self.extract_7z(file_path)
            elif file_path.suffix.lower() == '.rar':
                self.extract_rar(file_path)
            else:
                messagebox.showerror("Error", f"Unsupported file format: {file_path.suffix}")
                return
            
            self.status_var.set(f"Successfully installed {file_path.name}")
            # No need to manually refresh - auto-refresh will handle it
            messagebox.showinfo("Success", f"Mod installed successfully!\n\n{file_path.name}")
            
        except Exception as e:
            self.status_var.set("Installation failed")
            messagebox.showerror("Installation Error", f"Failed to install mod:\n{str(e)}")
    
    def extract_zip(self, file_path: Path):
        """Extract a ZIP archive"""
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Check if archive has a manifest.json
            manifest_found = self.find_manifest_in_archive(zip_ref.namelist())
            
            if manifest_found:
                # Extract to mods directory
                zip_ref.extractall(self.mods_path)
            else:
                messagebox.showwarning(
                    "Warning",
                    f"No manifest.json found in {file_path.name}.\n"
                    "This may not be a valid SMAPI mod.\n\n"
                    "Extracting anyway..."
                )
                zip_ref.extractall(self.mods_path)
    
    def extract_7z(self, file_path: Path):
        """Extract a 7Z archive"""
        with py7zr.SevenZipFile(file_path, 'r') as archive:
            archive.extractall(self.mods_path)
    
    def extract_rar(self, file_path: Path):
        """Extract a RAR archive"""
        with rarfile.RarFile(file_path, 'r') as rar_ref:
            rar_ref.extractall(self.mods_path)
    
    def find_manifest_in_archive(self, file_list: List[str]) -> bool:
        """Check if manifest.json exists in archive"""
        for file_name in file_list:
            if 'manifest.json' in file_name.lower():
                return True
        return False
    
    def download_mod(self):
        """Download a mod from URL"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("No URL", "Please enter a URL to download from.")
            return
        
        # Run download in separate thread to avoid blocking UI
        thread = threading.Thread(target=self._download_mod_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def _download_mod_thread(self, url: str):
        """Download mod in background thread"""
        try:
            self.status_var.set("Downloading...")
            self.download_btn.config(state='disabled')
            
            # Download file
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get filename from URL or Content-Disposition header
            filename = self.get_filename_from_response(response, url)
            
            # Save to temp location
            temp_file = Path.home() / "Downloads" / filename
            temp_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.status_var.set(f"Download complete: {filename}")
            
            # Install the downloaded file
            self.root.after(100, lambda: self.install_mod(str(temp_file)))
            
        except Exception as e:
            self.status_var.set("Download failed")
            self.root.after(100, lambda: messagebox.showerror("Download Error", f"Failed to download:\n{str(e)}"))
        
        finally:
            self.root.after(100, lambda: self.download_btn.config(state='normal'))
    
    def get_filename_from_response(self, response, url: str) -> str:
        """Extract filename from response headers or URL"""
        # Try Content-Disposition header first
        content_disp = response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disp:
            filename = content_disp.split('filename=')[1].strip('"')
            return filename
        
        # Fallback to URL
        filename = url.split('/')[-1].split('?')[0]
        
        # Ensure it has a valid extension
        if not any(filename.endswith(ext) for ext in ['.zip', '.7z', '.rar']):
            filename += '.zip'
        
        return filename
    
    def refresh_mods_list(self):
        """Refresh the list of installed mods"""
        self.mods_listbox.delete(0, tk.END)
        self.mod_data = []
        
        if not self.mods_path.exists():
            self.status_var.set(f"Mods folder not found: {self.mods_path} - Make sure SMAPI is installed!")
            return
        
        mods = []
        
        try:
            for item in self.mods_path.iterdir():
                if item.is_dir():
                    mod_name = item.name
                    
                    # Check if disabled
                    disabled = mod_name.endswith('.disabled')
                    if disabled:
                        mod_name = mod_name[:-9]  # Remove .disabled suffix
                    
                    # Check for manifest.json
                    manifest_path = item / "manifest.json"
                    if manifest_path.exists():
                        try:
                            with open(manifest_path, 'r', encoding='utf-8') as f:
                                manifest = json.load(f)
                                mod_name = manifest.get('Name', mod_name)
                                version = manifest.get('Version', '')
                                if version:
                                    mod_name = f"{mod_name} (v{version})"
                        except:
                            pass
                    
                    # Store mod with disabled status
                    mods.append((mod_name, disabled))
            
            # Sort by name
            mods.sort(key=lambda x: x[0])
            
            # Add to listbox with color coding
            for i, (mod_name, disabled) in enumerate(mods):
                self.mods_listbox.insert(tk.END, mod_name)
                # Set color: red for disabled, green for enabled
                color = "#FF6B6B" if disabled else "#4CAF50"  # Red or Green
                self.mods_listbox.itemconfig(i, fg=color)
                self.mod_data.append({'name': mod_name, 'disabled': disabled})
            
            self.status_var.set(f"Found {len(mods)} mod(s)")
            
        except Exception as e:
            self.status_var.set(f"Error reading mods: {e}")
    
    def auto_refresh_mods(self):
        """Auto-refresh mods list periodically without causing lag"""
        try:
            # Only refresh if the mods path exists
            if self.mods_path.exists():
                # Store current selection
                current_selection = self.mods_listbox.curselection()
                current_item = None
                if current_selection:
                    current_item = self.mods_listbox.get(current_selection[0])
                
                # Refresh the list
                self.refresh_mods_list()
                
                # Restore selection if possible
                if current_item:
                    for i in range(self.mods_listbox.size()):
                        if self.mods_listbox.get(i) == current_item:
                            self.mods_listbox.selection_set(i)
                            break
        except:
            pass  # Silently fail to avoid interrupting user
        
        # Schedule next refresh in 3 seconds
        self.root.after(3000, self.auto_refresh_mods)
    
    def toggle_mod(self):
        """Enable or disable selected mod"""
        selection = self.mods_listbox.curselection()
        
        if not selection:
            messagebox.showwarning("No Selection", "Please select a mod to enable/disable.")
            return
        
        mod_name = self.mods_listbox.get(selection[0])
        
        # Get clean name and disabled status
        clean_name = mod_name.split(' (v')[0]
        # Check stored mod data for disabled status
        idx = selection[0]
        is_disabled = self.mod_data[idx]['disabled'] if idx < len(self.mod_data) else False
        
        try:
            # Find the actual folder
            for item in self.mods_path.iterdir():
                if item.is_dir():
                    folder_name = item.name
                    
                    # Check manifest for real name
                    manifest_path = item / "manifest.json"
                    actual_name = folder_name.replace('.disabled', '')
                    
                    if manifest_path.exists():
                        try:
                            with open(manifest_path, 'r', encoding='utf-8') as f:
                                manifest = json.load(f)
                                actual_name = manifest.get('Name', actual_name)
                        except:
                            pass
                    
                    if actual_name == clean_name or folder_name.replace('.disabled', '') == clean_name:
                        if is_disabled:
                            # Enable mod (remove .disabled)
                            new_name = folder_name.replace('.disabled', '')
                            item.rename(self.mods_path / new_name)
                            self.status_var.set(f"Enabled: {clean_name}")
                        else:
                            # Disable mod (add .disabled)
                            new_name = folder_name + '.disabled'
                            item.rename(self.mods_path / new_name)
                            self.status_var.set(f"Disabled: {clean_name}")
                        
                        # Immediately refresh to show color change
                        self.refresh_mods_list()
                        return
            
            messagebox.showerror("Error", f"Could not find mod folder: {clean_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle mod:\n{str(e)}")
    
    def delete_mod(self):
        """Delete selected mod"""
        selection = self.mods_listbox.curselection()
        
        if not selection:
            messagebox.showwarning("No Selection", "Please select a mod to delete.")
            return
        
        mod_name = self.mods_listbox.get(selection[0])
        clean_name = mod_name.split(' (v')[0]
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete:\n{clean_name}?\n\nThis cannot be undone."
        )
        
        if not result:
            return
        
        try:
            # Find and delete the folder
            for item in self.mods_path.iterdir():
                if item.is_dir():
                    folder_name = item.name
                    
                    # Check manifest for real name
                    manifest_path = item / "manifest.json"
                    actual_name = folder_name.replace('.disabled', '')
                    
                    if manifest_path.exists():
                        try:
                            with open(manifest_path, 'r', encoding='utf-8') as f:
                                manifest = json.load(f)
                                actual_name = manifest.get('Name', actual_name)
                        except:
                            pass
                    
                    if actual_name == clean_name or folder_name.replace('.disabled', '') == clean_name:
                        shutil.rmtree(item)
                        self.status_var.set(f"Deleted: {clean_name}")
                        # No need to manually refresh - auto-refresh will handle it
                        messagebox.showinfo("Deleted", f"Successfully deleted {clean_name}")
                        return
            
            messagebox.showerror("Error", f"Could not find mod folder: {clean_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete mod:\n{str(e)}")
    
    def open_mods_folder(self):
        """Open the mods folder in file explorer"""
        try:
            if platform.system() == "Windows":
                os.startfile(self.mods_path)
            elif platform.system() == "Darwin":  # macOS
                os.system(f'open "{self.mods_path}"')
            else:  # Linux
                os.system(f'xdg-open "{self.mods_path}"')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("400x280")
        about_window.resizable(False, False)
        about_window.configure(bg=self.bg_color)
        
        # Center the window
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Content frame
        content_frame = tk.Frame(about_window, bg=self.bg_color, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            content_frame,
            text="Stardew Valley Mod Loader",
            bg=self.bg_color,
            fg=self.accent_color,
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Version
        version_label = tk.Label(
            content_frame,
            text="Version 1.0",
            bg=self.bg_color,
            fg=self.fg_color,
            font=('Segoe UI', 10)
        )
        version_label.pack(pady=(0, 15))
        
        # Description
        desc_text = (
            "A simple tool to manage Stardew Valley mods.\n\n"
            "Features:\n"
            "• Drag-and-drop installation\n"
            "• Download from URLs\n"
            "• Mod management (enable/disable/delete)\n\n"
            "Supported formats: ZIP, 7Z, RAR"
        )
        desc_label = tk.Label(
            content_frame,
            text=desc_text,
            bg=self.bg_color,
            fg=self.fg_color,
            font=('Segoe UI', 9),
            justify=tk.LEFT
        )
        desc_label.pack(pady=(0, 15))
        
        # Close button
        close_btn = tk.Button(
            content_frame,
            text="Close",
            command=about_window.destroy,
            bg=self.bg_tertiary,
            fg=self.fg_color,
            activebackground=self.highlight_color,
            activeforeground='white',
            relief=tk.FLAT,
            borderwidth=0,
            padx=20,
            pady=8,
            font=('Segoe UI', 9),
            cursor='hand2'
        )
        close_btn.pack()
    
    def show_secret(self):
        """Show secret message overlay"""
        # Create fullscreen overlay
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-topmost', True)
        overlay.configure(bg='#FF1493')  # Hot pink background
        
        # Create message
        message = tk.Label(
            overlay,
            text="I love you my baby",
            bg='#FF1493',
            fg='white',
            font=('Segoe UI', 72, 'bold')
        )
        message.pack(expand=True)
        
        # Add sparkle effect with hearts
        hearts = "💖 💕 💗 💓 💝"
        hearts_label = tk.Label(
            overlay,
            text=hearts,
            bg='#FF1493',
            fg='white',
            font=('Segoe UI', 48)
        )
        hearts_label.pack()
        
        # Auto-close after 4 seconds
        overlay.after(4000, overlay.destroy)


def main():
    """Main entry point"""
    root = TkinterDnD.Tk()
    app = StardewModLoader(root)
    root.mainloop()


if __name__ == "__main__":
    main()

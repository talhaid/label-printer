"""
Runtime hook for PyInstaller to ensure proper path handling
"""
import os
import sys

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Make sure the save directory exists
save_dir = os.path.join(os.getcwd(), "save")
csv_dir = os.path.join(save_dir, "csv")
zpl_dir = os.path.join(save_dir, "zpl_output")

for directory in [save_dir, csv_dir, zpl_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

print("Runtime path setup completed")

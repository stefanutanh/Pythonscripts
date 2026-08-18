# Python Automation & Utility Scripts

A collection of lightweight Python CLI utilities designed to automate system tasks and clean up duplicate files.

---

## 🛠 Features & Scripts

### 1. Wi-Fi Password Extractor (`wifi.py`)
Retrieves all saved Wi-Fi network profiles and passwords on a Windows machine.

* Identifies currently active Wi-Fi connection.
* Lists all saved SSIDs along with their cleartext credentials.
* Uses native Windows `netsh` integration.

**Usage:**
```bash
python wifi.py
```

### 2. Image Deduplicator (duplicate.py) (work in progress)

Scans a target directory and its subfolders to find identical image files using size filtering and cryptographic hash verification (SHA-256).
Safe Cleanup: Performs a dry-run by default, listing duplicates before any action is taken.
Quarantine Mode: Moves redundant copies to an isolated folder instead of permanently deleting them.
Conflict Safe: Automatically resolves name collisions to prevent overwriting files
Usage:
```bash
# Basic scan with default quarantine folder
python duplicate.py "path/to/images"
```

### Disclaimer
wifi.py is intended for administrative and personal recovery use on authorized devices only.

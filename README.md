<h1 align="center">📂 FileFlow</h1>
<p align="center">
Fast, Simple, and Safe File Sorting — Organize your downloads in seconds.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg">
  <img src="https://img.shields.io/badge/Platform-Windows%20|%20macOS%20|%20Linux-lightgrey.svg">
  <img src="https://img.shields.io/badge/License-MIT-green.svg">
</p>

---

## ✨ Features

- 🔎 **Live Preview** — See planned actions (*MOVE*, *SKIP*, *CONFLICT*) before touching files.  
- 🗂 **Smart Organization** — Sort by type: Images, Docs, Videos, Audio, Archives, Code, and more.  
- 🧩 **Custom Rules** — Map extensions (`.pdf`, `.jpg`, etc.) to folders via the built-in Rules Editor.  
- 🛡 **Safe Moves** — Hash-based duplicate detection + conflict resolution (skip or suffix).  
- 🧪 **Dry Run** — Test sorting without moving a single file.  
- ⏪ **Undo** — Restore everything from the last batch with one click.  
- 🧱 **Filters** — Ignore clutter (`node_modules`, `.git`, hidden/system files, etc.).  
- 🖥 **Cross-Platform UX** — Open/reveal files in Explorer (Win), Finder (macOS), or `xdg-open` (Linux).  

---

## 📦 Project Structure

```plaintext
.
├─ main.py
└─ src/
   ├─ gui.py           # Tkinter UI: Dashboard, Preview, Settings, Rules
   ├─ preview.py       # Live preview generator
   ├─ apply_moves.py   # Move execution, conflict handling, undo
   ├─ scanner.py       # Recursive file scanning with exclusions
   ├─ rules.py         # Extension → folder resolution
   ├─ config.py        # Defaults, validation, persistence
   ├─ types_map.py     # Default categories
   ├─ worker.py        # Background worker threads
   └─ utils/
      ├─ hash_utils.py # Buffered file hashing
      └─ os_ops.py     # OS-specific open/reveal actions
```

---

## 🚀 Running from Source

**Requirements**
- Python **3.10+**
- Tkinter (Linux: `sudo apt-get install python3-tk`)
- Linux file opening: `sudo apt-get install xdg-utils`
- Clone this repo: ``` git clone https://github.com/AryanSLAYERRR/FileFlow ```
- cd into Fileflow

**Windows (PowerShell)**  
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip wheel setuptools
python main.py
```

**macOS / Linux**  (not tested should work though)
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 main.py
```

---

## 🧭 How to Use

1. **Configure** in **Settings**:
   - Include paths (e.g., `Downloads`)
   - Optional destination roots ( where the folders will be created to sort, multiple can be set for multiple paths)
   - Exclude patterns + conflict policy
   - Add folders you want to exclude from scanning
2. **Scan** — Select “Scan / Preview” to analyze files.
   - Press Scan/Preview to Scan the files to move
   - Check the Subfolder BOX to scan folders in the DIR
   - Scan is very memory efficient, it seamlessly scans 80k+ files with less than 30mb ram consumption
4. **Review** — Watch planned actions in real time (*MOVE*, *SKIP*, *CONFLICT*).   
5. **Rules** — Map `.ext` → folder (e.g., `.jpg` → `Pictures`). Falls back to defaults.  
6. **Sort** — Use “Dry Run” to test; “Sort Now” to apply moves.  
7. **Undo** — “Undo ALL” restores from the last journaled batch.
   - May become unresponsive if the sum of files to undo is large, just wait for it to become responsive again

💡 *Pro tips:*  
- Double-click a row → open folder  
- Right-click a row → open/reveal/copy paths  

---

## 🧰 Building Native Executables (PyInstaller)

> Perform these in project root DIR

**Windows**
```bash
pip install pyinstaller
pyinstaller --noconsole --name FileFlow --add-data "src;src" main.py
```

**macOS**
```bash
pip install pyinstaller
pyinstaller --windowed --name FileFlow --add-data "src:src" main.py
```

**Linux**
```bash
pip install pyinstaller
pyinstaller --windowed --name fileflow --add-data "src:src" main.py
```

> ℹ **Tip:** Use `--onefile` for a single self-extracting binary (slower startup).

---

## ⚙️ Default Configuration

- **Include Paths:** `Downloads` folder by default  
- **Exclusions:** `.git`, `node_modules`, `__pycache__`, `.DS_Store`, etc.  
- **Conflict Policy:**
  - `skip` — Leave duplicates untouched
  - `suffix` — Append `(1)`, `(2)`, etc.
- **Categories:** Images, Docs, Videos, Audio, Archives, Code, Other

---

## 🔒 Safety & Undo

- **Duplicate detection:** Hash-based to avoid redundant copies  
- **Journal:** `.fileflow_journal.jsonl` in the first include path  
- **Undo:** “Undo ALL” reverses the last batch

---

## 📄 License

This project is licensed under the **MIT License** — see `LICENSE` for details.

---

<p align="center">✨ Made with care for tidy folders ✨</p>

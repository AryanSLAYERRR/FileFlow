<!--
   ███████╗██╗██╗     ███████╗███████╗██╗      ██████╗ ██╗    ██╗
   ██╔════╝██║██║     ██╔════╝██╔════╝██║     ██╔═══██╗██║    ██║
   █████╗  ██║██║     █████╗  ███████╗██║     ██║   ██║██║ █╗ ██║
   ██╔══╝  ██║██║     ██╔══╝  ╚════██║██║     ██║   ██║██║███╗██║
   ██║     ██║███████╗███████╗███████║███████╗╚██████╔╝╚███╔███╔╝
   ╚═╝     ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝ ╚═════╝  ╚══╝╚══╝
-->

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/GUI-Tkinter-4B8BBE?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Platforms-Windows%20%7C%20macOS%20%7C%20Linux-6aa84f?style=for-the-badge" />
</p>

<h1 align="center">FileFlow — Fast, Simple File Sorter</h1>
<p align="center">
Organize your downloads in seconds. Preview every move, resolve conflicts safely, and undo in one click — on Windows, macOS, and Linux.
</p>

---

## ✨ Highlights
- 🔎 Live Preview: stream of planned actions (MOVE • SKIP • CONFLICT) before touching files  
- 🗂️ Smart Organization: sort by extension into folders like Images, Docs, Videos, Audio, Archives, Code  
- 🧩 Custom Rules: map extensions (e.g., .pdf, .jpg) to destination folders in the built‑in Rules Editor  
- 🛡️ Safe Moves: identical files detected by hash; conflicts handled via “skip” or automatic “(1) (2) …” suffixes  
- 🧪 Dry Run: verify everything without moving a single file  
- ⏪ Undo: restore all moves from the last batch via a journal  
- 🧱 Filters: ignore clutter (node_modules, .git, __pycache__, hidden/system files as configured)  
- 🖥️ Cross‑Platform UX: open/reveal files using Explorer (Win), Finder (macOS), or xdg‑open (Linux)

---

## 📦 Project Structure
.
├─ main.py
└─ src/
   ├─ gui.py           # Tkinter interface: Dashboard, Preview, Settings, Rules
   ├─ preview.py       # Streaming preview generator (MOVE/SKIP/CONFLICT)
   ├─ apply_moves.py   # Apply moves, conflict resolution, journal & undo
   ├─ scanner.py       # Recursive scan with exclude globs & hidden filtering
   ├─ rules.py         # Rule resolution dispatcher
   ├─ config.py        # Defaults, validation, deep-merge, persistence
   ├─ types_map.py     # Extension → Category defaults
   ├─ worker.py        # Background workers for preview/apply
   └─ utils/
      ├─ hash_utils.py # Buffered file hashing
      └─ os_ops.py     # Open/reveal paths (Windows/macOS/Linux)
```

---

## 🚀 Run from Source
Requirements:
- Python 3.10+
- Tkinter available (Linux: `sudo apt-get install python3-tk`)
- Linux file opening: `sudo apt-get install xdg-utils`

Windows (PowerShell):
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip wheel setuptools
python main.py
```
macOS / Linux:

```
python3 -m venv .venv
source .venv/bin/activate
python3 main.py
```

---

## 🧭 Usage
1. Home → “Scan / Preview” to analyze files.  
2. Watch live actions (MOVE/SKIP/CONFLICT).  
3. Settings:
   - Add Include Paths (e.g., Downloads)
   - Optional Destination Root per include path
   - Exclude globs and conflict policy (skip/suffix)
4. Rules:
   - Map `.ext` → `Folder` (e.g., `.jpg` → `Pictures`)
   - Falls back to category defaults
5. Sort:
   - Use “Dry Run” to simulate
   - “Sort Now” to apply moves
6. Undo:
   - “Undo ALL” reverts last batch from the journal

Pro tips:
- Double‑click a row to open the file’s folder  
- Right‑click a row for open/reveal/copy paths

---

## 🧰 Build Native Executables (PyInstaller)
Build on each target OS for best compatibility.

Windows:
```
pip install pyinstaller
pyinstaller --noconsole --name FileFlow --add-data "src;src" main.py
# Output: dist\FileFlow\FileFlow.exe  (ship the entire dist\FileFlow folder)
```

macOS:
```
pip install pyinstaller
pyinstaller --windowed --name FileFlow --add-data "src:src" main.py
# Output: dist/FileFlow.app  (first run: Ctrl-click → Open)
```

Linux:
```
pip install pyinstaller
pyinstaller --windowed --name fileflow --add-data "src:src" main.py
# Output: dist/fileflow  (ship the entire folder)
```

Notes:
- Data separator: “;” on Windows, “:” on macOS/Linux  
- One‑file build (slower start, self‑extracts): add `--onefile` if desired

---

## ⚙️ Configuration Defaults
- Include Paths: user Downloads by default  
- Exclude Globs: common temp/dev clutter (`.git`, `node_modules`, `__pycache__`, `.DS_Store`, etc.)  
- Conflict Policy:
  - `skip`: do nothing if name exists (identical content SKIPped)
  - `suffix`: make “name (1).ext”, “name (2).ext”, …
- Categories: Images, Docs, Videos, Audio, Archives, Code, Other

---

## 🔒 Safety & Undo
- Hash‑based duplicate detection prevents redundant copies  
- Moves are journaled to `.fileflow_journal.jsonl` under the first include path  
- “Undo ALL” replays last batch in reverse to restore files

---

## 🧹 .gitignore (Recommended)
```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
*.so
*.pyd
*.dll

# Virtual environments
.venv/
venv/
env/
ENV/
.venv*/
.conda/
pip-wheel-metadata/

# Distribution / packaging
dist/
build/
*.egg-info/
*.egg
.eggs/
wheels/
*.whl
*.spec

# Unit test / coverage
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache/
pytest_cache/
nosetests.xml
coverage.xml
*.cover
*.py,cover

# Jupyter/IPython
.ipynb_checkpoints/
.profile_default/
ipython_config.py

# Logs and runtime
logs/
*.log

# App runtime artifacts
.fileflow_journal.jsonl
config.json

# OS files
.DS_Store
Thumbs.db
Desktop.ini

# Editor/IDE
.vscode/
.idea/
*.iml
*.code-workspace
.history/
*.swp
*.swo

# Static type checkers / linters
.mypy_cache/
.pyre/
.pytype/
ruff_cache/
.dmypy.json
.pyre_configuration.local

# Tool caches (poetry/pdm/etc.)
__pypackages__/
.pdm-python/
.masonry/
.poetry/
.poetry-cache/

# macOS debug symbols
*.dSYM/
```

---

## ❓ Troubleshooting
- PowerShell “`&&` not valid”: run commands separately or chain with `;`  
- “Activate.ps1 blocked”: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` then activate  
- Open/reveal not working:
  - macOS: `open` is standard
  - Linux: install `xdg-utils` (`xdg-open`)

---

## 📄 License
MIT


  Made with care for tidy folders ✨

```

[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/10088703/b43d829e-f085-44e6-ba90-49c013e09463/image.jpg?AWSAccessKeyId=ASIA2F3EMEYESWKX2CGT&Signature=RccdZwvQHc6kdnoDWln4WuepWBg%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEBQaCXVzLWVhc3QtMSJHMEUCIQCAHegQ7FSZEnGOqGyZC0yB5L9WH2K3Tf2drZEqXEOxOwIgYKNI99tSsuxQo6OCuIw%2FfQVo%2FCDpJ%2F1B3N8%2FiRF%2BE8Iq8QQIXRABGgw2OTk3NTMzMDk3MDUiDLmMaFxOHeJpqd%2F5%2FSrOBJTQkGd37G4bTpiU2OHqCWg0ghhbE2swlwosqgsVEIteKxV62610g8N7aOPVFVqQFo%2BAAL5uomiRusJBt6%2F5Ek1%2FTa6mn8w2%2Fs732Tu02zt2%2B0xPBUS9Rovxm0nS8ekAgzRZPzBfvjDFWtw37wcnfwpwWOk467ZINmG14J4t9B8lPTg%2BbbL50oRaIJ3BnKlUrdv1qY7NvUr223adhVncV5CjDvx6PJrNYEX72xp9G%2F5FOmv7QX9J7ts3i5UMWSr8C10yB3EOfEAFhvDuZ5FcJ%2FeUT9v5qt%2BGSsbgIwg%2B9vcQZDoVX%2FNQD0opRWZpU5ag%2BVLSZkwD6ITL5Tg4JT4laSdzryi8SRNA3Z%2FCbUUg7kIyqrwhGK%2B6LN1ePdtIXWBhzOmdfh7My5jjGcm1vpzG6vnjDeFKyBeZTrybyu2d1CIIdjcia0M0Pu6%2FV7K6b%2BFEQNjJ3x4R3l%2FDw5Djcp%2BBrvPBpGLHuChvLAkNsVTlqreFbAvMkPdDQyGrnr6z%2F9tEgXccQhbm70Z3It%2Bdv8XKQSMzj7YQFxi1m%2Fj7h40P45%2BGu13cWsOq05VE1EBA%2FgpLDR5tgZRjiTnlngVzSVOdFqUiosSTwJy2sNNPC%2Bhsa81GCTNPNGI8mpbU%2FGIBPyVJelnLZLco6mOikH4XoeAvJQ%2BcMsLYrLR03cd8Q0T5Jl4x6PduS8VAX2wh%2Btspxfu6r0%2FV1%2BxfnAcmfv40qFOyqByjZ%2FUfvY1xMfAB8RZXirYTcD3b%2FoEtMTN8c7nU4vO3YzFQFaFlS162iBg%2Bl%2BmFMOWx%2FMQGOpoB%2Fs%2BGSJ3WT4E5mJ0gOJ8dvxQg1sGk4yFTmJ%2FawVkO%2BlXOudJ0GW%2BI0ceGgf25CCnnZXhPyMOM25WxxNz1kJp9sRzu9K8%2BbirU52vcQI1tWhnOmx4z8pl3sb30VVL8qgZWFb88s1Bb4Mik1Ao%2BrB1Pg3TzYHJjCwwOw2kfr4S6TPGtYgOowoBKqIY1cwX0sLkFQJT55pg461K8Ww%3D%3D&Expires=1755258175

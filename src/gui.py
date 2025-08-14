import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.append(os.getcwd())

from src.config import load_config, get_default_config_path, save_config
from src.preview import build_preview
from src.apply_moves import apply_moves, undo_last, undo_all_stream
from src.utils.os_ops import open_file, reveal_in_file_manager


class FileFlowGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FileFlow - File Sorter")
        self.geometry("1000x640")

        self.cfg_path = get_default_config_path()
        self.cfg = load_config(self.cfg_path)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (HomeScreen, PreviewScreen, SettingsScreen, RulesScreen):
            page_name = F.__name__
            frame = F(parent=container, app=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomeScreen")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class HomeScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        tk.Label(self, text="FileFlow Dashboard", font=("Arial", 20)).pack(pady=20)

        tk.Button(self, text="Scan / Preview", width=20,
                  command=lambda: app.show_frame("PreviewScreen")).pack(pady=10)
        tk.Button(self, text="Settings", width=20,
                  command=lambda: app.show_frame("SettingsScreen")).pack(pady=10)
        tk.Button(self, text="Rules Editor", width=20,
                  command=lambda: app.show_frame("RulesScreen")).pack(pady=10)
        tk.Button(self, text="Quit", width=20, command=app.destroy).pack(pady=10)

class PreviewScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        toolbar = tk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.dry_var = tk.BooleanVar(value=False)
        self.subfolders_var = tk.BooleanVar(
            value=self.app.cfg.get("behavior", {}).get("sort_subfolders", False)
        )

        tk.Button(toolbar, text="Scan / Preview", command=self.run_preview).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="Sort Now", command=self.sort_now).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="Undo", command=self.undo_dialog).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Checkbutton(toolbar, text="Dry Run", variable=self.dry_var).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(toolbar, text="Include subfolders", variable=self.subfolders_var,
                       command=self.toggle_subfolders).pack(side=tk.LEFT, padx=5)

        tk.Button(toolbar, text="Back", command=lambda: app.show_frame("HomeScreen")).pack(side=tk.RIGHT, padx=5)

        columns = ("src", "action", "dest")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.title())
        self.tree.column("src", width=520, anchor="w")
        self.tree.column("action", width=100, anchor="center")
        self.tree.column("dest", width=520, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True)

        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self.on_open_file)

    def toggle_subfolders(self):
        self.app.cfg["behavior"]["sort_subfolders"] = bool(self.subfolders_var.get())
        save_config(self.app.cfg, self.app.cfg_path)

    def run_preview(self):
        self.tree.delete(*self.tree.get_children())
        self.toggle_subfolders()

        move_c = skip_c = conflict_c = total = 0
        for src, action, dest in build_preview(self.app.cfg):
            self.tree.insert("", tk.END, values=(src, action, dest))
            total += 1
            if action == "MOVE":
                move_c += 1
            elif action == "SKIP":
                skip_c += 1
            elif action == "CONFLICT":
                conflict_c += 1
        messagebox.showinfo("Preview Complete",
                            f"Found {total} items\nMOVE {move_c}, SKIP {skip_c}, CONFLICT {conflict_c}")

    def sort_now(self):
        self.toggle_subfolders()
        dry = self.dry_var.get()
        confirm = "Run as DRY RUN? No files will be moved." if dry else \
                  "Apply moves for real? This will move files."
        if not messagebox.askyesno("Confirm", confirm):
            return
        apply_moves(build_preview(self.app.cfg), self.app.cfg, dry_run=dry)
        messagebox.showinfo("Sort Complete", "Done. See console for log.")

    def undo_dialog(self):
        win = tk.Toplevel(self)
        win.title("Undo Options")
        tk.Button(win, text="Undo Last Batch", command=lambda: [undo_last(self.app.cfg),
                                                                win.destroy()]).pack(padx=10, pady=5)
        tk.Button(win, text="Undo ALL", command=lambda: [undo_all_stream(self.app.cfg),
                                                         win.destroy()]).pack(padx=10, pady=5)

    def on_open_file(self, event):
        sel = self.tree.selection()
        if sel:
            src = self.tree.item(sel[0], "values")[0]
            open_file(src)

class SettingsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        tk.Label(self, text="Settings", font=("Arial", 18)).pack(pady=10)

        tk.Label(self, text="Include Paths:").pack(anchor="w", padx=10)
        self.paths_entry = tk.Entry(self, width=80)
        self.paths_entry.insert(0, ", ".join(app.cfg.get("include_paths", [])))
        self.paths_entry.pack(padx=10, pady=5)

        tk.Label(self, text="Exclude Globs:").pack(anchor="w", padx=10)
        self.exclude_entry = tk.Entry(self, width=80)
        self.exclude_entry.insert(0, ", ".join(app.cfg.get("exclude_globs", [])))
        self.exclude_entry.pack(padx=10, pady=5)

        tk.Button(self, text="Save Settings", command=self.save_settings).pack(pady=10)
        tk.Button(self, text="Back", command=lambda: app.show_frame("HomeScreen")).pack()

    def save_settings(self):
        self.app.cfg["include_paths"] = [p.strip() for p in self.paths_entry.get().split(",") if p.strip()]
        self.app.cfg["exclude_globs"] = [p.strip() for p in self.exclude_entry.get().split(",") if p.strip()]
        save_config(self.app.cfg, self.app.cfg_path)
        messagebox.showinfo("Saved", "Settings saved.")

class RulesScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        tk.Label(self, text="Rules Editor (placeholder)", font=("Arial", 18)).pack(pady=20)
        tk.Label(self, text="Here you can add/edit rules.").pack(pady=10)
        tk.Button(self, text="Back", command=lambda: app.show_frame("HomeScreen")).pack(pady=10)


if __name__ == "__main__":
    app = FileFlowGUI()
    app.mainloop()

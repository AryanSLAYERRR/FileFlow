import os
import sys
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

sys.path.append(os.getcwd())

from src.config import load_config, get_default_config_path, save_config
from src.preview import build_preview
from src.apply_moves import apply_moves, undo_all_stream
from src.utils.os_ops import open_file
from src.worker import StreamWorker, ApplyWorker


class FileFlowGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FileFlow - File Sorter")
        self.geometry("1315x550")
        self.resizable(False, False)
        self.configure(bg="#1e1e1e")

        self.cfg_path = get_default_config_path()
        self.cfg = load_config(self.cfg_path)

        container = tk.Frame(self, bg="#1e1e1e")
        container.pack(fill="both", expand=True)

        # Initialize and create frames once
        self.frames = {}
        for F in (HomeScreen, PreviewScreen, SettingsScreen, RulesScreen):
            name = F.__name__
            frame = F(container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        geo = self.cfg.get("ui", {}).get("geometry")
        if geo:
            try:
                self.geometry(geo)
            except Exception:
                pass

        last = self.cfg.get("ui", {}).get("last_screen")
        if last and last in self.frames:
            self.show_frame(last)
        else:
            self.show_frame("HomeScreen")

    def show_frame(self, name):
        if not hasattr(self, "frames") or name not in self.frames:
            return
        self.frames[name].tkraise()
        try:
            self.cfg.setdefault("ui", {})
            self.cfg["ui"]["last_screen"] = name
        except Exception:
            pass

    def _on_close(self):
        # Remember UI state
        self.cfg.setdefault("ui", {})
        self.cfg["ui"]["geometry"] = self.geometry()
        save_config(self.cfg, self.cfg_path)
        self.destroy()

class HomeScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#1e1e1e")
        center_frame = tk.Frame(self, bg="#1e1e1e")
        center_frame.pack(expand=True, fill="both")

        tk.Label(
            center_frame,
            text="📂 FileFlow Dashboard",
            font=("Segoe UI", 20, "bold"),
            fg="white",
            bg="#1e1e1e",
        ).pack(pady=20)

        def styled_button(txt, cmd, bg_color):
            return tk.Button(
                center_frame,
                text=txt,
                command=cmd,
                font=("Segoe UI", 11),
                fg="white",
                bg=bg_color,
                relief="flat",
                width=25,
                pady=5,
                activebackground=bg_color,
                activeforeground="white",
            )

        styled_button("Scan / Preview", lambda: app.show_frame("PreviewScreen"), "#007acc").pack(pady=8)
        styled_button("Settings", lambda: app.show_frame("SettingsScreen"), "#007acc").pack(pady=8)
        styled_button("Rules Editor", lambda: app.show_frame("RulesScreen"), "#007acc").pack(pady=8)
        styled_button("Quit", app.destroy, "#d9534f").pack(pady=8)

class PreviewScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#1e1e1e")
        self.app = app
        self.all_rows = []
        self.compact_var = tk.BooleanVar(value=True)

        # Toolbar
        toolbar = tk.Frame(self, bg="#2d2d2d")
        toolbar.pack(side="top", fill="x")

        left_tools = tk.Frame(toolbar, bg="#2d2d2d")
        left_tools.pack(side="left", padx=5, pady=5)

        right_tools = tk.Frame(toolbar, bg="#2d2d2d")
        right_tools.pack(side="right", padx=5, pady=5)

        self.dry_var = tk.BooleanVar(value=False)
        self.subfolders_var = tk.BooleanVar(value=self.app.cfg.get("behavior", {}).get("sort_subfolders", False))

        def tb_btn(txt, cmd, bg):
            return tk.Button(
                left_tools,
                text=txt,
                command=cmd,
                font=("Segoe UI", 9),
                fg="white",
                bg=bg,
                relief="flat",
                padx=10,
                pady=3,
                activebackground=bg,
                activeforeground="white",
            )

        self.btn_scan = tb_btn("Scan / Preview", self.run_preview_async, "#007acc")
        self.btn_scan.pack(side="left", padx=3)
        self.btn_sort = tb_btn("Sort Now", self.sort_now_async, "#007acc")
        self.btn_sort.pack(side="left", padx=3)
        tb_btn("Undo", self.undo_dialog, "#6c757d").pack(side="left", padx=3)

        self.cancel_btn = tk.Button(
            left_tools,
            text="Cancel",
            command=self.cancel_current,
            font=("Segoe UI", 9),
            fg="white",
            bg="#d9534f",
            relief="flat",
            padx=10,
            pady=3,
            activebackground="#c9302c",
            activeforeground="white",
            state="disabled",
        )
        self.cancel_btn.pack(side="left", padx=3)

        tk.Checkbutton(
            left_tools,
            text="Dry Run",
            variable=self.dry_var,
            bg="#2d2d2d",
            fg="white",
            selectcolor="#2d2d2d",
            activebackground="#2d2d2d",
        ).pack(side="left", padx=5)

        tk.Checkbutton(
            left_tools,
            text="Include subfolders",
            variable=self.subfolders_var,
            command=self.toggle_subfolders,
            bg="#2d2d2d",
            fg="white",
            selectcolor="#2d2d2d",
        ).pack(side="left")


        tk.Checkbutton(
            left_tools,
            text="Compact Mode (lower memory, no filtering)",
            variable=self.compact_var,
            command=self.on_compact_toggle,
            bg="#2d2d2d",
            fg="white",
            selectcolor="#2d2d2d",
        ).pack(side="left")

        tk.Label(left_tools, text="Filter:", bg="#2d2d2d", fg="white").pack(side="left", padx=(15, 2))
        self.filter_var = tk.StringVar(value="All")
        self.filter_menu = ttk.Combobox(left_tools, textvariable=self.filter_var, values=["All", "MOVE", "SKIP", "CONFLICT"], width=10, state="disabled")
        self.filter_menu.pack(side="left")
        self.filter_menu.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        # Right-side tools
        tk.Button(
            right_tools,
            text="Open Destination Root",
            command=lambda: open_file(self.app.cfg.get("destination_roots", [None])[0] or self.app.cfg.get("include_paths", [""])),
            font=("Segoe UI", 9),
            fg="white",
            bg="#444",
            relief="flat",
            padx=10,
            pady=3,
            activebackground="#555",
            activeforeground="white",
        ).pack(side="left", padx=5)

        tk.Button(
            right_tools,
            text="Clear Log",
            command=self.clear_log,
            font=("Segoe UI", 9),
            fg="white",
            bg="#444",
            relief="flat",
            padx=10,
            pady=3,
            activebackground="#555",
            activeforeground="white",
        ).pack(side="left", padx=5)

        tk.Button(
            right_tools,
            text="⟵ Back",
            command=lambda: app.show_frame("HomeScreen"),
            font=("Segoe UI", 9),
            fg="white",
            bg="#444",
            relief="flat",
            padx=10,
            pady=3,
            activebackground="#555",
            activeforeground="white",
        ).pack(side="left")

        # Table and log area
        main_area = tk.Frame(self, bg="#1e1e1e")
        main_area.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#252526", fieldbackground="#252526", foreground="white", rowheight=24)
        style.configure("Treeview.Heading", background="#007acc", foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#005999")])

        columns = ("src", "action", "dest")
        self.tree = ttk.Treeview(main_area, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.title())
        self.tree.column("src", width=600, anchor="w")
        self.tree.column("action", width=100, anchor="center")
        self.tree.column("dest", width=600, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(main_area, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        self.log_text = tk.Text(main_area, bg="black", fg="lime", insertbackground="white", height=10)
        self.log_text.grid(row=1, column=0, columnspan=2, sticky="nsew")

        main_area.rowconfigure(0, weight=3)
        main_area.rowconfigure(1, weight=1)
        main_area.columnconfigure(0, weight=1)

        self.tree.tag_configure("MOVE", background="#2e4e2e")
        self.tree.tag_configure("SKIP", background="#333333")
        self.tree.tag_configure("CONFLICT", background="#5a2d2d")

        # Status bar
        status_bar = tk.Frame(self, bg="#2d2d2d")
        status_bar.pack(side="bottom", fill="x")
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(status_bar, textvariable=self.status_var, bg="#2d2d2d", fg="white")
        self.status_label.pack(side="left", padx=8, pady=2)
        # Display cap (limit number of rows shown to reduce memory)
        self.display_row_cap = self.app.cfg.get("ui", {}).get("preview_window_limit", 1000)
        # Background worker state
        self._q = None
        self._cancel = None
        self._poll_id = None
        self._running_mode = None
        self._apply_worker = None

        self.bind_all("<F5>", lambda e: self.run_preview_async())
        self.bind_all("<Control-l>", lambda e: self.clear_log())
        self.bind_all("<Control-L>", lambda e: self.clear_log())
        self.bind_all("<Escape>", lambda e: self.cancel_current())
        self.tree.bind("<Double-1>", self._on_tree_double_click)
        self.tree.bind("<Button-3>", self._on_tree_right_click)
        self._make_context_menu()

    def set_status(self, msg: str):
        self.status_var.set(msg)

    def clear_log(self):
        self.log_text.delete("1.0", tk.END)
        self.log_text.see("1.0")

    def on_compact_toggle(self):
        self.filter_menu.configure(state="readonly" if not self.compact_var.get() else "disabled")
        if self.compact_var.get():
            self.log("[UI] Compact Mode ON: filtering disabled to save memory")
        else:
            self.log("[UI] Compact Mode OFF: filtering enabled (higher memory)")

    def log(self, msg):
        ts = datetime.now().strftime("[%H:%M:%S]")
        self.log_text.insert(tk.END, f"{ts} {msg}\n")
        max_lines = 1000
        current = int(float(self.log_text.index('end-1c').split('.')[0]))
        if current > max_lines:
            self.log_text.delete('1.0', f'{current - max_lines}.0')
        self.log_text.see(tk.END)

    def toggle_subfolders(self):
        self.app.cfg.setdefault("behavior", {})
        self.app.cfg["behavior"]["sort_subfolders"] = bool(self.subfolders_var.get())
        save_config(self.app.cfg, self.app.cfg_path)

    def _set_running(self, mode: str | None):
        self._running_mode = mode
        is_running = mode is not None
        self.cancel_btn.configure(state=("normal" if is_running else "disabled"))
        if hasattr(self, "btn_scan"):
            self.btn_scan.configure(state=("disabled" if is_running else "normal"))
        if hasattr(self, "btn_sort"):
            self.btn_sort.configure(state=("disabled" if is_running else "normal"))
        if is_running:
            self.log(f"[UI] {mode.capitalize()} started...")
        else:
            self.log(f"[UI] {mode.capitalize()} finished" if mode else "[UI] Ready")

    def cancel_current(self):
        if self._running_mode == "apply":
            if not messagebox.askyesno("Cancel Apply", "Cancel now? Completed moves will remain applied."):
                return
        if self._cancel and not self._cancel.is_set():
            self._cancel.set()
            self.set_status("Cancelling…")
            self.log("[UI] Cancel requested...")

    def _make_context_menu(self):
        self._ctx_menu = tk.Menu(self, tearoff=0)
        self._ctx_menu.add_command(label="Open Destination Folder", command=self._ctx_open_dest_folder)
        self._ctx_menu.add_command(label="Open Source File", command=self._ctx_open_source_file)
        self._ctx_menu.add_separator()
        self._ctx_menu.add_command(label="Copy Selected Paths", command=self._ctx_copy_paths)

    def _on_tree_right_click(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self._ctx_menu.tk_popup(event.x_root, event.y_root)

    def _ctx_open_source_file(self):
        sel = self.tree.selection()
        if not sel:
            return
        src, _, _ = self.tree.item(sel, "values")
        open_file(src)

    def _ctx_copy_paths(self):
        sels = self.tree.selection()
        if not sels:
            return
        lines = []
        for iid in sels:
            src, action, dest = self.tree.item(iid, "values")
            lines.append(f"{action}\t{src}\t{dest}")
        text = "\n".join(lines)
        self.clipboard_clear()
        self.clipboard_append(text)
        self.log("[UI] Copied selected paths to clipboard")

    def _ctx_open_dest_folder(self):
        sel = self.tree.selection()
        if not sel:
            return
        _, _, dest = self.tree.item(sel, "values")
        open_file(os.path.dirname(dest))

    def _on_tree_double_click(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        src, _, _ = self.tree.item(iid, "values")
        open_file(os.path.dirname(src))

    def run_preview_async(self):
        if self._running_mode:
            messagebox.showinfo("Busy", "An operation is already running.")
            return

        inc = self.app.cfg.get("include_paths", [])
        if not inc:
            messagebox.showwarning("No include paths", "Add at least one Include Path in Settings.")
            return
        missing = [p for p in inc if not os.path.exists(p)]
        if missing:
            messagebox.showwarning("Missing paths", "These paths do not exist:\n" + "\n".join(missing))
            return

        # Reset UI
        self.tree.delete(*self.tree.get_children())
        self.clear_log()
        self.all_rows.clear()
        self.toggle_subfolders()

        # Counters
        self._move_c = self._skip_c = self._conflict_c = self._total = 0

        # Setup streaming worker
        self._q = queue.Queue(maxsize=500)
        self._cancel = threading.Event()

        def gen():
            return build_preview(self.app.cfg)

        worker = StreamWorker(target=gen, out_q=self._q, cancel_event=self._cancel)
        worker.start()

        self._set_running("preview")
        self.set_status("Scanning… 0 items")
        self._poll_queue_preview()

    def _poll_queue_preview(self):
        processed = 0
        try:
            while processed < 200:
                item = self._q.get_nowait()
                if item is None:
                    self._finish_preview()
                    return
                if isinstance(item, tuple) and len(item) == 3:
                    src, action, dest = item
                    if not self.compact_var.get():
                        self.all_rows.append((src, action, dest))
                    self.tree.insert("", tk.END, values=(src, action, dest), tags=(action,))
                    # Enforce display cap
                    if self.display_row_cap and len(self.tree.get_children()) > self.display_row_cap:
                        to_remove = len(self.tree.get_children()) - self.display_row_cap
                        for iid in self.tree.get_children()[:to_remove]:
                            self.tree.delete(iid)
                    self.log(f"{action}: {src} -> {dest}")
                    self._total += 1
                    if action == "MOVE":
                        self._move_c += 1
                    elif action == "SKIP":
                        self._skip_c += 1
                    elif action == "CONFLICT":
                        self._conflict_c += 1
                    self.set_status(f"Scanning… {self._total} items (MOVE {self._move_c} | SKIP {self._skip_c} | CONFLICT {self._conflict_c})")
                elif isinstance(item, tuple) and item and item[0] == "__ERROR__":
                    self.log(f"[ERROR] {item[1]}")
                processed += 1
        except queue.Empty:
            pass
        self._poll_id = self.after(50, self._poll_queue_preview)

    def _finish_preview(self):
        if self._poll_id:
            try:
                self.after_cancel(self._poll_id)
            except Exception:
                pass
            self._poll_id = None
        self.on_compact_toggle()
        messagebox.showinfo(
            "Preview Complete",
            f"Found {self._total} items\nMOVE {self._move_c}, SKIP {self._skip_c}, CONFLICT {self._conflict_c}",
        )
        self.set_status(f"Preview complete: {self._total} items (MOVE {self._move_c} | SKIP {self._skip_c} | CONFLICT {self._conflict_c})")
        self._set_running(None)
        self.cancel_btn.configure(state="disabled")
        self._q = None
        self._cancel = None

    def apply_filter(self):
        if self.compact_var.get():
            return
        self.tree.delete(*self.tree.get_children())
        selected = self.filter_var.get()
        for src, action, dest in self.all_rows:
            if selected == "All" or action == selected:
                self.tree.insert("", tk.END, values=(src, action, dest), tags=(action,))

    def sort_now_async(self):
        if self._running_mode:
            messagebox.showinfo("Busy", "An operation is already running.")
            return

        self.toggle_subfolders()
        dry = self.dry_var.get()
        confirm = "Run as DRY RUN? No files will be moved." if dry else "Apply moves for real?"
        if not messagebox.askyesno("Confirm", confirm):
            return

        self.log("=== SORT START ===")
        policy = self.app.cfg.get("behavior", {}).get("conflict_policy", "suffix").lower()
        self.set_status(f"Applying… policy={policy}")

        self._cancel = threading.Event()

        def iter_factory():
            return build_preview(self.app.cfg)

        def apply_wrapper(stream):
            apply_moves(stream, self.app.cfg, dry_run=dry)

        def progress(msg: str):
            self.log(msg)

        worker = ApplyWorker(preview_iter_fn=iter_factory, apply_fn=apply_wrapper, cancel_event=self._cancel, progress_cb=progress)
        self._apply_worker = worker
        worker.start()

        self._set_running("apply")
        self._poll_apply_done()

    def _poll_apply_done(self):
        if self._apply_worker and self._apply_worker.done_event.is_set():
            self.log("=== SORT COMPLETE ===")
            messagebox.showinfo("Sort Complete", "Done.")
            self.set_status("Apply complete")
            self._set_running(None)
            self.cancel_btn.configure(state="disabled")
            self._apply_worker = None
            self._cancel = None
            return
        self.after(150, self._poll_apply_done)

    def undo_dialog(self):
        win = tk.Toplevel(self)
        win.title("Undo Options")
        tk.Button(win, text="Undo ALL", command=lambda: [undo_all_stream(self.app.cfg), self.log("Undo ALL batches"), win.destroy()]).pack(padx=10, pady=5)

class SettingsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#1e1e1e")
        self.app = app

        toolbar = tk.Frame(self, bg="#2d2d2d")
        toolbar.pack(side="top", fill="x")
        tk.Button(toolbar, text="⟵ Back", command=lambda: app.show_frame("HomeScreen"), font=("Segoe UI", 9), fg="white", bg="#444").pack(side="right", padx=5, pady=3)

        tk.Label(self, text="Settings", font=("Segoe UI", 18), fg="white", bg="#1e1e1e").pack(pady=10)

        # Include paths
        tk.Label(self, text="Include Paths:", fg="white", bg="#1e1e1e").pack(anchor="w", padx=10)
        self.paths_list = tk.Listbox(self, height=5, width=80, bg="#252526", fg="white")
        for p in app.cfg.get("include_paths", []):
            self.paths_list.insert(tk.END, p)
        self.paths_list.pack(padx=10, pady=5)
        tk.Button(self, text="Add Path", command=self.add_path, bg="#007acc", fg="white").pack(pady=2)
        tk.Button(self, text="Remove Selected", command=self.remove_path, bg="#6c757d", fg="white").pack(pady=2)

        # Destination per selected include path
        self.set_dest_btn = tk.Button(self, text="Set Destination for Selected", command=self.set_destination_for_selected, bg="#007acc", fg="white")
        self.set_dest_btn.pack(pady=2)

        # Exclude globs
        tk.Label(self, text="Exclude Globs:", fg="white", bg="#1e1e1e").pack(anchor="w", padx=10, pady=(10, 0))
        self.exclude_entry = tk.Entry(self, width=80, bg="#252526", fg="white", insertbackground="white")
        self.exclude_entry.insert(0, ", ".join(app.cfg.get("exclude_globs", [])))
        self.exclude_entry.pack(padx=10, pady=5)

        # Hidden/system toggles
        ui_cfg = app.cfg.get("ui", {})
        self.show_hidden_var = tk.BooleanVar(value=ui_cfg.get("show_hidden_files", False))
        self.show_system_var = tk.BooleanVar(value=ui_cfg.get("show_system_files", False))

        tk.Checkbutton(self, text="Show hidden files", variable=self.show_hidden_var, bg="#1e1e1e", fg="white", selectcolor="#1e1e1e").pack(anchor="w", padx=10, pady=(10, 0))
        tk.Checkbutton(self, text="Show system files", variable=self.show_system_var, bg="#1e1e1e", fg="white", selectcolor="#1e1e1e").pack(anchor="w", padx=10)

        # Conflict policy
        tk.Label(self, text="Conflict Policy:", fg="white", bg="#1e1e1e").pack(anchor="w", padx=10, pady=(10, 0))
        self.conflict_var = tk.StringVar(value=app.cfg.get("behavior", {}).get("conflict_policy", "suffix"))
        self.conflict_menu = ttk.Combobox(self, textvariable=self.conflict_var, values=["skip", "suffix"], width=12, state="readonly")
        self.conflict_menu.pack(anchor="w", padx=10, pady=(0, 10))

        tk.Button(self, text="Save Settings", command=self.save_settings, bg="#28a745", fg="white").pack(pady=10)

    def add_path(self):
        folder = filedialog.askdirectory()
        if folder:
            self.paths_list.insert(tk.END, folder)

    def remove_path(self):
        for sel in reversed(self.paths_list.curselection()):
            self.paths_list.delete(sel)

    def set_destination_for_selected(self):
        sel = self.paths_list.curselection()
        if not sel:
            messagebox.showwarning("No selection", "Select an include path first.")
            return
        idx = sel[0]
        dest = filedialog.askdirectory(title="Choose destination root for this include path")
        if not dest:
            return

        include_paths = list(self.paths_list.get(0, tk.END))
        dest_roots = list(self.app.cfg.get("destination_roots", []))

        if len(dest_roots) < len(include_paths):
            dest_roots += [""] * (len(include_paths) - len(dest_roots))
        elif len(dest_roots) > len(include_paths):
            dest_roots = dest_roots[:len(include_paths)]

        dest_roots[idx] = dest
        self.app.cfg["destination_roots"] = dest_roots
        save_config(self.app.cfg, self.app.cfg_path)
        messagebox.showinfo("Saved", f"Destination set for:\n{include_paths[idx]}\n→ {dest}")

    def save_settings(self):
        include_paths = list(self.paths_list.get(0, tk.END))
        self.app.cfg["include_paths"] = include_paths

        dest_roots = list(self.app.cfg.get("destination_roots", []))
        if len(dest_roots) < len(include_paths):
            dest_roots += [""] * (len(include_paths) - len(dest_roots))
        elif len(dest_roots) > len(include_paths):
            dest_roots = dest_roots[:len(include_paths)]
        self.app.cfg["destination_roots"] = dest_roots

        self.app.cfg["exclude_globs"] = [p.strip() for p in self.exclude_entry.get().split(",") if p.strip()]
        self.app.cfg.setdefault("ui", {})
        self.app.cfg["ui"]["show_hidden_files"] = bool(self.show_hidden_var.get())
        self.app.cfg["ui"]["show_system_files"] = bool(self.show_system_var.get())
        self.app.cfg.setdefault("behavior", {})
        self.app.cfg["behavior"]["conflict_policy"] = self.conflict_var.get().lower()

        save_config(self.app.cfg, self.app.cfg_path)
        messagebox.showinfo("Saved", "Settings saved.")


class RulesScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#1e1e1e")
        self.app = app

        toolbar = tk.Frame(self, bg="#2d2d2d")
        toolbar.pack(side="top", fill="x")

        tk.Button(
            toolbar,
            text="⟵ Back",
            command=lambda: app.show_frame("HomeScreen"),
            font=("Segoe UI", 9),
            fg="white",
            bg="#444",
            relief="flat",
            activebackground="#555",
            activeforeground="white",
        ).pack(side="right", padx=5, pady=3)

        tk.Label(self, text="Rules Editor", font=("Segoe UI", 18, "bold"), fg="white", bg="#1e1e1e").pack(pady=(5, 5))

        btn_frame = tk.Frame(self, bg="#1e1e1e")
        btn_frame.pack(side="top", fill="x", padx=5, pady=5)
        tk.Button(btn_frame, text="Add Rule", command=self.add_rule, bg="#007acc", fg="white", font=("Segoe UI", 9), relief="flat").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Edit Rule", command=self.edit_rule, bg="#007acc", fg="white", font=("Segoe UI", 9), relief="flat").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Rule", command=self.delete_rule, bg="#d9534f", fg="white", font=("Segoe UI", 9), relief="flat").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear Selection", command=lambda: self.tree.selection_remove(self.tree.selection()), bg="#6c757d", fg="white", font=("Segoe UI", 9), relief="flat").pack(side=tk.LEFT, padx=5)

        tv_frame = tk.Frame(self, bg="#1e1e1e")
        tv_frame.pack(fill="both", expand=False, padx=10, pady=(0, 4))

        columns = ("ext", "folder")
        self.tree = ttk.Treeview(tv_frame, columns=columns, show="headings", height=12)
        self.tree.heading("ext", text="Extension")
        self.tree.heading("folder", text="Destination Folder")
        self.tree.column("ext", width=160, anchor="center")
        self.tree.column("folder", width=420, anchor="w")
        self.tree.bind("<Button-1>", self._on_tree_click)
        self.tree.pack(side="left", fill="both", expand=True)

        yscroll = ttk.Scrollbar(tv_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.pack(side="right", fill="y")

        self.load_rules()

    def _on_tree_click(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            self.tree.selection_remove(self.tree.selection())
            return
        cur_sel = self.tree.selection()
        if iid in cur_sel:
            self.tree.selection_remove(iid)
            return "break"

    def load_rules(self):
        self.tree.delete(*self.tree.get_children())
        for ext, folder in self.app.cfg.get("rules", {}).items():
            self.tree.insert("", tk.END, values=(ext, folder))

    def save_rules(self):
        self.app.cfg["rules"] = {self.tree.item(i, "values")[0]: self.tree.item(i, "values")[1] for i in self.tree.get_children()}
        save_config(self.app.cfg, self.app.cfg_path)
        self.load_rules()

    def add_rule(self):
        self.rule_dialog("Add Rule")

    def edit_rule(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Select a rule to edit")
            return
        ext, folder = self.tree.item(sel, "values")
        self.rule_dialog("Edit Rule", sel, ext, folder)

    def delete_rule(self):
        for iid in self.tree.selection():
            self.tree.delete(iid)
        self.save_rules()

    def rule_dialog(self, title, item_id=None, ext_val="", folder_val=""):
        win = tk.Toplevel(self)
        win.title(title)
        win.resizable(False, False)

        tk.Label(win, text="Extension (e.g., jpg — dot optional):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ext_entry = tk.Entry(win)
        ext_entry.insert(0, ext_val)
        ext_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(win, text="Destination Folder Name:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        folder_entry = tk.Entry(win)
        folder_entry.insert(0, folder_val)
        folder_entry.grid(row=1, column=1, padx=5, pady=5)

        def save_and_close():
            ext = ext_entry.get().strip().lower()
            folder = folder_entry.get().strip()
            if not ext or not folder:
                messagebox.showerror("Error", "Both fields are required")
                return
            if not ext.startswith("."):
                ext = "." + ext
            if item_id:
                self.tree.item(item_id, values=(ext, folder))
            else:
                self.tree.insert("", tk.END, values=(ext, folder))
            self.save_rules()
            win.destroy()

        tk.Button(win, text="Save", command=save_and_close).grid(row=2, column=0, columnspan=2, pady=8)
        win.grab_set()


if __name__ == "__main__":
    app = FileFlowGUI()
    app.mainloop()

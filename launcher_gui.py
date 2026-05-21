import threading
import subprocess
import sys
import time
from pathlib import Path
import re
import tkinter as tk
from tkinter import ttk, messagebox


def get_bot_files(workspace_dir: Path):
    bots = []
    pattern = re.compile(r"bot(\d+)\.py$")
    for p in workspace_dir.glob("bot*.py"):
        m = pattern.search(p.name)
        if m:
            bots.append((int(m.group(1)), p.name))
    bots.sort()
    return [name for _, name in bots]


class BotLauncher(tk.Tk):
    def __init__(self, workspace_dir: Path):
        super().__init__()
        self.title("Bot Launcher")
        self.workspace_dir = workspace_dir
        self.bot_files = get_bot_files(workspace_dir)
        self.vars = []
        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self, padding=10)
        frm.grid(sticky="nsew")

        lbl = ttk.Label(frm, text="Select bots to run:")
        lbl.grid(row=0, column=0, sticky="w")

        canvas = tk.Canvas(frm)
        canvas.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(frm, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner, anchor="nw")

        for i, bot in enumerate(self.bot_files, start=1):
            var = tk.IntVar(value=0)
            cb = ttk.Checkbutton(inner, text=bot, variable=var)
            cb.grid(row=i - 1, column=0, sticky="w")
            self.vars.append((var, bot))

        inner.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=2, column=0, pady=(8, 0), sticky="ew")

        run_sel = ttk.Button(btn_frame, text="Run Selected", command=self.run_selected)
        run_sel.grid(row=0, column=0, padx=4)

        run_all = ttk.Button(btn_frame, text="Run All", command=self.run_all)
        run_all.grid(row=0, column=1, padx=4)

        stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_run)
        stop_btn.grid(row=0, column=2, padx=4)

        ttk.Button(btn_frame, text="Exit", command=self.destroy).grid(row=0, column=3, padx=4)

        self.log = tk.Text(frm, height=12, width=70, state="disabled")
        self.log.grid(row=3, column=0, columnspan=2, pady=(8, 0))

        self.running = False
        self._stop_requested = False

    def append_log(self, msg: str):
        def _append():
            self.log.configure(state="normal")
            self.log.insert("end", msg + "\n")
            self.log.see("end")
            self.log.configure(state="disabled")

        self.log.after(0, _append)

    def run_selected(self):
        selected = [bot for var, bot in self.vars if var.get()]
        if not selected:
            messagebox.showinfo("No bots", "Please select at least one bot to run.")
            return
        self._start_runner(selected)

    def run_all(self):
        self._start_runner(self.bot_files)

    def stop_run(self):
        if self.running:
            self._stop_requested = True
            self.append_log("Stop requested — will stop after current bot finishes.")

    def _start_runner(self, selected_list):
        if self.running:
            messagebox.showinfo("Already running", "A run is already in progress.")
            return
        self._stop_requested = False
        thread = threading.Thread(target=self._runner_thread, args=(selected_list,), daemon=True)
        thread.start()

    def _runner_thread(self, selected_list):
        self.running = True
        workspace = self.workspace_dir
        for index, bot_file in enumerate(selected_list, start=1):
            if self._stop_requested:
                self.append_log("Run stopped by user.")
                break

            bot_path = workspace / bot_file
            self.append_log(f"=== Starting {bot_file} ({index}/{len(selected_list)}) ===")

            if not bot_path.exists():
                self.append_log(f"ERROR: {bot_file} not found at {bot_path}")
                break

            try:
                result = subprocess.run([sys.executable, str(bot_path)], cwd=str(workspace))
                self.append_log(f"{bot_file} finished with exit code {result.returncode}.")
                if result.returncode != 0:
                    self.append_log(f"Stopping sequence because {bot_file} returned non-zero exit code.")
                    break
            except Exception as e:
                self.append_log(f"Exception running {bot_file}: {e}")
                break

            if index < len(selected_list) and not self._stop_requested:
                self.append_log("Waiting 10 seconds before next bot...")
                for _ in range(10):
                    if self._stop_requested:
                        break
                    time.sleep(1)

        self.append_log("All selected bot runs completed or stopped.")
        self.running = False


if __name__ == "__main__":
    workspace = Path(__file__).resolve().parent
    app = BotLauncher(workspace)
    app.mainloop()

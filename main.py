# run logic
# bot1.py start -> bot1.py running -> bot1.py end
# wait 10 seconds ... (loops forever until stopped)
# Supports Normal Battle (sequential / random) and Rank Battle (sequential / random)

import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import time
import os
import threading
import random

# ─── Script Lists ─────────────────────────────────────────────────────────────
NORMAL_BOT_SCRIPTS = [
    "Normal Battle/bot1.py",  "Normal Battle/bot2.py",  "Normal Battle/bot3.py",
    "Normal Battle/bot4.py",  "Normal Battle/bot5.py",  "Normal Battle/bot6.py",
    "Normal Battle/bot7.py",  "Normal Battle/bot8.py",  "Normal Battle/bot9.py",
    "Normal Battle/bot10.py", "Normal Battle/bot11.py", "Normal Battle/bot12.py",
    "Normal Battle/bot13.py", 
]

RANK_BOT_SCRIPTS = [
    "Rank Battle/rankBot1.py",  "Rank Battle/rankBot2.py",  "Rank Battle/rankBot3.py",
    "Rank Battle/rankBot4.py",  "Rank Battle/rankBot5.py",  "Rank Battle/rankBot6.py",
    "Rank Battle/rankBot7.py",  "Rank Battle/rankBot8.py",  "Rank Battle/rankBot9.py",
    "Rank Battle/rankBot10.py", "Rank Battle/rankBot11.py", "Rank Battle/rankBot12.py",
]

WAIT_TIME = 10   # seconds between bots

# ─── Modes ────────────────────────────────────────────────────────────────────
MODE_NORMAL_SEQ    = "normal_seq"
MODE_NORMAL_RANDOM = "normal_random"
MODE_RANK_SEQ      = "rank_seq"
MODE_RANK_RANDOM   = "rank_random"


class BotRunnerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Clash of Clans  –  Multi-Bot Automation Controller")
        self.root.geometry("700x540")
        self.root.minsize(560, 440)

        # State
        self.is_running       = False
        self.mode             = None
        self.automation_thread = None

        self.setup_ui()

    # ── UI ──────────────────────────────────────────────────────────────────
    def setup_ui(self):
        # ── Row 1: Normal Battle buttons ──────────────────────────────────
        normal_frame = ttk.LabelFrame(self.root, text=" ⚔  Normal Battle ", padding="8")
        normal_frame.pack(fill=tk.X, padx=10, pady=(10, 2))

        self.normal_seq_btn = ttk.Button(
            normal_frame,
            text="▶  Normal Battle Respectively",
            command=lambda: self._start(MODE_NORMAL_SEQ),
        )
        self.normal_seq_btn.pack(side=tk.LEFT, padx=5)

        self.normal_rnd_btn = ttk.Button(
            normal_frame,
            text="🔀  Random Normal Battle",
            command=lambda: self._start(MODE_NORMAL_RANDOM),
        )
        self.normal_rnd_btn.pack(side=tk.LEFT, padx=5)

        # ── Row 2: Rank Battle buttons ────────────────────────────────────
        rank_frame = ttk.LabelFrame(self.root, text=" 🏆  Rank Battle ", padding="8")
        rank_frame.pack(fill=tk.X, padx=10, pady=(2, 4))

        self.rank_seq_btn = ttk.Button(
            rank_frame,
            text="▶  Rank Battle Respectively",
            command=lambda: self._start(MODE_RANK_SEQ),
        )
        self.rank_seq_btn.pack(side=tk.LEFT, padx=5)

        self.rank_rnd_btn = ttk.Button(
            rank_frame,
            text="🔀  Random Rank Battle",
            command=lambda: self._start(MODE_RANK_RANDOM),
        )
        self.rank_rnd_btn.pack(side=tk.LEFT, padx=5)

        # ── Stop + Status row ─────────────────────────────────────────────
        control_frame = ttk.Frame(self.root, padding="6")
        control_frame.pack(fill=tk.X, padx=10)

        self.stop_btn = ttk.Button(
            control_frame, text="⏹  Stop Loop",
            command=self.stop_automation, state=tk.DISABLED,
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(
            control_frame, text="Status: Idle", font=("Helvetica", 10, "bold")
        )
        self.status_label.pack(side=tk.RIGHT, padx=10)

        # ── Current Activity ──────────────────────────────────────────────
        progress_frame = ttk.LabelFrame(self.root, text=" Current Activity ", padding="8")
        progress_frame.pack(fill=tk.X, padx=10, pady=4)

        self.current_bot_label = ttk.Label(
            progress_frame, text="Active Bot: None", font=("Helvetica", 10)
        )
        self.current_bot_label.pack(anchor=tk.W)

        self.loop_label = ttk.Label(
            progress_frame, text="Loop Count: 0", font=("Helvetica", 9)
        )
        self.loop_label.pack(anchor=tk.W, pady=(4, 0))

        # ── Live Console ──────────────────────────────────────────────────
        log_frame = ttk.LabelFrame(self.root, text=" Live Console Logs ", padding="8")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self.log_area = scrolledtext.ScrolledText(
            log_frame, wrap=tk.WORD,
            font=("Consolas", 9), bg="#1e1e1e", fg="#ffffff",
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.insert(
            tk.END,
            "System ready.\n"
            "  • Normal Battle Respectively  – runs bot1 → bot12 in order, loops forever\n"
            "  • Random Normal Battle         – picks a random Normal bot each turn\n"
            "  • Rank Battle Respectively     – runs rankBot1 → rankBot12 in order, loops forever\n"
            "  • Random Rank Battle           – picks a random Rank bot each turn\n\n"
            "Click any Start button to begin.\n",
        )
        self.log_area.configure(state=tk.DISABLED)

    # ── Helpers ─────────────────────────────────────────────────────────────
    def _all_start_buttons(self):
        return [self.normal_seq_btn, self.normal_rnd_btn,
                self.rank_seq_btn,   self.rank_rnd_btn]

    def log(self, message):
        """Thread-safe log append."""
        self.log_area.configure(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state=tk.DISABLED)

    def update_status(self, text, bot_text=None, loop_text=None):
        self.status_label.config(text=f"Status: {text}")
        if bot_text  is not None:
            self.current_bot_label.config(text=f"Active Bot: {bot_text}")
        if loop_text is not None:
            self.loop_label.config(text=f"Loop Count: {loop_text}")

    # ── Start / Stop ────────────────────────────────────────────────────────
    def _start(self, mode: str):
        if self.is_running:
            return
        self.is_running = True
        self.mode = mode

        for btn in self._all_start_buttons():
            btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        self.automation_thread = threading.Thread(
            target=self.run_loop_sequence, daemon=True
        )
        self.automation_thread.start()

    def stop_automation(self):
        if self.is_running:
            self.is_running = False
            self.log("\n[!] Stop requested. Finishing current step then shutting down...")
            self.update_status("Stopping...")
            self.stop_btn.config(state=tk.DISABLED)

    # ── Main Loop ───────────────────────────────────────────────────────────
    def run_loop_sequence(self):
        # Decide which script pool to use
        if self.mode in (MODE_NORMAL_SEQ, MODE_NORMAL_RANDOM):
            pool  = NORMAL_BOT_SCRIPTS
            label = "Normal Battle"
        else:
            pool  = RANK_BOT_SCRIPTS
            label = "Rank Battle"

        is_random = self.mode in (MODE_NORMAL_RANDOM, MODE_RANK_RANDOM)

        loop_count = 1

        while self.is_running:
            self.log(
                f"\n{'='*45}\n"
                f"  {label}  –  LOOP #{loop_count}  "
                f"({'Random' if is_random else 'Sequential'})\n"
                f"{'='*45}"
            )
            self.update_status(f"Running – {label}", loop_text=str(loop_count))

            # Build execution order for this iteration
            if is_random:
                sequence = [random.choice(pool) for _ in range(len(pool))]
            else:
                sequence = list(pool)

            for bot in sequence:
                if not self.is_running:
                    break

                if not os.path.exists(bot):
                    self.log(f"[Warning] '{bot}' not found – skipping.")
                    continue

                self.update_status("Bot Active", bot_text=bot)
                self.log(f"\n[➔] {bot}  start")
                self.log(f"[⚙] {bot}  running...")

                result = subprocess.run(["python", bot])

                self.log(f"[✓] {bot}  ended  (exit code: {result.returncode})")

                if not self.is_running:
                    break

                # Countdown cooldown
                self.update_status("Cooldown", bot_text=f"Waiting after {bot}")
                for i in range(WAIT_TIME, 0, -1):
                    if not self.is_running:
                        break
                    self.log(f"[⏳] Next bot in {i}s...")
                    time.sleep(1)

            loop_count += 1

        # Clean exit
        self.log("\n[✓] Automation stopped.")
        self.update_status("Idle", bot_text="None")
        for btn in self._all_start_buttons():
            btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = BotRunnerGUI(root)
    root.mainloop()
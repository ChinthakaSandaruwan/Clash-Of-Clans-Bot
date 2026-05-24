"""
Clash of Clans – New Update Bot GUI Controller
===============================================
Features:
  - Army Configuration: Set troop counts, hero enable/skip, spell counts
  - Save / Load army config from army_config.json
  - Start / Pause / Stop loop controls
  - Loop count, Infinite mode, Cooldown, Attack Strategy settings
  - Live dark-themed console log viewer
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import os
import sys
import json
import random

# ─── Path Setup ────────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
ARMY_CONFIG_FILE = os.path.join(script_dir, "army_config.json")

import new_update_bot


# ─── Stdout Redirector ─────────────────────────────────────────────────────────
class DualRedirector:
    def __init__(self, widget, original):
        self.widget   = widget
        self.original = original

    def write(self, s):
        if self.original:
            self.original.write(s)
        self.widget.after(0, self._append, s)

    def _append(self, s):
        try:
            self.widget.configure(state="normal")
            self.widget.insert("end", s)
            self.widget.see("end")
            self.widget.configure(state="disabled")
        except Exception:
            pass

    def flush(self):
        if self.original:
            self.original.flush()


# ─── Helpers ───────────────────────────────────────────────────────────────────
CLR_BG      = "#0f0f0f"
CLR_PANEL   = "#1a1a1a"
CLR_CARD    = "#222222"
CLR_BORDER  = "#2e2e2e"
CLR_ACCENT  = "#3498db"
CLR_GREEN   = "#27ae60"
CLR_ORANGE  = "#d35400"
CLR_RED     = "#c0392b"
CLR_YELLOW  = "#f1c40f"
CLR_TEXT    = "#e8e8e8"
CLR_MUTED   = "#888888"
CLR_LOG_BG  = "#050505"
CLR_LOG_FG  = "#2ecc71"

FONT_TITLE  = ("Segoe UI", 13, "bold")
FONT_HEAD   = ("Segoe UI", 10, "bold")
FONT_BODY   = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 9)


def styled_label(parent, text, fg=CLR_TEXT, font=FONT_BODY, **kw):
    return tk.Label(parent, text=text, fg=fg, bg=parent["bg"], font=font, **kw)


def styled_spin(parent, var, from_, to, width=7):
    return tk.Spinbox(parent, textvariable=var, from_=from_, to=to,
                      font=FONT_BODY, width=width,
                      bg=CLR_CARD, fg=CLR_TEXT,
                      insertbackground="white", bd=0,
                      relief=tk.FLAT, highlightthickness=1,
                      highlightbackground=CLR_BORDER)


def styled_entry(parent, var, width=18):
    return tk.Entry(parent, textvariable=var,
                    font=FONT_BODY, width=width,
                    bg=CLR_CARD, fg=CLR_TEXT,
                    insertbackground="white", bd=0,
                    relief=tk.FLAT, highlightthickness=1,
                    highlightbackground=CLR_BORDER)


def styled_check(parent, text, var, command=None):
    kw = dict(text=text, variable=var, font=FONT_BODY,
              fg=CLR_TEXT, bg=parent["bg"],
              selectcolor=CLR_CARD, activebackground=parent["bg"],
              activeforeground=CLR_TEXT, bd=0)
    if command:
        kw["command"] = command
    return tk.Checkbutton(parent, **kw)


def make_btn(parent, text, color, command, w=16, h=2):
    return tk.Button(parent, text=text, font=FONT_HEAD,
                     bg=color, fg="#ffffff",
                     activebackground=color, activeforeground="#ffffff",
                     bd=0, width=w, height=h,
                     cursor="hand2", command=command,
                     relief=tk.FLAT)


def section_frame(parent, title, color=CLR_ACCENT):
    """A labelled dark section card."""
    f = tk.LabelFrame(parent, text=f"  {title}  ",
                      font=FONT_HEAD, fg=color,
                      bg=CLR_PANEL, bd=1, relief=tk.GROOVE,
                      padx=10, pady=8)
    return f


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN GUI CLASS
# ═══════════════════════════════════════════════════════════════════════════════
class BotGUIController:
    def __init__(self, root):
        self.root = root
        self.root.title("Clash of Clans  –  New Update Bot Controller")
        self.root.configure(bg=CLR_BG)
        self.root.geometry("820x920")
        self.root.minsize(760, 800)

        self.is_running = False
        self.bot_thread = None
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr

        self._build_ui()

        # Redirect output to log widget
        sys.stdout = DualRedirector(self.log_area, self.orig_stdout)
        sys.stderr = DualRedirector(self.log_area, self.orig_stderr)

        # Auto-load saved army config
        self._load_army()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ──────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground=CLR_CARD,
                        background=CLR_PANEL,
                        foreground=CLR_TEXT,
                        arrowcolor=CLR_TEXT)

        pad = dict(padx=10, pady=6)
        main = tk.Frame(self.root, bg=CLR_BG, padx=12, pady=10)
        main.pack(fill=tk.BOTH, expand=True)

        # ── Header ─────────────────────────────────────────────────────────
        hdr = tk.Frame(main, bg=CLR_PANEL, bd=1, relief=tk.SOLID, padx=12, pady=10)
        hdr.pack(fill=tk.X, pady=(0, 8))

        tk.Label(hdr, text="⚔  CLASH OF CLANS — NEW UPDATE BOT CONTROLLER",
                 font=FONT_TITLE, fg=CLR_ACCENT, bg=CLR_PANEL).pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="● Idle")
        self.status_lbl = tk.Label(hdr, textvariable=self.status_var,
                                   font=FONT_HEAD, fg=CLR_MUTED, bg=CLR_PANEL)
        self.status_lbl.pack(side=tk.RIGHT)

        # ── Loop & Strategy Settings ────────────────────────────────────────
        sf = section_frame(main, "Loop & Strategy Options")
        sf.pack(fill=tk.X, pady=(0, 8))

        # Loop count row
        r0 = tk.Frame(sf, bg=CLR_PANEL)
        r0.pack(fill=tk.X, pady=3)
        styled_label(r0, "Loop Count:", font=FONT_HEAD).pack(side=tk.LEFT)
        self.loop_count_var = tk.IntVar(value=1)
        self.loop_spin = styled_spin(r0, self.loop_count_var, 1, 9999)
        self.loop_spin.pack(side=tk.LEFT, padx=8)
        self.infinite_var = tk.BooleanVar(value=False)
        self.infinite_check = styled_check(r0, "Infinite Loops", self.infinite_var,
                                           command=self._toggle_infinite)
        self.infinite_check.pack(side=tk.LEFT, padx=8)

        # Cooldown row
        r1 = tk.Frame(sf, bg=CLR_PANEL)
        r1.pack(fill=tk.X, pady=3)
        styled_label(r1, "Cooldown (sec):", font=FONT_HEAD).pack(side=tk.LEFT)
        self.cooldown_var = tk.IntVar(value=10)
        self.cooldown_spin = styled_spin(r1, self.cooldown_var, 1, 3600)
        self.cooldown_spin.pack(side=tk.LEFT, padx=8)

        # Strategy row
        r2 = tk.Frame(sf, bg=CLR_PANEL)
        r2.pack(fill=tk.X, pady=3)
        styled_label(r2, "Attack Strategy:", font=FONT_HEAD).pack(side=tk.LEFT)
        self.strategy_var = tk.StringVar(value="Alternating (Left -> Right -> Random)")
        self.strategy_combo = ttk.Combobox(r2, textvariable=self.strategy_var,
                                           values=[
                                               "Alternating (Left -> Right -> Random)",
                                               "Left Side Only",
                                               "Right Side Only",
                                               "Random (Left / Right each loop)"
                                           ],
                                           font=FONT_BODY, state="readonly", width=40)
        self.strategy_combo.pack(side=tk.LEFT, padx=8)

        # ── Army Configuration ──────────────────────────────────────────────
        af = section_frame(main, "Army Configuration", color="#e67e22")
        af.pack(fill=tk.X, pady=(0, 8))
        self.army_widgets = []

        # ─ Troops ─
        tk.Label(af, text="🪖  Troops", font=FONT_HEAD,
                 fg="#e67e22", bg=CLR_PANEL).grid(row=0, column=0, columnspan=4,
                                                   sticky="w", pady=(0, 4))

        troop_labels  = ["T1", "T2", "T3", "T4 (Siege Machine)"]
        troop_defaults = ["Electro Dragon", "Balloon", "Archer", "Stone Slammer"]
        troop_counts   = [11, 3, 1, 1]
        self.troop_name_vars  = []
        self.troop_count_vars = []

        for i, (lbl, name, cnt) in enumerate(zip(troop_labels, troop_defaults, troop_counts)):
            row = i + 1
            col_fg = "#e67e22" if i == 3 else CLR_MUTED
            tk.Label(af, text=lbl, font=FONT_BODY, fg=col_fg,
                     bg=CLR_PANEL, width=16, anchor="w").grid(row=row, column=0, sticky="w")
            nv = tk.StringVar(value=name)
            cv = tk.IntVar(value=cnt)
            self.troop_name_vars.append(nv)
            self.troop_count_vars.append(cv)
            entry = styled_entry(af, nv, width=20)
            entry.grid(row=row, column=1, padx=6, pady=2, sticky="w")
            self.army_widgets.append(entry)
            spin = styled_spin(af, cv, 1, 200, width=6)
            if i == 3:  # Siege Machine always 1 — lock it
                cv.set(1)
                spin.configure(state="disabled")
            else:
                self.army_widgets.append(spin)
            spin.grid(row=row, column=2, padx=4, pady=2, sticky="w")
            tk.Label(af, text="troops", font=FONT_BODY, fg=CLR_MUTED,
                     bg=CLR_PANEL).grid(row=row, column=3, sticky="w")

        # ─ Heroes ─
        tk.Label(af, text="🦸  Heroes", font=FONT_HEAD,
                 fg="#9b59b6", bg=CLR_PANEL).grid(row=6, column=0, columnspan=4,
                                                    sticky="w", pady=(10, 4))

        hero_labels   = ["H1 (BK)", "H2 (AQ)", "H3 (GW)", "H4 (RC)"]
        hero_defaults  = ["Barbarian King", "Archer Queen", "Grand Warden", "Royal Champion"]
        self.hero_name_vars    = []
        self.hero_enabled_vars = []

        for i, (lbl, name) in enumerate(zip(hero_labels, hero_defaults)):
            row = 7 + i
            tk.Label(af, text=lbl, font=FONT_BODY, fg=CLR_MUTED,
                     bg=CLR_PANEL, width=16, anchor="w").grid(row=row, column=0, sticky="w")
            nv = tk.StringVar(value=name)
            ev = tk.BooleanVar(value=True)
            self.hero_name_vars.append(nv)
            self.hero_enabled_vars.append(ev)
            entry = styled_entry(af, nv, width=20)
            entry.grid(row=row, column=1, padx=6, pady=2, sticky="w")
            self.army_widgets.append(entry)
            chk = styled_check(af, "Deploy", ev)
            chk.grid(row=row, column=2, columnspan=2, padx=4, pady=2, sticky="w")
            self.army_widgets.append(chk)

        # ─ Spells ─
        tk.Label(af, text="✨  Spells", font=FONT_HEAD,
                 fg="#1abc9c", bg=CLR_PANEL).grid(row=12, column=0, columnspan=4,
                                                    sticky="w", pady=(10, 4))

        spell_labels   = ["S1", "S2"]
        spell_defaults  = ["Rage", "Freeze"]
        spell_counts_d  = [5, 2]
        self.spell_name_vars  = []
        self.spell_count_vars = []

        for i, (lbl, name, cnt) in enumerate(zip(spell_labels, spell_defaults, spell_counts_d)):
            row = 13 + i
            tk.Label(af, text=lbl, font=FONT_BODY, fg=CLR_MUTED,
                     bg=CLR_PANEL, width=16, anchor="w").grid(row=row, column=0, sticky="w")
            nv = tk.StringVar(value=name)
            cv = tk.IntVar(value=cnt)
            self.spell_name_vars.append(nv)
            self.spell_count_vars.append(cv)
            entry = styled_entry(af, nv, width=20)
            entry.grid(row=row, column=1, padx=6, pady=2, sticky="w")
            self.army_widgets.append(entry)
            spin = styled_spin(af, cv, 1, 30, width=6)
            spin.grid(row=row, column=2, padx=4, pady=2, sticky="w")
            self.army_widgets.append(spin)

        # ─ Save / Load Buttons ─
        btn_row = tk.Frame(af, bg=CLR_PANEL)
        btn_row.grid(row=16, column=0, columnspan=4, sticky="w", pady=(12, 0))
        self.save_btn = make_btn(btn_row, "💾  Save Army", "#1a5276", self._save_army, w=14, h=1)
        self.save_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.load_btn = make_btn(btn_row, "📂  Load Army", "#1a5276", self._load_army, w=14, h=1)
        self.load_btn.pack(side=tk.LEFT)
        tk.Label(btn_row, text="(auto-saved to army_config.json)",
                 font=FONT_BODY, fg=CLR_MUTED, bg=CLR_PANEL).pack(side=tk.LEFT, padx=12)

        # ── Control Buttons ─────────────────────────────────────────────────
        cf = tk.Frame(main, bg=CLR_BG)
        cf.pack(fill=tk.X, pady=(0, 8))

        self.start_btn = make_btn(cf, "▶  START BOT", CLR_GREEN, self._start)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.pause_btn = make_btn(cf, "⏸  PAUSE BOT", CLR_ORANGE, self._pause)
        self.pause_btn.configure(state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = make_btn(cf, "⏹  STOP BOT", CLR_RED, self._stop)
        self.stop_btn.configure(state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

        # ── Activity Bar ────────────────────────────────────────────────────
        abar = tk.Frame(main, bg=CLR_PANEL, bd=1, relief=tk.SOLID, padx=10, pady=6)
        abar.pack(fill=tk.X, pady=(0, 8))

        self.loop_var  = tk.StringVar(value="Loop: —")
        self.timer_var = tk.StringVar(value="")
        tk.Label(abar, textvariable=self.loop_var,
                 font=FONT_BODY, fg=CLR_MUTED, bg=CLR_PANEL).pack(side=tk.LEFT)
        tk.Label(abar, textvariable=self.timer_var,
                 font=FONT_HEAD, fg=CLR_YELLOW, bg=CLR_PANEL).pack(side=tk.RIGHT)

        # ── Live Log ────────────────────────────────────────────────────────
        lf = section_frame(main, "Live Console Logs")
        lf.pack(fill=tk.BOTH, expand=True)

        self.log_area = scrolledtext.ScrolledText(lf, wrap=tk.WORD,
                                                  font=FONT_MONO,
                                                  bg=CLR_LOG_BG, fg=CLR_LOG_FG,
                                                  insertbackground="white", bd=0)
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.configure(state="normal")
        self.log_area.insert("end",
            "System Ready.\n"
            "  • Configure your army below, then press START BOT.\n"
            "  • Hero 'Deploy' checkbox: uncheck to skip heroes that are upgrading.\n"
            "  • Troop count = exact number of clicks per slot.\n"
            "  • Spell count = max number of casts per spell slot.\n\n")
        self.log_area.configure(state="disabled")

    # ──────────────────────────────────────────────────────────────────────────
    #  ARMY CONFIG  SAVE / LOAD
    # ──────────────────────────────────────────────────────────────────────────
    def _army_config_dict(self):
        troops = [{"name": self.troop_name_vars[i].get(),
                   "count": self.troop_count_vars[i].get()} for i in range(4)]
        heroes = [{"name": self.hero_name_vars[i].get(),
                   "enabled": self.hero_enabled_vars[i].get()} for i in range(4)]
        spells = [{"name": self.spell_name_vars[i].get(),
                   "count": self.spell_count_vars[i].get()} for i in range(2)]
        return {"troops": troops, "heroes": heroes, "spells": spells}

    def _save_army(self):
        cfg = self._army_config_dict()
        try:
            with open(ARMY_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            print(f"[ARMY] Config saved to army_config.json")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _load_army(self):
        if not os.path.exists(ARMY_CONFIG_FILE):
            return
        try:
            with open(ARMY_CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)

            for i, t in enumerate(cfg.get("troops", [])[:4]):
                self.troop_name_vars[i].set(t.get("name", ""))
                if i != 3:   # don't overwrite Siege Machine lock
                    self.troop_count_vars[i].set(t.get("count", 1))

            for i, h in enumerate(cfg.get("heroes", [])[:4]):
                self.hero_name_vars[i].set(h.get("name", ""))
                self.hero_enabled_vars[i].set(h.get("enabled", True))

            for i, s in enumerate(cfg.get("spells", [])[:2]):
                self.spell_name_vars[i].set(s.get("name", ""))
                self.spell_count_vars[i].set(s.get("count", 1))

            print("[ARMY] Config loaded from army_config.json")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    # ──────────────────────────────────────────────────────────────────────────
    #  TOGGLE / CONTROLS
    # ──────────────────────────────────────────────────────────────────────────
    def _toggle_infinite(self):
        self.loop_spin.configure(
            state=tk.DISABLED if self.infinite_var.get() else tk.NORMAL)

    def _lock_ui(self, lock: bool):
        state = tk.DISABLED if lock else tk.NORMAL
        
        # Configure standard widgets
        for w in [self.loop_spin, 
                  self.infinite_check if hasattr(self, "infinite_check") else None,
                  self.cooldown_spin if hasattr(self, "cooldown_spin") else None]:
            if w:
                try:
                    w.configure(state=state)
                except Exception:
                    pass
        
        # Configure strategy combo
        if hasattr(self, "strategy_combo") and self.strategy_combo:
            try:
                self.strategy_combo.configure(state="disabled" if lock else "readonly")
            except Exception:
                pass
                
        # Configure army widgets
        if hasattr(self, "army_widgets") and self.army_widgets:
            for w in self.army_widgets:
                try:
                    w.configure(state=state)
                except Exception:
                    pass
                    
        # Configure save/load buttons
        for btn in [self.save_btn if hasattr(self, "save_btn") else None,
                    self.load_btn if hasattr(self, "load_btn") else None]:
            if btn:
                try:
                    btn.configure(state=state)
                except Exception:
                    pass
                    
        # Apply special rule for loop_spin state based on infinite checkbox
        if not lock and self.infinite_var.get():
            try:
                self.loop_spin.configure(state=tk.DISABLED)
            except Exception:
                pass

    def _set_status(self, text, color=CLR_MUTED):
        self.status_var.set(text)
        self.status_lbl.configure(fg=color)

    # ──────────────────────────────────────────────────────────────────────────
    #  BOT CONTROLS
    # ──────────────────────────────────────────────────────────────────────────
    def _start(self):
        if self.is_running:
            return
        self.is_running = True
        self._set_status("● Running", CLR_GREEN)
        self.start_btn.configure(state=tk.DISABLED)
        self.pause_btn.configure(state=tk.NORMAL,
                                 text="⏸  PAUSE BOT", bg=CLR_ORANGE)
        self.stop_btn.configure(state=tk.NORMAL)
        self._lock_ui(True)

        self.bot_thread = threading.Thread(target=self._worker, daemon=True)
        self.bot_thread.start()

    def _pause(self):
        if not self.is_running:
            return
        if new_update_bot.bot_paused.is_set():
            new_update_bot.bot_paused.clear()
            self.pause_btn.configure(text="▶  RESUME BOT", bg=CLR_GREEN)
            self._set_status("⏸ Paused", CLR_YELLOW)
            print("\n⏸ [PAUSED] Bot paused.")
        else:
            new_update_bot.bot_paused.set()
            self.pause_btn.configure(text="⏸  PAUSE BOT", bg=CLR_ORANGE)
            self._set_status("● Running", CLR_GREEN)
            print("\n▶ [RESUMED] Bot resumed.")

    def _stop(self):
        if not self.is_running:
            return
        print("\n⏹ [STOPPING] Sending stop signal...")
        new_update_bot.bot_stopped = True
        new_update_bot.bot_paused.set()
        self.stop_btn.configure(state=tk.DISABLED)
        self.pause_btn.configure(state=tk.DISABLED)
        self._set_status("⏹ Stopping", CLR_RED)

    # ──────────────────────────────────────────────────────────────────────────
    #  WORKER THREAD
    # ──────────────────────────────────────────────────────────────────────────
    def _worker(self):
        max_loops  = self.loop_count_var.get()
        is_inf     = self.infinite_var.get()
        cooldown   = self.cooldown_var.get()
        strategy   = self.strategy_var.get()
        army_cfg   = self._army_config_dict()

        new_update_bot.bot_stopped = False
        new_update_bot.bot_paused.set()

        loop = 1
        try:
            while not new_update_bot.bot_stopped:
                if not is_inf and loop > max_loops:
                    break

                lbl = f"Loop {loop}" if is_inf else f"Loop {loop} of {max_loops}"
                self.root.after(0, lambda l=lbl: self.loop_var.set(f"Loop: {l}"))
                self.root.after(0, lambda: self._set_status("● Running", CLR_GREEN))

                print(f"\n{'='*50}")
                print(f"  BOT ATTACK — {lbl.upper()}")
                army_strs = [f"{t['name']}x{t['count']}" for t in army_cfg['troops']]
                print(f"  Army: {', '.join(army_strs)}")
                heroes_on = [h['name'] for h in army_cfg['heroes'] if h['enabled']]
                print(f"  Heroes: {', '.join(heroes_on) if heroes_on else 'none'}")
                spell_strs = [f"{s['name']}x{s['count']}" for s in army_cfg['spells']]
                print(f"  Spells: {', '.join(spell_strs)}")
                print(f"{'='*50}")

                # Set attack strategy
                if strategy == "Left Side Only":
                    new_update_bot.forced_side = "left"
                elif strategy == "Right Side Only":
                    new_update_bot.forced_side = "right"
                elif strategy == "Random (Left / Right each loop)":
                    new_update_bot.forced_side = random.choice(["left", "right"])
                else:
                    new_update_bot.forced_side = None

                # Execute attack
                new_update_bot.main(army_config=army_cfg)

                if new_update_bot.bot_stopped:
                    break

                loop += 1

                # Cooldown
                if is_inf or loop <= max_loops:
                    print(f"\n[⏳] Cooldown: {cooldown}s before next attack...")
                    self.root.after(0, lambda: self._set_status("⏳ Cooldown", CLR_YELLOW))
                    for sec in range(cooldown, 0, -1):
                        if new_update_bot.bot_stopped:
                            break
                        self.root.after(0, lambda s=sec: self.timer_var.set(f"Next attack in {s}s"))
                        try:
                            new_update_bot.bot_sleep(1.0)
                        except KeyboardInterrupt:
                            break
                    self.root.after(0, lambda: self.timer_var.set(""))

            msg = "⏹ [STOPPED]" if new_update_bot.bot_stopped else "🏁 [FINISHED]"
            print(f"\n{msg} Bot loop ended.")

        except KeyboardInterrupt:
            print("\n⏹ [STOPPED] Bot stopped by user.")
        except Exception as e:
            print(f"\n❌ [ERROR] {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.root.after(0, self._reset_ui)

    def _reset_ui(self):
        self.is_running = False
        self._set_status("● Idle", CLR_MUTED)
        self.loop_var.set("Loop: —")
        self.timer_var.set("")
        self.start_btn.configure(state=tk.NORMAL)
        self.pause_btn.configure(state=tk.DISABLED,
                                 text="⏸  PAUSE BOT", bg=CLR_ORANGE)
        self.stop_btn.configure(state=tk.DISABLED)
        self._lock_ui(False)

    def _on_close(self):
        if self.is_running:
            new_update_bot.bot_stopped = True
            new_update_bot.bot_paused.set()
        sys.stdout = self.orig_stdout
        sys.stderr = self.orig_stderr
        self.root.destroy()


# ─── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = BotGUIController(root)
    root.mainloop()

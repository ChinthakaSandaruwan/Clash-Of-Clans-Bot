# No Need GUI , i want run this all bots bot 1 ,bot 2, bot 3, bot 4, bot 5, bot 6 , bot 7, bot 8, bot 9, bot 10  Using This Main.py File 

# run logic 
# bot1.py start -> bot1.py running -> bot1.py end 
# wait 10 seconds
# bot2.py start -> bot2.py running -> bot2.py end
# wait 10 seconds
# bot3.py start -> bot3.py running -> bot3.py end
# wait 10 seconds
# bot4.py start -> bot4.py running -> bot4.py end
# wait 10 seconds
# bot5.py start -> bot5.py running -> bot5.py end
# wait 10 seconds
# bot6.py start -> bot6.py running -> bot6.py end
# wait 10 seconds
# bot7.py start -> bot7.py running -> bot7.py end
# wait 10 seconds
# bot8.py start -> bot8.py running -> bot8.py end
# wait 10 seconds
# bot9.py start -> bot9.py running -> bot9.py end
# wait 10 seconds
# bot10.py start -> bot10.py running -> bot10.py end
# wait 10 seconds
# bot11.py start -> bot11.py running -> bot11.py end
# wait 10 seconds
# bot12.py start -> bot12.py running -> bot12.py end
#wait 10 seconds

# run again like a loop  again and again
# bot1.py start -> bot1.py running -> bot1.py end 
# wait 10 seconds
# bot2.py start -> bot2.py running -> bot2.py end
# wait 10 seconds
# bot3.py start -> bot3.py running -> bot3.py end
# wait 10 seconds
# bot4.py start -> bot4.py running -> bot4.py end
# wait 10 seconds
# bot5.py start -> bot5.py running -> bot5.py end
# wait 10 seconds
# bot6.py start -> bot6.py running -> bot6.py end
# wait 10 seconds
# bot7.py start -> bot7.py running -> bot7.py end
# wait 10 seconds
# bot8.py start -> bot8.py running -> bot8.py end
# wait 10 seconds
# bot9.py start -> bot9.py running -> bot9.py end
# wait 10 seconds
# bot10.py start -> bot10.py running -> bot10.py end
# wait 10 seconds
# bot11.py start -> bot11.py running -> bot11.py end
# wait 10 seconds
# bot12.py start -> bot12.py running -> bot12.py end
# wait 10 seconds

import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import time
import os
import threading

# List of all your bot scripts
BOT_SCRIPTS = [
    "bot1.py", "bot2.py", "bot3.py", "bot4.py", "bot5.py",
    "bot6.py", "bot7.py", "bot8.py", "bot9.py", "bot10.py", "bot11.py", "bot12.py"
]
WAIT_TIME = 10

class BotRunnerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Bot Automation Clash Of Clans Controller For Max Army Camp")
        self.root.geometry("650x500")
        self.root.minsize(500, 400)
        
        # State variables
        self.is_running = False
        self.automation_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # --- Top Control Panel ---
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        self.start_btn = ttk.Button(control_frame, text="▶ Start Automation", command=self.start_automation)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="⏹ Stop Loop", command=self.stop_automation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(control_frame, text="Status: Idle", font=("Helvetica", 10, "bold"))
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # --- Current Progress Panel ---
        progress_frame = ttk.LabelFrame(self.root, text=" Current Activity ", padding="10")
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.current_bot_label = ttk.Label(progress_frame, text="Active Bot: None", font=("Helvetica", 10))
        self.current_bot_label.pack(anchor=tk.W)
        
        self.loop_label = ttk.Label(progress_frame, text="Loop Count: 0", font=("Helvetica", 9))
        self.loop_label.pack(anchor=tk.W, pady=(5, 0))
        
        # --- Log Output Panel ---
        log_frame = ttk.LabelFrame(self.root, text=" Live Console Logs ", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, font=("Consolas", 9), bg="#1e1e1e", fg="#ffffff")
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.insert(tk.END, "System ready. Click 'Start Automation' to begin the sequence.\n")
        self.log_area.configure(state=tk.DISABLED)

    def log(self, message):
        """Thread-safe logging helper to write directly to the GUI window"""
        self.log_area.configure(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)  # Auto-scroll to bottom
        self.log_area.configure(state=tk.DISABLED)

    def update_status(self, text, bot_text=None, loop_text=None):
        """Thread-safe UI text updates"""
        self.status_label.config(text=f"Status: {text}")
        if bot_text:
            self.current_bot_label.config(text=f"Active Bot: {bot_text}")
        if loop_text:
            self.loop_label.config(text=f"Loop Count: {loop_text}")

    def start_automation(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            # Run the automation loop in a separate thread so the GUI doesn't freeze
            self.automation_thread = threading.Thread(target=self.run_loop_sequence, daemon=True)
            self.automation_thread.start()

    def stop_automation(self):
        if self.is_running:
            self.is_running = False
            self.log("\n[!] Stop requested. Finishing current step and safely shutting down...")
            self.update_status("Stopping...")
            self.stop_btn.config(state=tk.DISABLED)

    def run_loop_sequence(self):
        loop_count = 1
        
        while self.is_running:
            self.log(f"\n=========================================\n  STARTING LOOP ITERATION #{loop_count}\n=========================================")
            self.update_status("Running Sequence", loop_text=str(loop_count))
            
            for bot in BOT_SCRIPTS:
                if not self.is_running:
                    break
                    
                if not os.path.exists(bot):
                    self.log(f"[Warning] File '{bot}' not found. Skipping...")
                    continue
                
                # Update status bars
                self.update_status("Bot Active", bot_text=bot)
                self.log(f"\n[➔] {bot} start")
                self.log(f"[⚙] {bot} running...")
                
                # Execute bot and wait for it to finish
                # stdout/stderr tracking makes sure bot internal prints flow through to main console terminal
                result = subprocess.run(["python", bot])
                
                self.log(f"[✓] {bot} ended (Exit Code: {result.returncode})")
                
                if not self.is_running:
                    break
                    
                # 10-second wait system that checks every second if the user hit stop
                self.update_status("Cooldown / Waiting", bot_text=f"Waiting after {bot}")
                for i in range(WAIT_TIME, 0, -1):
                    if not self.is_running:
                        break
                    self.log(f"[⏳] Next bot in {i} seconds...")
                    time.sleep(1)
            
            loop_count += 1
            
        # Reset UI on clean exit
        self.log("\n[✓] Automation loop stopped entirely.")
        self.update_status("Idle", bot_text="None")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = BotRunnerGUI(root)
    root.mainloop()
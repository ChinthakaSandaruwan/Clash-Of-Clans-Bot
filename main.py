# no need GUI , i want run this all bots bot 1 ,bot 2, bot 3, bot 4, bot 5, bot 6 , bot 7, bot 8, bot 9, bot 10  using this main.py file 

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


import subprocess
import time
import os

# List of all your bot scripts (ordered from bot1 to bot11)
BOT_SCRIPTS = [
    "bot1.py", "bot2.py", "bot3.py", "bot4.py", "bot5.py",
    "bot6.py", "bot7.py", "bot8.py", "bot9.py", "bot10.py", "bot11.py"
]

WAIT_TIME = 10  # Seconds to wait between bots

def run_bots_loop():
    loop_count = 1
    
    try:
        while True:
            print(f"\n========== STARTING LOOP ITERATION #{loop_count} ==========")
            
            for bot in BOT_SCRIPTS:
                # Quick safety check to see if the file actually exists
                if not os.path.exists(bot):
                    print(f"[Warning] {bot} not found in this folder. Skipping to next...")
                    continue
                
                print(f"\n[➔] {bot} start")
                print(f"[⚙] {bot} running...")
                
                # subprocess.run waits until the script finishes executing
                result = subprocess.run(["python", bot])
                
                print(f"[✓] {bot} end (Exit Code: {result.returncode})")
                
                # Wait 10 seconds before starting the next bot
                print(f"[⏳] Waiting {WAIT_TIME} seconds...")
                time.sleep(WAIT_TIME)
            
            print(f"\n========== FINISHED LOOP ITERATION #{loop_count} ==========")
            loop_count += 1
            
    except KeyboardInterrupt:
        print("\n[!] Automation stopped manually by user (Ctrl+C). Exiting cleanly.")

if __name__ == "__main__":
    run_bots_loop()
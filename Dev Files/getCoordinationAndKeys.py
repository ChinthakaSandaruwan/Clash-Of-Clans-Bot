import time
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key

print("=== Real-Time Delay, Click, Scroll & Keyboard Capturer ===")
print("දැන් ගේම් එකට/app එකට ගිහින් ඔයා සාමාන්‍යයෙන් කරන වැඩ ටික කරන්න.")
print("පළමු Click 3 මඟ හරින අතර 4 වන Click එකේ සිට සැබෑ වෙලාව (Delay) මැන සේව් කරයි.")
print("වැඩේ ඉවර වුණාම Mouse එකේ 'Right Click' එකක් කරන්න.\n")

last_action_time = None
file_path = "actions_log.txt"

# 🌟 Click වාර ගණන මැනීමට ගෝලීය කවුන්ටරයක් (Counter)
click_count = 0

# File එක අලුතින් open කරලා header එකක් දාමු
with open(file_path, "a", encoding="utf-8") as f:
    f.write(f"\n--- New Session ({time.strftime('%Y-%m-%d %H:%M:%S')}) ---\n")

def get_delay():
    global last_action_time
    current_time = time.time()
    
    if last_action_time is None:
        delay = 0.5
    else:
        delay = round(current_time - last_action_time, 2)
        
    last_action_time = current_time
    return delay

def log_action(action_str):
    """Actions log file එකට ලියන පොදු function එක"""
    delay = get_delay()
    log_line = f"{action_str}\ntime.sleep({delay})\n\n"
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(log_line)
    print(f"Captured: {action_str} | Delay: {delay}s")

# --- Mouse Functions ---
def on_click(x, y, button, pressed):
    global click_count
    
    if pressed:
        if button == Button.right:
            print("\n[Finished] සේව් වුණා. වැඩසටහන නැවැත්තුවා.")
            return False # Listener නවත්වන්න
        
        if button == Button.left:
            click_count += 1  # Click එකක් සිදුවූ වාර ගණන 1කින් එකතු කරයි
            
            # 🌟 Click වාර ගණන 3 හෝ ඊට අඩු නම් එය මඟ හැරීමට (Skip) සලස්වයි
            if click_count <= 3:
                print(f"[SKIP] පළමු Click 3න් එකක් මඟ හැරියා (Click වාරය: {click_count}/3)")
                # පළමු ක්ලික් වල කාලය මීළඟ ඒවාට බලපෑම් නොකිරීමට කාලය යාවත්කාලීන කරයි
                global last_action_time
                last_action_time = time.time()
                return 
            
            # 4 වන Click එකේ සිට සාමාන්‍ය පරිදි ලොග් වේ
            log_action(f"pyautogui.click({x}, {y})")

def on_scroll(x, y, dx, dy):
    # 🌟 පළමු ක්ලික් 3 අවසන් වනතුරු Scroll ක්‍රියාවන්ද සටහන් නොකරයි
    if click_count < 3:
        return
    scroll_amount = 1000 if dy > 0 else -1000
    log_action(f"pyautogui.scroll({scroll_amount})")

# --- Keyboard Function ---
def on_press(key):
    # 🌟 පළමු ක්ලික් 3 අවසන් වනතුරු Keyboard ක්‍රියාවන්ද සටහන් නොකරයි
    if click_count < 3:
        return
        
    try:
        # සාමාන්‍ය අකුරු සහ අංක (a-z, 0-9)
        if hasattr(key, 'char') and key.char is not None:
            log_action(f"pyautogui.write('{key.char}')")
        
        # Space key එක
        elif key == Key.space:
            log_action(f"pyautogui.press('space')")
            
        # Enter key එක
        elif key == Key.enter:
            log_action(f"pyautogui.press('enter')")

    except Exception as e:
        print(f"Error: {e}")

# --- Listeners Start ---
# Mouse Listener
mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
# Keyboard Listener
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

# Right click කරනකම් මෙතන රැඳී සිටී
mouse_listener.join()
# Mouse එක නැවැත්තුවාම keyboard එකත් නවත්වන්න
keyboard_listener.stop()

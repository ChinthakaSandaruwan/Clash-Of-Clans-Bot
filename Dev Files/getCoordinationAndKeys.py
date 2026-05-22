import time
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key

print("=== Real-Time Delay, Click, Scroll & Keyboard Capturer ===")
print("Now go to the game/app and perform your normal actions.")
print("The first 3 clicks will be skipped, and from the 4th click onwards, the real delay will be measured and saved.")
print("When you are finished, perform a 'Right Click' with your mouse.\n")

last_action_time = None
file_path = "actions_log.txt"

# 🌟 Global counter to measure the number of clicks
click_count = 0

# Open the file freshly and write a header
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
    """Common function to write actions into the log file"""
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
            print("\n[Finished] Saved successfully. Program stopped.")
            return False # Stop the listener
        
        if button == Button.left:
            click_count += 1  # Increments the click count by 1
            
            # 🌟 Skips the click if the count is 3 or less
            if click_count <= 3:
                print(f"[SKIP] Skipped one of the first 3 clicks (Click count: {click_count}/3)")
                # Updates the time so that the duration of the first clicks doesn't affect subsequent ones
                global last_action_time
                last_action_time = time.time()
                return 
            
            # Logs normally starting from the 4th click
            log_action(f"pyautogui.click({x}, {y})")

def on_scroll(x, y, dx, dy):
    # 🌟 Do not log scroll actions until the first 3 clicks are completed
    if click_count < 3:
        return
    scroll_amount = 1000 if dy > 0 else -1000
    log_action(f"pyautogui.scroll({scroll_amount})")

# --- Keyboard Function ---
def on_press(key):
    # 🌟 Do not log keyboard actions until the first 3 clicks are completed
    if click_count < 3:
        return
        
    try:
        # Standard letters and numbers (a-z, 0-9)
        if hasattr(key, 'char') and key.char is not None:
            log_action(f"pyautogui.write('{key.char}')")
        
        # Space key
        elif key == Key.space:
            log_action(f"pyautogui.press('space')")
            
        # Enter key
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

# Remains here until a right click is performed
mouse_listener.join()
# Stop the keyboard listener when the mouse listener stops
keyboard_listener.stop()
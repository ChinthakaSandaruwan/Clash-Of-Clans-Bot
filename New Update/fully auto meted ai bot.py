import cv2
import numpy as np
import pyautogui
import os
import time
import math
import random
from PIL import ImageGrab
from pynput.mouse import Controller

# ─── Safety and Configuration ──────────────────────────────────────────────────
pyautogui.FAILSAFE = True  # Move mouse to any corner to stop the bot
mouse_ctrl = Controller()

# Determine paths to template images relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
images_dir = os.path.join(project_root, "Normal Battle", "Images")

# Template names
TEMPLATES = {
    "attack_lobby": "(1)attack!.png",
    "find_match": "(2)Find a Match 1700.png",
    "attack_confirm": "(3)Attack!.png",
    "return_home": "(4)Return Home.png",
    "star_bonus": "(0)Star Bonus Received.png"
}

# ─── Multi-Scale OpenCV Template Matching ───────────────────────────────────────
def find_template(template_name, threshold=0.72):
    """
    Finds a template on the screen at multiple scales to support different screen resolutions.
    Returns (cx, cy) if found, otherwise None.
    """
    img_name = TEMPLATES.get(template_name)
    if not img_name:
        print(f"[ERROR] Unknown template identifier: {template_name}")
        return None

    template_path = os.path.join(images_dir, img_name)
    template = cv2.imread(template_path)
    if template is None:
        print(f"[ERROR] Could not load template file: {template_path}")
        return None

    # Grab the current screen
    screenshot = ImageGrab.grab()
    screenshot_np = np.array(screenshot)
    screen_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    h_temp, w_temp = template_gray.shape[:2]
    best_match = None

    # Try multiple scaling factors to support different screen heights/resolutions
    scales = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]

    for scale in scales:
        resized_w = int(w_temp * scale)
        resized_h = int(h_temp * scale)

        # Skip if template is larger than the screen
        if resized_w > screen_gray.shape[1] or resized_h > screen_gray.shape[0]:
            continue
        if resized_w < 10 or resized_h < 10:
            continue

        resized_temp = cv2.resize(template_gray, (resized_w, resized_h), interpolation=cv2.INTER_AREA)
        
        result = cv2.matchTemplate(screen_gray, resized_temp, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            if best_match is None or max_val > best_match[2]:
                cx = max_loc[0] + resized_w // 2
                cy = max_loc[1] + resized_h // 2
                best_match = (cx, cy, max_val)

    if best_match is not None:
        cx, cy, confidence = best_match
        print(f"[FOUND] {img_name} at ({cx}, {cy}) with confidence {confidence:.3f}")
        return (cx, cy)

    return None

def click_template(template_name, threshold=0.72, clicks=1, post_sleep=1.0):
    """
    Waits for a template to appear on screen and clicks it.
    """
    print(f"Searching for: {TEMPLATES[template_name]}...", end="\r")
    pos = find_template(template_name, threshold)
    if pos is not None:
        pyautogui.moveTo(pos[0], pos[1], duration=0.3)
        for _ in range(clicks):
            pyautogui.click()
            time.sleep(0.1)
        print(f"[CLICK] Clicked {template_name} button.")
        time.sleep(post_sleep)
        return True
    return False

# ─── Dynamic Slot Detection (Computer Vision) ──────────────────────────────────
def is_slot_active(region_bgr, slot_x, slot_y, slot_w, slot_h, bottom_y_start):
    """
    Determines if a slot is active (colored/non-empty) or inactive (grayscale/greyed out/empty).
    Uses color saturation (S in HSV) and brightness (V in HSV) of the center icon area.
    """
    rx = slot_x
    ry = slot_y - bottom_y_start
    
    # Crop the center 50% of the slot region to isolate the icon
    w_half = slot_w // 4
    h_half = slot_h // 4
    
    x1 = max(0, rx - w_half)
    x2 = min(region_bgr.shape[1], rx + w_half)
    y1 = max(0, ry - h_half)
    y2 = min(region_bgr.shape[0], ry + h_half)
    
    crop = region_bgr[y1:y2, x1:x2]
    if crop.size == 0:
        return False
        
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    mean_sat = np.mean(hsv[:, :, 1])  # Saturation
    mean_val = np.mean(hsv[:, :, 2])  # Value/Brightness
    
    # Active cards are colorful (mean_sat > 28) and bright enough (mean_val > 45)
    # Recovering heroes or empty slots (x0) are gray/dark
    return (mean_sat > 28) and (mean_val > 45)

def detect_deployment_slots(screen_w, screen_h):
    """
    Grabs the bottom region of the screen and detects troop/hero/spell slots using CV contour detection.
    Returns a list of tuples: (cx, cy, cw, ch)
    """
    print("[INFO] Scanning bottom region for active slots...")
    
    # Grab only the bottom 22% of the screen where slots are located
    bottom_y_start = int(screen_h * 0.78)
    bottom_y_end = int(screen_h * 0.98)
    
    screenshot = ImageGrab.grab(bbox=(0, bottom_y_start, screen_w, bottom_y_end))
    screenshot_np = np.array(screenshot)
    region_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    region_gray = cv2.cvtColor(region_bgr, cv2.COLOR_BGR2GRAY)
    
    # Detect edges
    edges = cv2.Canny(region_gray, 40, 120)
    
    # Find contours of card-like shapes
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    slots_detected = []
    
    # Expected sizes of slot card relative to screen height/width
    min_h = int(screen_h * 0.06)
    max_h = int(screen_h * 0.17)
    min_w = int(screen_w * 0.02)
    max_w = int(screen_w * 0.11)
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Filter contours by size and aspect ratio (width / height)
        if (min_h < h < max_h) and (min_w < w < max_w):
            aspect = w / h
            if 0.45 < aspect < 1.3:
                cx = x + w // 2
                cy = bottom_y_start + y + h // 2
                slots_detected.append((cx, cy, w, h))
                
    # Sort slots by horizontal (x) position
    slots_detected = sorted(slots_detected, key=lambda s: s[0])
    
    # Merge overlapping/very close slot center positions (closer than 2.5% of screen width)
    min_dist = int(screen_w * 0.025)
    merged_slots = []
    
    for s in slots_detected:
        cx, cy, cw, ch = s
        if not merged_slots:
            merged_slots.append(s)
        else:
            if cx - merged_slots[-1][0] < min_dist:
                # Merge close slots by averaging coordinates and dimensions
                prev = merged_slots[-1]
                merged_slots[-1] = (
                    (prev[0] + cx) // 2,
                    (prev[1] + cy) // 2,
                    (prev[2] + cw) // 2,
                    (prev[3] + ch) // 2
                )
            else:
                merged_slots.append(s)
                
    print(f"[INFO] Detected {len(merged_slots)} slot cards at horizontal positions: {[s[0] for s in merged_slots]}")
    return merged_slots

# ─── Dynamic Attack Deployment Macro ───────────────────────────────────────────
def execute_dynamic_attack(screen_w, screen_h):
    """
    Deploys troops and spells dynamically without hardcoded coordinates.
    Monitors slot state in real-time and only deploys active cards.
    """
    # 1. Move to screen center and zoom out
    center_x = screen_w // 2
    center_y = screen_h // 2
    pyautogui.moveTo(center_x, center_y, duration=0.3)
    time.sleep(0.5)
    
    print("[SCROLL] Performing extended zoom out...")
    pyautogui.keyDown('ctrl')  # Zooming out on PC emulator usually uses Ctrl + scroll
    for _ in range(15):
        mouse_ctrl.scroll(0, -1)
        time.sleep(0.05)
    pyautogui.keyUp('ctrl')
    print("[OK] Zoom out complete.")
    time.sleep(1)
    
    # 2. Wait for loading (10 seconds)
    print("[INFO] Waiting for base rendering to finalize...")
    time.sleep(10)
    
    # 3. Detect active slots
    slots = detect_deployment_slots(screen_w, screen_h)
    
    # Fallback to horizontal grid if detection failed
    if not slots:
        print("[WARNING] No slots detected via CV. Falling back to default uniform horizontal grid...")
        y_pos = int(screen_h * 0.92)
        slot_w = int(screen_w * 0.05)
        slot_h = int(screen_h * 0.12)
        start_x = int(screen_w * 0.15)
        end_x = int(screen_w * 0.85)
        step = (end_x - start_x) // 9
        slots = [(start_x + i * step, y_pos, slot_w, slot_h) for i in range(10)]
        
    num_slots = len(slots)
    
    # Define deployment circles
    # Troops/Heroes deploy along the outer boundary (ellipse)
    rx_outer = int(screen_w * 0.36)
    ry_outer = int(screen_h * 0.36)
    
    # Spells deploy inside the core base area
    rx_inner = int(screen_w * 0.14)
    ry_inner = int(screen_h * 0.14)
    
    print("🚀 [ATTACK] Starting dynamic deployment macro...")
    
    bottom_y_start = int(screen_h * 0.78)
    bottom_y_end = int(screen_h * 0.98)
    
    # Loop through detected slots and deploy
    for idx, (slot_x, slot_y, slot_w, slot_h) in enumerate(slots):
        # Grab current screen and check if the slot is active BEFORE selecting it
        screenshot = ImageGrab.grab(bbox=(0, bottom_y_start, screen_w, bottom_y_end))
        region_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        if not is_slot_active(region_bgr, slot_x, slot_y, slot_w, slot_h, bottom_y_start):
            print(f"[SKIP] Slot {idx+1}/{num_slots} is inactive (greyed-out/empty/recovering hero).")
            continue
            
        # Select the slot
        pyautogui.moveTo(slot_x, slot_y, duration=0.2)
        pyautogui.click()
        time.sleep(0.3)
        
        # Decide if this slot is a troop/hero or a spell
        is_spell = idx >= int(num_slots * 0.8)
        
        if not is_spell:
            # Troop/Hero deployment loop: click until the card becomes empty/inactive
            print(f"[DEPLOY] Slot {idx+1}/{num_slots} (Troop/Hero) -> Deploying dynamically...")
            
            total_clicks = 0
            # Limit total loops to prevent infinite clicking on unrecognized slots
            for loop in range(10):
                # Check if still active
                screenshot = ImageGrab.grab(bbox=(0, bottom_y_start, screen_w, bottom_y_end))
                region_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                if not is_slot_active(region_bgr, slot_x, slot_y, slot_w, slot_h, bottom_y_start):
                    break
                    
                # Perform 5 clicks spread around the perimeter
                for d in range(5):
                    angle = (total_clicks / 15) * 2 * math.pi + random.uniform(-0.1, 0.1)
                    x = int(center_x + rx_outer * math.cos(angle))
                    y = int(center_y + ry_outer * math.sin(angle))
                    pyautogui.click(x, y)
                    total_clicks += 1
                    time.sleep(0.12)
                    
                time.sleep(0.1)
                
            print(f"[DEPLOY] Completed slot {idx+1} (clicks: {total_clicks})")
        else:
            # Spell deployment: drop near core center
            print(f"[DEPLOY] Slot {idx+1}/{num_slots} (Spell) -> Deploying spells...")
            total_clicks = 0
            for loop in range(3):
                # Check if still active
                screenshot = ImageGrab.grab(bbox=(0, bottom_y_start, screen_w, bottom_y_end))
                region_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                if not is_slot_active(region_bgr, slot_x, slot_y, slot_w, slot_h, bottom_y_start):
                    break
                    
                # Drop 1 spell per loop
                theta = random.uniform(0, 2 * math.pi)
                x = int(center_x + rx_inner * math.cos(theta))
                y = int(center_y + ry_inner * math.sin(theta))
                pyautogui.click(x, y)
                total_clicks += 1
                time.sleep(0.25)
                
            print(f"[DEPLOY] Completed spell slot {idx+1} (clicks: {total_clicks})")
            
        time.sleep(0.2)
        
    print("[SUCCESS] All slots deployed. Monitoring hero abilities...")
    
    # 4. Periodically click the hero/troop slots to trigger special hero abilities
    # We do this twice, waiting 15s between runs
    for cycle in range(2):
        time.sleep(15)
        print(f"[HERO] Activating hero abilities cycle {cycle+1}/2...")
        for slot_x, slot_y, _, _ in slots:
            pyautogui.click(slot_x, slot_y)
            time.sleep(0.1)
            
    print("[SUCCESS] Macro deployment finished.")

# ─── Main Program Flow ─────────────────────────────────────────────────────────
def main():
    print("--- Clash of Clans Fully Automated Dynamic Bot ---")
    screen_w, screen_h = pyautogui.size()
    print(f"Detected screen resolution: {screen_w}x{screen_h}\n")
    
    # Phase 1: Click Attack Lobby Button
    print("Waiting for Attack (Lobby) button...")
    while True:
        if click_template("attack_lobby", threshold=0.72, post_sleep=2.0):
            break
        time.sleep(0.5)
        
    # Phase 2: Click Find a Match Button
    print("Waiting for Find a Match button...")
    while True:
        if click_template("find_match", threshold=0.72, post_sleep=2.0):
            break
        time.sleep(0.5)
        
    # Phase 3: Wait for opponent base to load and confirm attack
    print("Waiting for opponent match screen...")
    while True:
        if click_template("attack_confirm", threshold=0.72, post_sleep=1.0):
            break
        time.sleep(0.5)
        
    # Phase 4: Execute the Attack Macro
    execute_dynamic_attack(screen_w, screen_h)
    
    # Phase 5: Wait for battle to finish and click Return Home
    print("Waiting for Return Home button...")
    while True:
        if click_template("return_home", threshold=0.72, post_sleep=4.0):
            break
        time.sleep(1.0)
        
    # Phase 6: Check for optional Star Bonus Received window
    print("Checking for optional Star Bonus Received window...")
    start_time = time.time()
    found_star_bonus = False
    while time.time() - start_time < 10.0:
        pos = find_template("star_bonus", threshold=0.75)
        if pos is not None:
            pyautogui.moveTo(pos[0], pos[1], duration=0.3)
            pyautogui.click()
            print("[CLICK] Closed Star Bonus Received popup.")
            found_star_bonus = True
            time.sleep(2.0)
            break
        time.sleep(0.5)
        
    if not found_star_bonus:
        print("No Star Bonus window detected.")
        
    print("\n==========================================")
    print("[SUCCESS] Fully Automated Battle completed!")
    print("==========================================")

if __name__ == "__main__":
    main()

import cv2
import numpy as np
import pyautogui
import os
import time
from PIL import ImageGrab
from pynput.mouse import Controller

# ─── Safety & Init ────────────────────────────────────────────────────────────
pyautogui.FAILSAFE = True          # Move mouse to a corner to abort the bot
mouse_ctrl = Controller()

script_dir  = os.path.dirname(os.path.abspath(__file__))
images_dir  = os.path.join(script_dir, "Images")

# ─── OpenCV Template Matching ─────────────────────────────────────────────────
def find_on_screen(template_path, threshold=0.72):
    """
    Capture the screen and use OpenCV TM_CCOEFF_NORMED to locate the template.
    Returns (center_x, center_y, confidence) on match, or None if not found.
    """
    # Grab the current screen
    screenshot = ImageGrab.grab()
    screenshot_np  = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    # Load the template from disk
    template = cv2.imread(template_path)
    if template is None:
        print(f"[ERROR] Could not load template: {template_path}")
        return None

    # Convert both to grayscale for matching
    screen_gray    = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
    template_gray  = cv2.cvtColor(template,       cv2.COLOR_BGR2GRAY)

    th, tw = template_gray.shape[:2]

    result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        cx = max_loc[0] + tw // 2
        cy = max_loc[1] + th // 2
        return (cx, cy, max_val)

    return None


# ─── Image Sequence ───────────────────────────────────────────────────────────
#
#   CORRECT FLOW:
#   1.png → Attack! (orange lobby button)
#   2.png → Find a Match (yellow button)
#   3.png → Attack! with swords (after opponent found)
#   4.png → Confirm Attack! GREEN button  ← macro runs AFTER clicking this
#   5.png → Return Home                   ← ends the loop
#
image_sequence = [
    ('1.png', 'Attack! lobby button'),
    ('2.png', 'Find a Match'),
    ('3.png', 'Attack! (rank battle screen)'),
    ('4.png', 'Confirm Attack! (green button)'),   # ← triggers macro after click
    ('5.png', 'Return Home'),
]

print("=" * 54)
print("  Clash of Clans  ─  Rank Battle Bot  (OpenCV)")
print("=" * 54)
print("Sequence: 1 → 2 → 3 → 4 (confirm+macro) → 5 (home)\n")
print("Move mouse to a screen corner to ABORT at any time.\n")

current_step = 0

while current_step < len(image_sequence):
    img_name, description = image_sequence[current_step]
    image_path = os.path.join(images_dir, img_name)

    print(f"[Step {current_step + 1}/{len(image_sequence)}] Searching for: "
          f"{img_name}  ({description})", end="\r")

    result = find_on_screen(image_path, threshold=0.72)

    if result is not None:
        cx, cy, confidence = result
        print(f"\n[FOUND] {img_name}  confidence={confidence:.3f}  at ({cx}, {cy})")
        pyautogui.moveTo(cx, cy, duration=0.2)
        pyautogui.click()
        print(f"[CLICK] Clicked ({cx}, {cy})")

        # ── Step 4: After clicking the green Confirm Attack button ────────────
        if img_name == '4.png':
            print("\n[INFO] Attack confirmed! Waiting 10 s for battle to load...")
            time.sleep(10)

            # ── Zoom out with Ctrl + scroll ───────────────────────────────────
            sw, sh = pyautogui.size()
            cx_screen, cy_screen = sw // 2, sh // 2
            pyautogui.moveTo(cx_screen, cy_screen, duration=0.3)
            time.sleep(0.4)

            print("[SCROLL] Zooming out (Ctrl + scroll)...")
            pyautogui.keyDown('ctrl')
            for _ in range(15):
                mouse_ctrl.scroll(0, -1)
                time.sleep(0.05)
            pyautogui.keyUp('ctrl')
            print("[OK] Zoom out complete.")
            time.sleep(1)

            # ── Wait for village to render then deploy ────────────────────────
            print("\n🚀 [MACRO] Deploying troops (Home Village army)...")
            time.sleep(10)

            # Electro Dragons ─────────────────────────────────────────────────
            pyautogui.click(263, 1119);  time.sleep(4.14)   # select
            pyautogui.click(639,  902);  time.sleep(0.30)   # 1
            pyautogui.click(552,  841);  time.sleep(0.25)   # 2
            pyautogui.click(478,  760);  time.sleep(0.25)   # 3
            pyautogui.click(397,  706);  time.sleep(0.25)   # 4
            pyautogui.click(321,  639);  time.sleep(0.20)   # 5
            pyautogui.click(220,  567);  time.sleep(0.20)   # 6
            pyautogui.click(310,  472);  time.sleep(0.25)   # 7
            pyautogui.click(418,  387);  time.sleep(0.30)   # 8
            pyautogui.click(508,  315);  time.sleep(0.20)   # 9
            pyautogui.click(585,  261);  time.sleep(0.20)   # 10
            pyautogui.click(674,  203);  time.sleep(0.20)   # 11

            # Balloons ────────────────────────────────────────────────────────
            pyautogui.click(354, 1113);  time.sleep(1.34)   # select
            pyautogui.click(259,  609);  time.sleep(0.30)   # 1
            pyautogui.click(359,  671);  time.sleep(0.25)   # 2
            pyautogui.click(420,  723);  time.sleep(0.25)   # 3

            # Archers ─────────────────────────────────────────────────────────
            pyautogui.click(549, 1097);  time.sleep(0.55)   # select
            pyautogui.click(214,  549);  time.sleep(0.30)   # 1

            # Stone Slammer ───────────────────────────────────────────────────
            pyautogui.click(681, 1087);  time.sleep(0.63)   # select
            pyautogui.click(211,  542);  time.sleep(0.30)   # 1

            # Heroes ──────────────────────────────────────────────────────────
            pyautogui.click(848, 1097);  time.sleep(0.82)   # Barbarian King select
            pyautogui.click(206,  544);  time.sleep(1.32)
            pyautogui.click(951, 1076);  time.sleep(0.84)   # Archer Queen select
            pyautogui.click(459,  341);  time.sleep(0.99)
            pyautogui.click(1099, 1063); time.sleep(0.84)   # Grand Warden select
            pyautogui.click(442,  730);  time.sleep(1.14)
            pyautogui.click(1239, 1095); time.sleep(0.85)   # Royal Champion select
            pyautogui.click(205,  552);  time.sleep(0.98)

            # Rage Spells ─────────────────────────────────────────────────────
            pyautogui.click(1371, 1121); time.sleep(0.82)   # select
            pyautogui.click(880,  689);  time.sleep(1.18)   # 1
            pyautogui.click(776,  594);  time.sleep(0.25)   # 2
            pyautogui.click(772,  492);  time.sleep(0.25)   # 3
            pyautogui.click(906,  448);  time.sleep(0.25)   # 4
            pyautogui.click(899,  545);  time.sleep(0.30)   # 5

            # Freeze Spell ────────────────────────────────────────────────────
            pyautogui.click(1538, 1111); time.sleep(1.11)   # select
            pyautogui.click(980,  555);  time.sleep(1.53)   # 1

            # Hero Abilities ──────────────────────────────────────────────────
            pyautogui.click(835,  1105); time.sleep(1.26)   # Barbarian King ability
            pyautogui.click(953,  1093); time.sleep(0.83)   # Archer Queen ability
            pyautogui.click(1111, 1098); time.sleep(0.50)   # Grand Warden ability
            pyautogui.click(1208, 1101); time.sleep(0.55)   # Royal Champion ability

            print("[OK] Troop deployment macro finished.")
            print("[INFO] Waiting for battle to end and Return Home to appear...\n")

        # Advance to next step after clicking
        current_step += 1
        time.sleep(2)

    time.sleep(0.5)   # poll interval

# ─── Done ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 54)
print("  [SUCCESS] Rank Battle attack completed!")
print("=" * 54)

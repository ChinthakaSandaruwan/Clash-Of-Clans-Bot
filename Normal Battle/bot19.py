import pyautogui
import os
import time
from pynput.mouse import Controller

# Bot19 - Mixed style: 6 left-side EDs (bot6 order: 6,7,8,9,10,11) then 5 right-side EDs (bot12/13: 7,8,9,10,11)
# Heroes from bot13 (right side), spells from bot13 (right side)
# All coordinates taken from existing bot1-bot14

pyautogui.FAILSAFE = True
mouse_ctrl = Controller()

image_sequence = [
    '(1)attack!.png',
    '(2)Find a Match 1700.png',
    '(3)Attack!.png',
    '(4)Return Home.png'
]

print("--- Clash of Clans Automated Bot (Single Run) ---")
print("Bot19 | Style: Left-Mid EDs then Right-Low EDs")
print("Searching for images in sequence...\n")

current_step = 0

while current_step < len(image_sequence):
    target_image = image_sequence[current_step]
    print(f"Searching: {target_image} (Step {current_step + 1}/{len(image_sequence)})", end="\r")

    try:
        location = pyautogui.locateOnScreen(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Images', target_image), confidence=0.8)

        if location is not None:
            print(f"\n[FOUND] {target_image}")
            center_point = pyautogui.center(location)

            pyautogui.click(center_point)
            print(f"[CLICK] Position: {center_point}")

            if target_image == '(3)Attack!.png':
                print("[INFO] Attack started. Zooming out...")
                time.sleep(1)

                screen_width, screen_height = pyautogui.size()
                center_x = screen_width // 2
                center_y = screen_height // 2

                pyautogui.moveTo(center_x, center_y, duration=0.3)
                time.sleep(0.5)

                for _ in range(15):
                    mouse_ctrl.scroll(0, -1)
                    time.sleep(0.05)
                time.sleep(1)

                print("\n[MACRO] Deploying troops...")
                time.sleep(10)

                # Electro Dragon Select (bot6 style)
                pyautogui.click(263, 1119)
                time.sleep(4.14)
                # --- Left side 6 EDs (bot6 order: starts at pos6) ---
                # 6 ED (bot1/6)
                pyautogui.click(220, 567)
                time.sleep(0.20)
                # 7 ED (bot1/6)
                pyautogui.click(310, 472)
                time.sleep(0.25)
                # 8 ED (bot1/6)
                pyautogui.click(418, 387)
                time.sleep(0.30)
                # 9 ED (bot1/6)
                pyautogui.click(508, 315)
                time.sleep(0.20)
                # 10 ED (bot1/6)
                pyautogui.click(585, 261)
                time.sleep(0.20)
                # 11 ED (bot1/6)
                pyautogui.click(674, 203)
                time.sleep(0.20)
                # --- Right side 5 EDs (bot12/13: pos 7-11) ---
                # 7 ED right (bot12/13)
                pyautogui.click(1728, 526)
                time.sleep(0.88)
                # 8 ED right (bot12/13)
                pyautogui.click(1766, 574)
                time.sleep(0.54)
                # 9 ED right (bot12/13)
                pyautogui.click(1670, 667)
                time.sleep(0.60)
                # 10 ED right (bot12/13)
                pyautogui.click(1579, 743)
                time.sleep(0.55)
                # 11 ED right (bot12/13)
                pyautogui.click(1500, 823)
                time.sleep(0.54)

                # Dragon Select (bot1)
                pyautogui.click(354, 1113)
                time.sleep(1.34)
                # Dragon Drop left top (bot1)
                pyautogui.click(674, 203)
                time.sleep(0.20)

                # Minion Select (bot1)
                pyautogui.click(549, 1097)
                time.sleep(0.55)
                # Minion Drop left (bot13)
                pyautogui.click(214, 549)
                time.sleep(0.30)

                # Vehicles right (bot13)
                pyautogui.click(704, 1080)
                time.sleep(1.19)
                pyautogui.click(1744, 587)
                time.sleep(1.09)

                # Royal Champion right (bot13)
                pyautogui.click(816, 1091)
                time.sleep(1.33)
                pyautogui.click(1491, 368)
                time.sleep(1.18)

                # Barbarian King right (bot13)
                pyautogui.click(955, 1080)
                time.sleep(0.89)
                pyautogui.click(1554, 775)
                time.sleep(1.02)

                # Archer Queen right (bot13)
                pyautogui.click(1108, 1067)
                time.sleep(0.90)
                pyautogui.click(1499, 370)
                time.sleep(1.02)

                # Grand Warden right (bot13)
                pyautogui.click(1229, 1053)
                time.sleep(0.99)
                pyautogui.click(1711, 538)
                time.sleep(1.05)

                # Rage Spells right (bot12/13)
                pyautogui.click(1393, 1100)
                time.sleep(1.02)
                pyautogui.click(1128, 780)
                time.sleep(1.35)
                pyautogui.click(1223, 627)
                time.sleep(0.63)
                pyautogui.click(1159, 519)
                time.sleep(0.54)
                pyautogui.click(1091, 438)
                time.sleep(0.49)
                pyautogui.click(1024, 574)
                time.sleep(0.30)

                # Freeze Spell right (bot12/13)
                pyautogui.click(1523, 1119)
                time.sleep(1.02)
                pyautogui.click(1007, 593)
                time.sleep(1.01)

                # Hero Abilities (bot13 style)
                pyautogui.click(1183, 1088)
                time.sleep(0.82)
                pyautogui.click(822, 1058)
                time.sleep(0.62)
                pyautogui.click(941, 1069)
                time.sleep(0.44)
                pyautogui.click(1102, 1079)
                time.sleep(0.46)

                print("[SUCCESS] Attack macro completed!\n")

            current_step += 1
            time.sleep(2)

    except pyautogui.ImageNotFoundException:
        pass
    except Exception as e:
        print(f"\n[ERROR] {e}")

    time.sleep(0.5)


# Check for Star Bonus Received popup
print("\n[INFO] Checking for Star Bonus Received window...")
star_bonus_image = '(0)Star Bonus Received.png'
star_bonus_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Images', star_bonus_image)

start_time = time.time()
found_star_bonus = False
while time.time() - start_time < 10:
    try:
        location = pyautogui.locateOnScreen(star_bonus_path, confidence=0.8)
        if location is not None:
            print("[FOUND] Star Bonus Received window found!")
            center_point = pyautogui.center(location)
            pyautogui.click(center_point)
            print(f"[CLICK] Clicked OK button at: {center_point}")
            found_star_bonus = True
            time.sleep(2)
            break
    except pyautogui.ImageNotFoundException:
        pass
    except Exception as e:
        print(f"[ERROR] Error checking for Star Bonus: {e}")
    time.sleep(0.5)

if not found_star_bonus:
    print("[INFO] No Star Bonus window detected within timeout.")

print("\n==========================================")
print("[SUCCESS] Attack completed successfully!")
print("Program will now exit.")
print("==========================================")

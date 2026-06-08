import pyautogui
import os
import time
from pynput.mouse import Controller

# Bot20 - Mixed style: Left-side EDs starting from pos5→1 (bottom up), then right-side EDs 1→5 (top-right)
# Heroes from bot13 right, spells left (bot1 style)
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
print("Bot20 | Style: Left Bottom-Up then Right Top-Down")
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

                # Electro Dragon Select (bot1)
                pyautogui.click(263, 1119)
                time.sleep(4.14)
                # --- Left side bottom→up: pos5 down to pos1 (bot1) ---
                # 5 ED left (bot1)
                pyautogui.click(321, 639)
                time.sleep(0.20)
                # 4 ED left (bot1)
                pyautogui.click(397, 706)
                time.sleep(0.25)
                # 3 ED left (bot1)
                pyautogui.click(478, 760)
                time.sleep(0.25)
                # 2 ED left (bot1)
                pyautogui.click(552, 841)
                time.sleep(0.25)
                # 1 ED left (bot1)
                pyautogui.click(639, 902)
                time.sleep(0.30)
                # --- Right side top→down: pos1 to pos6 (bot12/13) ---
                # 1 ED right (bot12/13)
                pyautogui.click(1256, 169)
                time.sleep(0.46)
                # 2 ED right (bot12/13)
                pyautogui.click(1345, 240)
                time.sleep(0.25)
                # 3 ED right (bot12/13)
                pyautogui.click(1436, 315)
                time.sleep(0.25)
                # 4 ED right (bot12/13)
                pyautogui.click(1506, 371)
                time.sleep(0.25)
                # 5 ED right (bot12/13)
                pyautogui.click(1577, 413)
                time.sleep(0.25)
                # 6 ED right (bot12/13)
                pyautogui.click(1668, 461)
                time.sleep(0.25)

                # Dragon Select (bot1)
                pyautogui.click(354, 1113)
                time.sleep(1.34)
                # Dragon Drop left top (bot1)
                pyautogui.click(674, 203)
                time.sleep(0.20)

                # Minion Select (bot1)
                pyautogui.click(549, 1097)
                time.sleep(0.55)
                # Minion Drop left (bot1)
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

                # Barbarian King left (bot1)
                pyautogui.click(955, 1080)
                time.sleep(0.89)
                pyautogui.click(206, 544)
                time.sleep(1.02)

                # Archer Queen left (bot1)
                pyautogui.click(1108, 1067)
                time.sleep(0.90)
                pyautogui.click(459, 341)
                time.sleep(1.02)

                # Grand Warden right (bot13)
                pyautogui.click(1229, 1053)
                time.sleep(0.99)
                pyautogui.click(1711, 538)
                time.sleep(1.05)

                # Rage Spells left (bot1)
                pyautogui.click(1371, 1121)
                time.sleep(0.82)
                pyautogui.click(880, 689)
                time.sleep(1.18)
                pyautogui.click(776, 594)
                time.sleep(0.25)
                pyautogui.click(772, 492)
                time.sleep(0.25)
                pyautogui.click(906, 448)
                time.sleep(0.25)
                pyautogui.click(899, 545)
                time.sleep(0.30)

                # Freeze Spell left (bot1)
                pyautogui.click(1538, 1111)
                time.sleep(1.11)
                pyautogui.click(980, 555)
                time.sleep(1.53)

                # Hero Abilities (bot1 style)
                pyautogui.click(835, 1105)
                time.sleep(1.26)
                pyautogui.click(953, 1093)
                time.sleep(0.83)
                pyautogui.click(1111, 1098)
                time.sleep(0.50)
                pyautogui.click(1208, 1101)
                time.sleep(0.55)

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

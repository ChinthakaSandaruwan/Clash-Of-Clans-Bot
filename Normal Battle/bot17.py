import pyautogui
import os
import time
from pynput.mouse import Controller

# Bot17 - Mixed style: All 11 right-side EDs (bot12/13), heroes from bot1 left side
# Spells from bot12/13 right side
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
print("Bot17 | Style: Full Right-Side EDs + Left Heroes")
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

                # Electro Dragon Select (from bot12/13)
                pyautogui.click(255, 1096)
                time.sleep(3.59)
                # 1 ED right-side (bot12/13) - reversed order vs bot12: start from bottom
                pyautogui.click(1500, 823)
                time.sleep(0.54)
                # 2 ED right-side
                pyautogui.click(1579, 743)
                time.sleep(0.55)
                # 3 ED right-side
                pyautogui.click(1670, 667)
                time.sleep(0.60)
                # 4 ED right-side
                pyautogui.click(1766, 574)
                time.sleep(0.54)
                # 5 ED right-side
                pyautogui.click(1728, 526)
                time.sleep(0.88)
                # 6 ED right-side
                pyautogui.click(1668, 461)
                time.sleep(0.58)
                # 7 ED right-side
                pyautogui.click(1577, 413)
                time.sleep(0.78)
                # 8 ED right-side
                pyautogui.click(1506, 371)
                time.sleep(0.47)
                # 9 ED right-side
                pyautogui.click(1436, 315)
                time.sleep(0.59)
                # 10 ED right-side
                pyautogui.click(1345, 240)
                time.sleep(0.69)
                # 11 ED right-side
                pyautogui.click(1256, 169)
                time.sleep(0.46)

                # Dragon Select (bot1)
                pyautogui.click(354, 1113)
                time.sleep(1.34)
                # Dragon Drop left-side (bot1)
                pyautogui.click(674, 203)
                time.sleep(0.20)

                # Minion Select (bot1)
                pyautogui.click(549, 1097)
                time.sleep(0.55)
                # Minion Drop left (bot1)
                pyautogui.click(214, 549)
                time.sleep(0.30)

                # Vehicles left (bot1)
                pyautogui.click(681, 1087)
                time.sleep(0.63)
                pyautogui.click(211, 542)
                time.sleep(0.30)

                # Barbarian King left (bot1)
                pyautogui.click(848, 1097)
                time.sleep(0.82)
                pyautogui.click(206, 544)
                time.sleep(1.32)

                # Archer Queen left (bot1)
                pyautogui.click(951, 1076)
                time.sleep(0.84)
                pyautogui.click(459, 341)
                time.sleep(0.99)

                # Grand Warden left (bot1)
                pyautogui.click(1099, 1063)
                time.sleep(0.84)
                pyautogui.click(442, 730)
                time.sleep(1.14)

                # Royal Champion left (bot1)
                pyautogui.click(1239, 1095)
                time.sleep(0.85)
                pyautogui.click(205, 552)
                time.sleep(0.98)

                # Rage Spells right-side (bot12/13)
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

                # Freeze Spell right-side (bot12/13)
                pyautogui.click(1523, 1119)
                time.sleep(1.02)
                pyautogui.click(1007, 593)
                time.sleep(1.01)

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

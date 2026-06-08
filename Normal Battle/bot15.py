import pyautogui
import os
import time
from pynput.mouse import Controller

# Bot15 - Mixed style: Start from ED11 down to ED6 (top-to-mid left), then right-side EDs 1-5
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
print("Bot15 | Style: Left-Top to Right Mix")
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

                # Electro Dragon Select (from bot1)
                pyautogui.click(263, 1119)
                time.sleep(4.14)
                # 11Electro Dragon Drop (bot1 pos 11 -> start from top)
                pyautogui.click(674, 203)
                time.sleep(0.20)
                # 10Electro Dragon Drop (bot1)
                pyautogui.click(585, 261)
                time.sleep(0.20)
                # 9Electro Dragon Drop (bot1)
                pyautogui.click(508, 315)
                time.sleep(0.20)
                # 8Electro Dragon Drop (bot1)
                pyautogui.click(418, 387)
                time.sleep(0.30)
                # 7Electro Dragon Drop (bot1)
                pyautogui.click(310, 472)
                time.sleep(0.25)
                # 6Electro Dragon Drop (bot1)
                pyautogui.click(220, 567)
                time.sleep(0.20)
                # Right-side 1 ED (bot12/13)
                pyautogui.click(1256, 169)
                time.sleep(0.30)
                # Right-side 2 ED (bot12/13)
                pyautogui.click(1345, 240)
                time.sleep(0.25)
                # Right-side 3 ED (bot12/13)
                pyautogui.click(1436, 315)
                time.sleep(0.25)
                # Right-side 4 ED (bot12/13)
                pyautogui.click(1506, 371)
                time.sleep(0.25)
                # Right-side 5 ED (bot12/13)
                pyautogui.click(1577, 413)
                time.sleep(0.25)

                # Dragon Select (bot1)
                pyautogui.click(354, 1113)
                time.sleep(1.34)
                # Dragon Drop (bot1)
                pyautogui.click(674, 203)
                time.sleep(0.20)

                # Minion Select (bot1)
                pyautogui.click(549, 1097)
                time.sleep(0.55)
                # Minion Drop (bot1)
                pyautogui.click(214, 549)
                time.sleep(0.30)

                # Vehicles (bot1)
                pyautogui.click(681, 1087)
                time.sleep(0.63)
                pyautogui.click(211, 542)
                time.sleep(0.30)

                # Barbarian King (bot1)
                pyautogui.click(848, 1097)
                time.sleep(0.82)
                pyautogui.click(206, 544)
                time.sleep(1.32)

                # Archer Queen (bot1)
                pyautogui.click(951, 1076)
                time.sleep(0.84)
                pyautogui.click(459, 341)
                time.sleep(0.99)

                # Grand Warden (bot1)
                pyautogui.click(1099, 1063)
                time.sleep(0.84)
                pyautogui.click(809, 66)
                time.sleep(0.17)

                # Royal Champion (bot1)
                pyautogui.click(1239, 1095)
                time.sleep(0.85)
                pyautogui.click(205, 552)
                time.sleep(0.98)

                # Rage Spells (bot12/13 side)
                pyautogui.click(1393, 1100)
                time.sleep(1.02)
                # Rege Spell Drop
                pyautogui.click(671, 422)
                time.sleep(3.94)

                pyautogui.click(796, 314)
                time.sleep(1.02)

                pyautogui.click(941, 268)
                time.sleep(1.01)

                pyautogui.click(1063, 330)
                time.sleep(0.87)

                pyautogui.click(1139, 405)
                time.sleep(1.07)


                # Freeze Spell (bot12/13)
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

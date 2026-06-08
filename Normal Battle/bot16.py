import pyautogui
import os
import time
from pynput.mouse import Controller

# Bot16 - Mixed style: Right-side EDs 6-11 first, then left-side EDs 1-5
# All coordinates taken from existing bot12/13 and bot1

pyautogui.FAILSAFE = True
mouse_ctrl = Controller()

image_sequence = [
    '(1)attack!.png',
    '(2)Find a Match 1700.png',
    '(3)Attack!.png',
    '(4)Return Home.png'
]

print("--- Clash of Clans Automated Bot (Single Run) ---")
print("Bot16 | Style: Right-Mid then Left-Low Mix")
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
                # Right-side 6 ED (bot12/13)
                pyautogui.click(1668, 461)
                time.sleep(0.58)
                # Right-side 7 ED (bot12/13)
                pyautogui.click(1728, 526)
                time.sleep(0.88)
                # Right-side 8 ED (bot12/13)
                pyautogui.click(1766, 574)
                time.sleep(0.54)
                # Right-side 9 ED (bot12/13)
                pyautogui.click(1670, 667)
                time.sleep(0.60)
                # Right-side 10 ED (bot12/13)
                pyautogui.click(1579, 743)
                time.sleep(0.55)
                # Right-side 11 ED (bot12/13)
                pyautogui.click(1500, 823)
                time.sleep(0.54)
                # Left-side 1 ED (bot1)
                pyautogui.click(639, 902)
                time.sleep(0.30)
                # Left-side 2 ED (bot1)
                pyautogui.click(552, 841)
                time.sleep(0.25)
                # Left-side 3 ED (bot1)
                pyautogui.click(478, 760)
                time.sleep(0.25)
                # Left-side 4 ED (bot1)
                pyautogui.click(397, 706)
                time.sleep(0.25)
                # Left-side 5 ED (bot1)
                pyautogui.click(321, 639)
                time.sleep(0.20)

                # Dragon Select (bot1)
                pyautogui.click(354, 1113)
                time.sleep(1.34)
                # Dragon Drop (bot12/13)
                pyautogui.click(674, 203)
                time.sleep(0.20)

                # Minion Select (bot1)
                pyautogui.click(549, 1097)
                time.sleep(0.55)
                # Minion Drop (bot1)
                pyautogui.click(214, 549)
                time.sleep(0.30)

                # Vehicles (bot13 right-side)
                pyautogui.click(704, 1080)
                time.sleep(1.19)
                pyautogui.click(1744, 587)
                time.sleep(1.09)

                # Royal Champion (bot13)
                pyautogui.click(816, 1091)
                time.sleep(1.33)
                pyautogui.click(1491, 368)
                time.sleep(1.18)

                # Barbarian King (bot13)
                pyautogui.click(955, 1080)
                time.sleep(0.89)
                pyautogui.click(1554, 775)
                time.sleep(1.02)

                # Archer Queen (bot13)
                pyautogui.click(1108, 1067)
                time.sleep(0.90)
                pyautogui.click(1499, 370)
                time.sleep(1.02)

                # Grand Warden (bot13)
                pyautogui.click(1229, 1053)
                time.sleep(0.99)
                pyautogui.click(1711, 538)
                time.sleep(1.05)

                # Rage Spells (bot1 side)
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

                # Freeze Spell (bot1)
                pyautogui.click(1538, 1111)
                time.sleep(1.11)
                pyautogui.click(980, 555)
                time.sleep(1.53)

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

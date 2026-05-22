import pyautogui
import os
import time
from pynput.mouse import Controller

pyautogui.FAILSAFE = True
mouse_ctrl = Controller()

image_sequence = [
    '(1)attack!.png',
    '(2)Find a Match 1700.png',
    '(3)Attack!.png',
    '(4)Return Home.png'
]

print("--- Clash of Clans Automated Bot (Single Run) ---")
print("Searching for images in sequence...\n")

current_step = 0

while current_step < len(image_sequence):
    target_image = image_sequence[current_step]
    print(f"Searching: {target_image} (Step {current_step + 1}/{len(image_sequence)})", end="\r")

    try:
        location = pyautogui.locateOnScreen(os.path.join(os.path.dirname(os.path.abspath(__file__)), target_image), confidence=0.8)
        
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
                
                # Electro Dragon Select
                pyautogui.click(263, 1119)
                time.sleep(4.14)
                # 8Electro Dragon Drop
                pyautogui.click(418, 387)
                time.sleep(0.30)
                # 9Electro Dragon Drop
                pyautogui.click(508, 315)
                time.sleep(0.20)
                # 10Electro Dragon Drop
                pyautogui.click(585, 261)
                time.sleep(0.20)
                # 11Electro Dragon Drop
                pyautogui.click(674, 203)
                time.sleep(0.20)
                # 1Electro Dragon Drop
                pyautogui.click(639, 902)
                time.sleep(0.30)
                # 2Electro Dragon Drop
                pyautogui.click(552, 841)
                time.sleep(0.25)
                # 3Electro Dragon Drop
                pyautogui.click(478, 760)
                time.sleep(0.25)
                # 4Electro Dragon Drop
                pyautogui.click(397, 706)
                time.sleep(0.25)
                # 5Electro Dragon Drop
                pyautogui.click(321, 639)
                time.sleep(0.20)
                # 6Electro Dragon Drop
                pyautogui.click(220, 567)
                time.sleep(0.20)
                # 7Electro Dragon Drop
                pyautogui.click(310, 472)
                time.sleep(0.25)

                # Balloons
                pyautogui.click(354, 1113)
                time.sleep(1.34)
                pyautogui.click(259, 609)
                time.sleep(0.30)
                pyautogui.click(359, 671)
                time.sleep(0.25)
                pyautogui.click(420, 723)
                time.sleep(0.25)

                # Archers
                pyautogui.click(549, 1097)
                time.sleep(0.55)
                pyautogui.click(214, 549)
                time.sleep(0.30)

                # Vehicles
                pyautogui.click(681, 1087)
                time.sleep(0.63)
                pyautogui.click(211, 542)
                time.sleep(0.30)

                # Archer Queen
                pyautogui.click(951, 1076)
                time.sleep(0.84)
                pyautogui.click(459, 341)
                time.sleep(0.99)

                # Barbarian King
                pyautogui.click(848, 1097)
                time.sleep(0.82)
                pyautogui.click(206, 544)
                time.sleep(1.32)

                # Royal Champion
                pyautogui.click(1239, 1095)
                time.sleep(0.85)
                pyautogui.click(205, 552)
                time.sleep(0.98)

                # Grand Warden
                pyautogui.click(1099, 1063)
                time.sleep(0.84)
                pyautogui.click(442, 730)
                time.sleep(1.14)

                # Rage Spells
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

                # Freeze Spell
                pyautogui.click(1538, 1111)
                time.sleep(1.11)
                pyautogui.click(980, 555)
                time.sleep(1.53)

                # Hero Abilities
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

print("\n==========================================")
print("[SUCCESS] Attack completed successfully!")
print("Program will now exit.")
print("==========================================")
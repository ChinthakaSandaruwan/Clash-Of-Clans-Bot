import pyautogui
import time
from pynput.mouse import Controller

# Mouse එක screen එකේ කොනකට වේගයෙන් ගියොත් bot එක නැවතීමේ safety feature එක
pyautogui.FAILSAFE = True

# pynput mouse controller එකක් සාදා ගැනීම (Scroll කිරීම සඳහා)
mouse_ctrl = Controller()

# ඔබ ලබාදුන් පින්තූරවල නම් නිවැරදිව පිළිවෙලට මෙහි ඇතුළත් කර ඇත
image_sequence = [
    '(1)attack!.png',             # පියවර 1
    '(2)Find a Match 1700.png',   # පියවර 2
    '(3)Attack!.png',             # පියවර 3 (මීට පසු Zoom Out සහ Attack Macro එක සිදුවේ)
    '(4)Return Home.png'          # පියවර 4
]

print("--- Clash of Clans Fully Automated Bot ආරම්භ වුණා ---")
print("පින්තූර පිළිවෙලට පරීක්ෂා කරමින් පවතී...\n")

current_step = 0  # ආරම්භක පියවර 

while True:
    # සියලුම පියවර අවසන් වූ පසු නැවත පළමු පියවරට (Loop) මාරු වේ
    if current_step >= len(image_sequence):
        print("\n==========================================")
        print("[SUCCESS] සියලුම Attack පියවරවල් සාර්ථකව අවසන්!")
        print("නැවත මුල සිට (පළමු පියවරේ සිට) ආරම්භ වේ...")
        print("==========================================\n")
        current_step = 0
        time.sleep(3)

    target_image = image_sequence[current_step]
    print(f"සොයමින් පවතී: {target_image} (පියවර {current_step + 1}/{len(image_sequence)})", end="\r")

    try:
        # Screen එක මත අදාළ පියවරේ පින්තූරය තිබේදැයි බලයි
        location = pyautogui.locateOnScreen(target_image, confidence=0.8)
        
        if location is not None:
            print(f"\n[FOUND] {target_image} රූපය Screen එක මත හමු වුණා!")
            center_point = pyautogui.center(location)
            
            # මූසිකය අදාළ ස්ථානයට ගෙන ගොස් ක්ලික් කරයි
            pyautogui.click(center_point)
            print(f"[CLICK] Click කළ ස්ථානය: {center_point}")
            
            # 🌟 විශේෂ ක්‍රියාවලිය: පියවර 3 (Attack!) ක්ලික් කළාට පසු සිදුවන දේ
            if target_image == '(3)Attack!.png':
                print("[INFO] Attack එක ආරම්භ වුණා. සිතියම Zoom Out කිරීමට සූදානම් වේ...")
                time.sleep(1) # Attack එක load වීමට තත්පර 1ක් නවතී
                
                # 1. Screen එකේ හරියටම මැද Coordinates සොයා ගැනීම
                screen_width, screen_height = pyautogui.size()
                center_x = screen_width // 2
                center_y = screen_height // 2
                
                # 2. Mouse එක Screen එකේ මැදටම ගෙන යාම
                pyautogui.moveTo(center_x, center_y, duration=0.3)
                print(f"[MOVE] Mouse එක Screen මධ්‍යයට ගෙන ගියා: ({center_x}, {center_y})")
                time.sleep(0.5)
                
                # 3. දිගු Scroll Out (Zoom Out) එකක් සිදු කිරීම
                print("[SCROLL] දිගු Zoom Out එකක් සිදු කරයි...")
                for _ in range(15):
                    mouse_ctrl.scroll(0, -1)
                    time.sleep(0.05)
                print("[SUCCESS] Zoom Out එක සාර්ථකයි!")
                time.sleep(1)
                
                # ⚔️ 4. ඔබ ලබාදුන් සැබෑ Attack (Troop Deploy) Macro එක ආරම්භ කිරීම
                print("\n🚀 [MACRO] භටයින් සිතියමට මුදා හැරීම (Troop Deployment) ආරම්භ කළා...")
                
                
                
                #Electro Dragons
                #Electro Dragon Select   
                pyautogui.click(263, 1119)
                time.sleep(4.14)
                #7Electro Dragon Drop
                pyautogui.click(310, 472)
                time.sleep(0.25)
                #8Electro Dragon Drop
                pyautogui.click(418, 387)
                time.sleep(0.30)
                #9Electro Dragon Drop
                pyautogui.click(508, 315)
                time.sleep(0.20)
                #10Electro Dragon Drop
                pyautogui.click(585, 261)
                time.sleep(0.20)
                #11Electro Dragon Drop
                pyautogui.click(674, 203)
                time.sleep(0.20)
                 #1Electro Dragon Drop
                pyautogui.click(639, 902)
                time.sleep(0.30)
                #2Electro Dragon Drop
                pyautogui.click(552, 841)
                time.sleep(0.25)
                #3Electro Dragon Drop
                pyautogui.click(478, 760)
                time.sleep(0.25)
                #4Electro Dragon Drop
                pyautogui.click(397, 706)
                time.sleep(0.25)
                #5Electro Dragon Drop
                pyautogui.click(321, 639)
                time.sleep(0.20)
                #6Electro Dragon Drop
                pyautogui.click(220, 567)
                time.sleep(0.20)

                #Balloons
                #Balloon Select
                pyautogui.click(354, 1113)
                time.sleep(1.34)
                #1Balloon Drop
                pyautogui.click(259, 609)
                time.sleep(0.30)
                #2Balloon Drop
                pyautogui.click(359, 671)
                time.sleep(0.25)
                #3Balloon Drop
                pyautogui.click(420, 723)
                time.sleep(0.25)

                #Archers
                #Archer Select
                pyautogui.click(549, 1097)
                time.sleep(0.55)
                #1Archer Drop
                pyautogui.click(214, 549)
                time.sleep(0.30)

                #Vehicles
                #Stone Slammer Select
                pyautogui.click(681, 1087)
                time.sleep(0.63)
                #1Stone Slammer Drop
                pyautogui.click(211, 542)
                time.sleep(0.30)

                #Barbarian King Select
                pyautogui.click(848, 1097)
                time.sleep(0.82)
                #Barbarian King Drop
                pyautogui.click(206, 544)
                time.sleep(1.32)

                #Archer Queen Select
                pyautogui.click(951, 1076)
                time.sleep(0.84)
                #Archer Queen Drop
                pyautogui.click(459, 341)
                time.sleep(0.99)

                #Grand Warden Select
                pyautogui.click(1099, 1063)
                time.sleep(0.84)
                #Grand Warden Drop
                pyautogui.click(442, 730)
                time.sleep(1.14)

                #Royal Champion Select
                pyautogui.click(1239, 1095)
                time.sleep(0.85)
                #Royal Champion Drop
                pyautogui.click(205, 552)
                time.sleep(0.98)

                #Rage Spell Select
                pyautogui.click(1371, 1121)
                time.sleep(0.82)
                #1Rage Spell Drop
                pyautogui.click(880, 689)
                time.sleep(1.18)
                #2Rage Spell Drop
                pyautogui.click(776, 594)
                time.sleep(0.25)
                #3Rage Spell Drop
                pyautogui.click(772, 492)
                time.sleep(0.25)
                #4Rage Spell Drop
                pyautogui.click(906, 448)
                time.sleep(0.25)
                #5Rage Spell Drop
                pyautogui.click(899, 545)
                time.sleep(0.30)

                #Freeze Spell Select
                pyautogui.click(1538, 1111)
                time.sleep(1.11)
                #1Freeze Spell Drop
                pyautogui.click(980, 555)
                time.sleep(1.53)

                #Barbarian King Ability
                pyautogui.click(835, 1105)
                time.sleep(1.26)
                #Archer Queen Ability
                pyautogui.click(953, 1093)
                time.sleep(0.83)
                #Grand Warden Ability
                pyautogui.click(1111, 1098)
                time.sleep(0.50)
                #Royal Champion Ability
                pyautogui.click(1208, 1101)
                time.sleep(0.55)
                
                
                
                
                
                
                
                
                
                print("[SUCCESS] Attack Macro එක අවසන් වුණා. දැන් Return Home Button එක එනතුරු බලන් සිටී...\n")
            
            # සාර්ථකව ක්ලික් වූ (සහ Macro එක අවසන් වූ) පසු ඊළඟ පියවරට (Next Step) යයි
            current_step += 1
            time.sleep(2)
            
    except pyautogui.ImageNotFoundException:
        pass
    except Exception as e:
        print(f"\n[ERROR] බලාපොරොත්තු නොවූ දෝෂයක්: {e}")
        
    time.sleep(0.5)

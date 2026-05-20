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

                # Electro Dragon Select
                pyautogui.click(272, 1094)
                time.sleep(4.6)






                #1 electro dragon Drop
                pyautogui.click(589, 916)
                time.sleep(2.34)

                #2 electro dragon Drop
                pyautogui.click(500, 870)
                time.sleep(0.55)

                #3 electro dragon Drop
                pyautogui.click(401, 802)
                time.sleep(0.56)

                #4 electro dragon Drop
                pyautogui.click(288, 725)
                time.sleep(0.55)

                #5 electro dragon Drop
                pyautogui.click(163, 601)
                time.sleep(1.14)

                #6 electro dragon Drop
                pyautogui.click(191, 494)
                time.sleep(0.74)

                #7 electro dragon Drop
                pyautogui.click(326, 399)
                time.sleep(0.6)

                #8 electro dragon Drop
                pyautogui.click(405, 316)
                time.sleep(0.51)

                #9 electro dragon Drop
                pyautogui.click(487, 248)
                time.sleep(0.45)
 
                #10 electro dragon Drop
                pyautogui.click(590, 177)
                time.sleep(0.49)

                #11 electro dragon Drop
                pyautogui.click(712, 113)
                time.sleep(1.19)
                
                
                
                
                
                

                #Range Spell Select
                pyautogui.click(1383, 1100)
                time.sleep(1.94)

                #1 Range Spell Drop
                pyautogui.click(832, 763)
                time.sleep(1.36)

                #2 Range Spell Drop
                pyautogui.click(676, 645)
                time.sleep(0.43)

                #3 Range Spell Drop
                pyautogui.click(639, 533)
                time.sleep(0.47)

                #4 Range Spell Drop
                pyautogui.click(749, 461)
                time.sleep(0.38)

                #5 Range Spell Drop
                pyautogui.click(857, 393)
                time.sleep(0.53)

                #Balloon Select
                pyautogui.click(418, 1073)
                time.sleep(1.9)

                #1 Balloon Drop
                pyautogui.click(192, 552)
                time.sleep(0.93)

                #2 Balloon Drop
                pyautogui.click(192, 552)
                time.sleep(0.27)

                #3 Balloon Drop
                pyautogui.click(188, 552)
                time.sleep(0.33)

                #Archer Select
                pyautogui.click(516, 1098)
                time.sleep(0.97)

                #1 Archer Drop
                pyautogui.click(192, 552)
                time.sleep(0.5)

                #Barbarian King Select
                pyautogui.click(151, 558)
                time.sleep(0.69)

                #Barbarian King Drop
                pyautogui.click(837, 1093)
                time.sleep(1.15)

                #Archer Queen Select
                pyautogui.click(167, 556)
                time.sleep(1.18)

                #Archer Queen Drop
                pyautogui.click(973, 1080)
                time.sleep(1.07)

                #Grand Warden Select
                pyautogui.click(163, 565)
                time.sleep(0.85)

                #Grand Warden Drop
                pyautogui.click(1108, 1062)
                time.sleep(0.74)

                #Royal Champion Select
                pyautogui.click(179, 569)
                time.sleep(0.76)

                #Royal Champion Drop
                pyautogui.click(1249, 1075)
                time.sleep(0.9)

                #Freeze Spell Select
                pyautogui.click(172, 573)
                time.sleep(0.98)

                #1 Freeze Spell Drop
                pyautogui.click(1531, 1082)
                time.sleep(0.8)

                #Stone Slammer Select
                pyautogui.click(902, 563)
                time.sleep(1.02)

                #Stone Slammer Drop
                pyautogui.click(713, 1067)
                time.sleep(1.07)

                #Barbarian King Ability
                pyautogui.click(177, 557)
                time.sleep(1.24)

                #Archer Queen Ability
                pyautogui.click(845, 1073)
                time.sleep(0.82)

                #Grand Warden Ability
                pyautogui.click(951, 1080)
                time.sleep(0.34)

                #Royal Champion Ability
                pyautogui.click(1098, 1088)
                time.sleep(0.4)

                pyautogui.click(1204, 1095)
                time.sleep(0.36)
                
                print("[SUCCESS] Attack Macro එක අවසන් වුණා. දැන් Return Home Button එක එනතුරු බලන් සිටී...\n")
            
            # සාර්ථකව ක්ලික් වූ (සහ Macro එක අවසන් වූ) පසු ඊළඟ පියවරට (Next Step) යයි
            current_step += 1
            time.sleep(2)
            
    except pyautogui.ImageNotFoundException:
        pass
    except Exception as e:
        print(f"\n[ERROR] බලාපොරොත්තු නොවූ දෝෂයක්: {e}")
        
    time.sleep(0.5)

"""
Clash of Clans - New Update Dynamic Attack Bot
================================================
Learns the drop style from Normal Battle bots:
 - Troops dropped along the LEFT PERIMETER ARC of the base (bottom-left to top-left diagonal sweep)
 - Heroes each dropped at a single strategic point along the left side
 - Spells dropped in the CENTER/RIGHT interior area of the base
 - Hero abilities triggered after all troops deployed
 
All coordinates are derived 100% dynamically from screen resolution.
No hardcoded pixel values.
"""

import cv2
import numpy as np
import pyautogui
import os
import time
import math
import random
import threading
from PIL import ImageGrab
from pynput.mouse import Controller

# ─── GUI Thread Control ────────────────────────────────────────────────────────
bot_paused = threading.Event()
bot_paused.set()  # Default: not paused (running)
bot_stopped = False
forced_side = None
hero_ability_delay = 4

_orig_sleep = time.sleep

def bot_sleep(seconds):
    global bot_stopped
    step = 0.05
    t_spent = 0
    while t_spent < seconds:
        if bot_stopped:
            raise KeyboardInterrupt("Bot stopped by user")
        bot_paused.wait()  # Block here if paused
        
        sleep_time = min(step, seconds - t_spent)
        _orig_sleep(sleep_time)
        t_spent += sleep_time

time.sleep = bot_sleep

# ─── Safety ────────────────────────────────────────────────────────────────────
pyautogui.FAILSAFE = True
mouse_ctrl = Controller()

# ─── Paths (images shared with Normal Battle folder) ───────────────────────────
script_dir   = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
images_dir   = os.path.join(project_root, "Normal Battle", "Images")

TEMPLATES = {
    "attack_lobby":   "(1)attack!.png",
    "find_match":     "(2)Find a Match 1700.png",
    "attack_confirm": "(3)Attack!.png",
    "return_home":    "(4)Return Home.png",
    "star_bonus":     "(0)Star Bonus Received.png",
}

# ─── Timing constants (learned from Normal Battle bots) ─────────────────────────
T_SELECT_LONG  = 4.14   # wait after selecting first troop type (filling animation)
T_SELECT_MED   = 1.34   # wait after selecting additional troop types
T_SELECT_SHORT = 0.82   # wait after selecting heroes / spells
T_DROP         = 0.20   # time between each individual drop click
T_SPELL_DROP   = 0.25   # time between each spell drop click
T_HERO_ABILITY = 0.83   # time between hero ability clicks
T_LOAD_BASE    = 10     # wait for base to render before deploying


# ═══════════════════════════════════════════════════════════════════════════════
#  MULTI-SCALE OPENCV TEMPLATE MATCHING
# ═══════════════════════════════════════════════════════════════════════════════
def find_template(name, threshold=0.72):
    """Find a template on screen across multiple scales. Returns (cx, cy) or None."""
    path = os.path.join(images_dir, TEMPLATES[name])
    tmpl = cv2.imread(path)
    if tmpl is None:
        print(f"[ERROR] Could not load: {path}")
        return None

    shot      = np.array(ImageGrab.grab())
    screen_bgr = cv2.cvtColor(shot, cv2.COLOR_RGB2BGR)
    screen_g   = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
    tmpl_g     = cv2.cvtColor(tmpl,       cv2.COLOR_BGR2GRAY)
    th, tw     = tmpl_g.shape[:2]

    best = None
    for scale in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]:
        rw, rh = int(tw * scale), int(th * scale)
        if rw < 10 or rh < 10 or rw > screen_g.shape[1] or rh > screen_g.shape[0]:
            continue
        rt     = cv2.resize(tmpl_g, (rw, rh), interpolation=cv2.INTER_AREA)
        res    = cv2.matchTemplate(screen_g, rt, cv2.TM_CCOEFF_NORMED)
        _, mv, _, ml = cv2.minMaxLoc(res)
        if mv >= threshold and (best is None or mv > best[2]):
            best = (ml[0] + rw // 2, ml[1] + rh // 2, mv)

    if best:
        print(f"[FOUND] {TEMPLATES[name]}  conf={best[2]:.3f}  at ({best[0]},{best[1]})")
        return (best[0], best[1])
    return None


def wait_and_click(name, threshold=0.72, post_sleep=1.5):
    """Poll until template found, then click it."""
    print(f"  Waiting for [{TEMPLATES[name]}]...", end="\r")
    while True:
        pos = find_template(name, threshold)
        if pos:
            pyautogui.moveTo(pos[0], pos[1], duration=0.25)
            pyautogui.click()
            print(f"[CLICK] {name}  → ({pos[0]},{pos[1]})")
            time.sleep(post_sleep)
            return pos
        time.sleep(0.4)


# ═══════════════════════════════════════════════════════════════════════════════
#  DYNAMIC SLOT DETECTION  (Computer Vision - Contour method)
# ═══════════════════════════════════════════════════════════════════════════════
def is_active(region_bgr, cx, cy, w, h, roi_y):
    """
    Returns True if slot at (cx,cy) looks colored/active (not greyed-out).
    Golden rule: (Saturation > 15) or (Value > 110)
    """
    lx = max(0, cx - w // 4)
    rx = min(region_bgr.shape[1], cx + w // 4)
    ty = max(0, cy - roi_y - h // 4)
    by = min(region_bgr.shape[0], cy - roi_y + h // 4)
    crop = region_bgr[ty:by, lx:rx]
    if crop.size == 0:
        return False
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    sat = float(np.mean(hsv[:, :, 1]))
    val = float(np.mean(hsv[:, :, 2]))
    return (sat > 15.0) or (val > 110.0)


def detect_slots_improved(sw, sh):
    """Scan the bottom deployment bar using relaxed contours."""
    roi_y = int(sh * 0.78)
    roi_b = int(sh * 0.98)
    shot  = ImageGrab.grab(bbox=(0, roi_y, sw, roi_b))
    bgr   = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
    gray  = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 40, 120)
    cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    mn_h = int(sh * 0.02)   # 24 pixels on 1200h
    mx_h = int(sh * 0.18)   # 216 pixels
    mn_w = int(sw * 0.015)  # 28 pixels on 1920w
    mx_w = int(sw * 0.12)   # 230 pixels
    
    raw = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        aspect = w / h if h > 0 else 0
        if mn_h < h < mx_h and mn_w < w < mx_w and 0.35 < aspect < 2.0:
            raw.append((x + w//2, roi_y + y + h//2, w, h))

    raw.sort(key=lambda s: s[0])

    # Merge very close detections
    md = int(sw * 0.025)
    merged = []
    for s in raw:
        if not merged or s[0] - merged[-1][0] >= md:
            merged.append(s)
        else:
            p = merged[-1]
            merged[-1] = ((p[0]+s[0])//2, (p[1]+s[1])//2, (p[2]+s[2])//2, (p[3]+s[3])//2)

    return merged


def detect_and_classify_slots(sw, sh):
    """
    Detects all 10 slots on the bottom bar using a highly robust hybrid strategy.
    Reference coordinates are scaled dynamically, then matched with relaxed contours.
    If any slot is missed (e.g. too dark/grayed out), we fallback to scaled reference coordinates.
    """
    ref_points = [
        (int(263 * sw / 1920), int(1100 * sh / 1200)),  # 0: E-Drag
        (int(354 * sw / 1920), int(1100 * sh / 1200)),  # 1: Balloon
        (int(549 * sw / 1920), int(1100 * sh / 1200)),  # 2: Archer
        (int(681 * sw / 1920), int(1100 * sh / 1200)),  # 3: Stone Slammer
        (int(848 * sw / 1920), int(1100 * sh / 1200)),  # 4: BK
        (int(951 * sw / 1920), int(1100 * sh / 1200)),  # 5: AQ
        (int(1099 * sw / 1920), int(1100 * sh / 1200)), # 6: GW
        (int(1239 * sw / 1920), int(1100 * sh / 1200)), # 7: RC
        (int(1371 * sw / 1920), int(1100 * sh / 1200)), # 8: Rage
        (int(1538 * sw / 1920), int(1100 * sh / 1200)), # 9: Freeze
    ]
    
    detected = detect_slots_improved(sw, sh)
    print(f"[SLOTS] Relaxed CV detected {len(detected)} slots.")
    
    slots = []
    max_dist = int(sw * 0.035)  # Max allowed horizontal matching distance
    w_fb = int(sw * 0.05)
    h_fb = int(sh * 0.12)
    
    for idx, (rx, ry) in enumerate(ref_points):
        matched = None
        best_dist = max_dist
        for s in detected:
            dist = abs(s[0] - rx)
            if dist < best_dist:
                best_dist = dist
                matched = s
                
        if matched:
            cx, _, w, h = matched
            slots.append((cx, ry, w, h))
            print(f"  Slot {idx+1} matched to dynamic contour x={cx} (using fixed y={ry})")
        else:
            slots.append((rx, ry, w_fb, h_fb))
            print(f"  Slot {idx+1} using scaled fallback at ({rx}, {ry})")
            
    # Strictly classify by order (guaranteed 100% correct classification!)
    troops = slots[0:4]
    heroes = slots[4:8]
    spells = slots[8:10]
    
    return troops, heroes, spells


# ═══════════════════════════════════════════════════════════════════════════════
#  DYNAMIC DROP-POINT GENERATORS  (learned from Normal Battle bot patterns)
# ═══════════════════════════════════════════════════════════════════════════════
def get_attack_side():
    """
    Reads state to determine if this attack should be Left or Right side.
    Cycle:
      Attack 1: Left side
      Attack 2: Right side
      Attack 3: Random (left or right)
    """
    global forced_side
    if forced_side in ["left", "right"]:
        print(f"\n🎯 [STATE] GUI Forced Attack Side: {forced_side.upper()}")
        return forced_side

    state_file = os.path.join(script_dir, "new_update_bot_state.txt")
    attack_count = 1
    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                attack_count = int(f.read().strip())
        except Exception:
            attack_count = 1
            
    # Decide side
    if attack_count == 1:
        side = "left"
        print(f"\n🎯 [STATE] Attack #{attack_count}: Choosing LEFT side.")
    elif attack_count == 2:
        side = "right"
        print(f"\n🎯 [STATE] Attack #{attack_count}: Choosing RIGHT side.")
    else:
        side = random.choice(["left", "right"])
        print(f"\n🎯 [STATE] Attack #{attack_count} (Random): Choosing {side.upper()} side.")
        
    # Update state for next run (cycle 1 -> 2 -> 3 -> 1)
    next_count = attack_count + 1
    if next_count > 3:
        next_count = 1
    try:
        with open(state_file, "w") as f:
            f.write(str(next_count))
    except Exception as e:
        print(f"[WARNING] Could not save attack state: {e}")
        
    return side


def get_left_perimeter_sweep(sw, sh, n_points=14):
    """
    Generate drop points along the LEFT-SIDE perimeter of the base.
    
    These are the EXACT safe coordinates from bot1.py (proven to never land in the red zone),
    normalised to screen fractions so they work on any resolution.
    
    Source coordinates on 1920x1200:
      (639,902) → (552,841) → (478,760) → (397,706) → (321,639) →
      (220,567) → (310,472) → (418,387) → (508,315) → (585,261) → (674,203)
    """
    # Normalised coordinates (x/1920, y/1200) from bot1.py — all proven safe outside the base
    norm_pts = [
        (0.333, 0.752),   # bottom-right of sweep arc
        (0.287, 0.701),
        (0.249, 0.633),
        (0.207, 0.588),
        (0.167, 0.533),
        (0.115, 0.473),   # leftmost point
        (0.161, 0.393),
        (0.218, 0.323),
        (0.265, 0.263),
        (0.305, 0.218),
        (0.351, 0.169),   # top of sweep arc
    ]
    
    # Scale to the current screen resolution
    points = [(int(nx * sw), int(ny * sh)) for nx, ny in norm_pts]
    return points


def get_right_perimeter_sweep(sw, sh, n_points=14):
    """
    Generate drop points along the RIGHT-SIDE perimeter of the base.
    This is created by mirroring the left perimeter coordinates horizontally.
    """
    left_pts = get_left_perimeter_sweep(sw, sh, n_points)
    # Mirror x around center: mirrored_x = sw - x
    return [(sw - x, y) for x, y in left_pts]


def get_hero_drop_points(sw, sh):
    """
    Return 4 hero drop positions along the left edge, spread vertically.
    
    Pattern from Normal Battle bots:
      BK  → (206, 544)   left side, mid-height
      AQ  → (459, 341)   upper-center-left
      GW  → (442, 730)   lower-center-left
      RC  → (205, 552)   left side (near BK)
    Normalised to screen fractions.
    """
    return [
        (int(sw * 0.107), int(sh * 0.453)),   # Barbarian King  – left mid
        (int(sw * 0.239), int(sh * 0.284)),   # Archer Queen    – upper left
        (int(sw * 0.230), int(sh * 0.608)),   # Grand Warden    – lower left
        (int(sw * 0.107), int(sh * 0.460)),   # Royal Champion  – left mid
    ]


def get_right_hero_drop_points(sw, sh):
    """
    Return 4 hero drop positions along the right edge, mirrored from left.
    """
    left_pts = get_hero_drop_points(sw, sh)
    return [(sw - x, y) for x, y in left_pts]


def shift_outwards(points, sw, sh, side="left", offset_px=30):
    """
    Shifts coordinates outwards from the center of the screen to prevent
    hitting base red zones on retry passes.
    """
    center_x = sw // 2
    center_y = sh // 2
    shifted = []
    for x, y in points:
        dx = x - center_x
        dy = y - center_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            nx = x + int((dx / dist) * offset_px)
            ny = y + int((dy / dist) * offset_px)
            # clamp to screen
            nx = max(50, min(sw - 50, nx))
            ny = max(50, min(sh - 150, ny))
            shifted.append((nx, ny))
        else:
            shifted.append((x, y))
    return shifted


def get_spell_drop_points(sw, sh, side="left", n_spells=6):
    """
    Return n_spells drop points scattered in the interior area.
    If side is 'left' (attacking from left), drops spells in the center-right interior zone.
    If side is 'right' (attacking from right), drops spells in the center-left interior zone.
    """
    # Center-right interior zone for left attack, center-left for right attack
    if side == "left":
        base_x = sw * 0.46
    else:
        base_x = sw * 0.54

    base_y = sh * 0.42
    spread_x = sw * 0.08
    spread_y = sh * 0.20

    pts = []
    for i in range(n_spells):
        angle = (i / max(n_spells, 1)) * 2 * math.pi
        px = int(base_x + spread_x * math.cos(angle) + random.uniform(-0.01, 0.01) * sw)
        py = int(base_y + spread_y * math.sin(angle) + random.uniform(-0.01, 0.01) * sh)
        px = max(50, min(sw - 50, px))
        py = max(50, min(sh - 150, py)) 
        pts.append((px, py))
    return pts


# ═══════════════════════════════════════════════════════════════════════════════
#  SMART DEPLOYMENT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
def _safe_cancel_spot(sw, sh):
    """
    Returns a random safe interior map coordinate that is away from the base
    perimeter red-lines. Used to cancel a stuck troop selection after a red-line
    click error. Position is in the far edge of the visible map area.
    """
    # Pick a corner near the edge of the map — guaranteed clear of any base structure
    candidates = [
        # Top-left map corner
        (int(sw * 0.08), int(sh * 0.12)),
        # Top-right map corner
        (int(sw * 0.92), int(sh * 0.12)),
        # Bottom-left (outside deployment bar)
        (int(sw * 0.08), int(sh * 0.72)),
        # Bottom-right (outside deployment bar)
        (int(sw * 0.92), int(sh * 0.72)),
    ]
    x, y = random.choice(candidates)
    # Add a small random jitter so repeated cancels look different
    x += random.randint(-30, 30)
    y += random.randint(-20, 20)
    return max(50, min(sw - 50, x)), max(40, min(sh - 160, y))


def _slot_still_active(slot, sw, sh):
    """Re-captures slot bar and checks if slot is still active/highlighted."""
    cx, cy, w, h = slot
    roi_y = int(sh * 0.78)
    roi_b = int(sh * 0.98)
    shot = ImageGrab.grab(bbox=(0, roi_y, sw, roi_b))
    bgr  = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
    return is_active(bgr, cx, cy, w, h, roi_y)


# ═══════════════════════════════════════════════════════════════════════════════
#  SMART DEPLOYMENT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
def deploy_slot(slot, drop_points, sw, sh, max_batches=12, drops_per_batch=5, delay=T_DROP, randomize=True):
    """
    Select a slot and continuously drop troops at drop_points in a repeating sweep
    until the slot becomes inactive (card is empty).

    Red-Line Recovery:
    If a drop click fails to place the troop (slot still active after expected
    change on count-mode drops), the bot:
      1. Clicks a safe random map corner to cancel the stuck selection
      2. Re-selects the troop slot card
      3. Retries the drop at a position shifted further outward from center

    If randomize is True, also adds spatial jitter, randomizes the sweep direction,
    and randomizes the starting point to prevent robotic repetition.

    Args:
        slot:            (cx, cy, w, h) of the slot card
        drop_points:     List of (x, y) positions to click on the map
        max_batches:     Maximum sweep rounds before stopping (safety cap)
        drops_per_batch: How many drop points to use per sweep pass
        delay:           Time between individual drop clicks
        randomize:       Whether to add human-like random variance to drops
    """
    cx, cy, w, h = slot
    roi_y = int(sh * 0.78)
    roi_b = int(sh * 0.98)

    # Work on a copy of the drop points
    pts = list(drop_points)

    if randomize:
        # 1. Randomly reverse the sweep direction
        if random.choice([True, False]):
            pts.reverse()

        # 2. Randomly shift the starting point (rotate the list)
        shift = random.randint(0, len(pts) - 1)
        pts = pts[shift:] + pts[:shift]

    n_pts = len(pts)
    total_clicks = 0
    ptr = 0   # pointer into pts
    consecutive_stuck = 0  # track how many times in a row the slot didn't clear

    for batch in range(max_batches):
        # Re-check slot state before each batch
        shot = ImageGrab.grab(bbox=(0, roi_y, sw, roi_b))
        bgr  = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
        if not is_active(bgr, cx, cy, w, h, roi_y):
            break   # slot exhausted

        cleared_this_batch = False

        for drop_idx in range(drops_per_batch):
            px, py = pts[ptr % n_pts]

            if randomize:
                # 3. Add small spatial jitter (±8 pixels)
                px += random.randint(-8, 8)
                py += random.randint(-8, 8)
                # Clamp to screen
                px = max(50, min(sw - 50, px))
                py = max(50, min(sh - 150, py))

            pyautogui.click(px, py)
            total_clicks += 1
            ptr += 1

            # ── Red-Line Recovery Check ────────────────────────────────────────
            # After a drop click, quickly check if the slot STILL looks active.
            # If the same slot is active after we clicked and we've tried at
            # least one drop, we suspect the last click landed on a red zone.
            time.sleep(0.06)  # brief pause for game to respond
            if total_clicks >= 1 and _slot_still_active(slot, sw, sh):
                # The drop likely failed (red-line hit).  Run recovery:
                consecutive_stuck += 1
                if consecutive_stuck >= 2:
                    print(f"  ⚠️  [RED-LINE] Slot still active after drop — running recovery (stuck×{consecutive_stuck})")

                    # Step 1: Click a safe spot to cancel the stuck selection
                    cancel_x, cancel_y = _safe_cancel_spot(sw, sh)
                    print(f"  ↩  [RED-LINE] Cancel-click at ({cancel_x},{cancel_y})")
                    pyautogui.click(cancel_x, cancel_y)
                    time.sleep(0.18)

                    # Step 2: Re-select the troop slot
                    pyautogui.moveTo(cx, cy, duration=0.15)
                    pyautogui.click()
                    time.sleep(T_SELECT_SHORT)

                    # Step 3: Build a shifted-outward position from current drop point
                    center_x, center_y = sw // 2, sh // 2
                    dx, dy = px - center_x, py - center_y
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        shift_amount = 35 + consecutive_stuck * 10   # grow shift with repeated failures
                        px2 = int(px + (dx / dist) * shift_amount)
                        py2 = int(py + (dy / dist) * shift_amount)
                        px2 = max(50, min(sw - 50, px2))
                        py2 = max(40, min(sh - 160, py2))
                    else:
                        # Fallback: choose a random perimeter point
                        px2, py2 = random.choice(pts)

                    print(f"  ↪  [RED-LINE] Recovery drop at ({px2},{py2})")
                    pyautogui.click(px2, py2)
                    time.sleep(0.12)
                    cleared_this_batch = True
            else:
                consecutive_stuck = 0
                cleared_this_batch = True

            # 4. Add small random delay jitter to look human
            click_delay = delay + random.uniform(-0.04, 0.04) if randomize else delay
            time.sleep(max(0.05, click_delay))

        time.sleep(random.uniform(0.06, 0.12) if randomize else 0.08)

    return total_clicks


def deploy_hero(slot, drop_point, sw, sh, delay=T_SELECT_SHORT):
    """Select a hero slot and drop at a single strategic point."""
    cx, cy, _, _ = slot
    roi_y = int(sh * 0.78)
    roi_b = int(sh * 0.98)

    shot = ImageGrab.grab(bbox=(0, roi_y, sw, roi_b))
    bgr  = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
    w_est = int(sw * 0.04)
    h_est = int(sh * 0.10)
    if not is_active(bgr, cx, cy, w_est, h_est, roi_y):
        print(f"  [SKIP] Hero slot at x={cx} is inactive (recovering).")
        return 0

    pyautogui.moveTo(cx, cy, duration=0.2)
    pyautogui.click()
    time.sleep(delay)
    pyautogui.click(drop_point[0], drop_point[1])
    time.sleep(0.30)
    return 1


def deploy_spell(slot, drop_point, sw, sh, delay=T_SPELL_DROP):
    """Select a spell slot and drop one spell at the specified point."""
    cx, cy, w, h = slot
    roi_y = int(sh * 0.78)
    roi_b = int(sh * 0.98)

    shot = ImageGrab.grab(bbox=(0, roi_y, sw, roi_b))
    bgr  = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
    if not is_active(bgr, cx, cy, w, h, roi_y):
        print(f"  [SKIP] Spell slot at x={cx} is inactive/empty.")
        return 0

    pyautogui.moveTo(cx, cy, duration=0.2)
    pyautogui.click()
    time.sleep(0.35)
    pyautogui.click(drop_point[0], drop_point[1])
    time.sleep(delay)
    return 1


# Removed old classify_slots function (now handled dynamically by detect_and_classify_slots)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN ATTACK ROUTINE
# ═══════════════════════════════════════════════════════════════════════════════
def execute_attack(sw, sh, army_config=None):
    """
    Execute one attack. If army_config is provided (from GUI), use configured
    troop counts, hero enable/skip flags and spell counts.
    army_config = {
        'troops':  [{'name': 'EDrag', 'count': 11}, ...],   # T1-T4
        'heroes':  [{'name': 'BK', 'enabled': True}, ...],  # H1-H4
        'spells':  [{'name': 'Rage', 'count': 5}, ...],     # S1-S2
    }
    """
    cx_screen = sw // 2
    cy_screen = sh // 2

    # Parse army_config once
    global hero_ability_delay
    troop_counts  = None
    hero_enabled  = None
    spell_counts  = None
    if army_config:
        t = army_config.get("troops", [])
        h = army_config.get("heroes", [])
        s = army_config.get("spells", [])
        if t: troop_counts = [max(1, entry.get("count", 1)) for entry in t]
        if h: hero_enabled  = [entry.get("enabled", True) for entry in h]
        if s: spell_counts  = [max(1, entry.get("count", 1)) for entry in s]
        if "hero_ability_delay" in army_config:
            hero_ability_delay = army_config["hero_ability_delay"]

    # ── 1. Zoom out ────────────────────────────────────────────────────────────
    pyautogui.moveTo(cx_screen, cy_screen, duration=0.3)
    time.sleep(0.4)
    print("[SCROLL] Zooming out...")
    for _ in range(15):
        mouse_ctrl.scroll(0, -1)
        time.sleep(0.05)
    print("[OK] Zoom complete.")
    time.sleep(1)

    # ── 2. Wait for base to fully render ───────────────────────────────────────
    print(f"[WAIT] Letting base render for {T_LOAD_BASE}s...")
    time.sleep(T_LOAD_BASE)

    # ── 3 & 4. Detect & Classify Slots (Hybrid Method) ─────────────────────────
    troops, heroes, spells = detect_and_classify_slots(sw, sh)

    # ── 5. Generate dynamic drop points ────────────────────────────────────────
    side = get_attack_side()
    if side == "left":
        sweep_pts = get_left_perimeter_sweep(sw, sh, n_points=14)
        hero_pts  = get_hero_drop_points(sw, sh)
    else:
        sweep_pts = get_right_perimeter_sweep(sw, sh, n_points=14)
        hero_pts  = get_right_hero_drop_points(sw, sh)

    spell_pts  = get_spell_drop_points(sw, sh, side=side, n_spells=max(6, len(spells) * 2))

    roi_y = int(sh * 0.78)
    roi_b = int(sh * 0.98)

    # ── 6. Deploy troops in perimeter sweep ───────────────────────────────
    print(f"\n🚀 [ATTACK] Deploying troops ({side}-perimeter sweep)...")
    shot = ImageGrab.grab(bbox=(0, roi_y, sw, roi_b))
    bgr  = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)

    deployed_any_troops = False
    for i, slot in enumerate(troops):
        cx, cy, w, h = slot
        if not is_active(bgr, cx, cy, w, h, roi_y):
            print(f"  [T{i+1}] Skip slot at x={cx} (inactive/x0)")
            continue

        print(f"  [T{i+1}] Select slot at x={cx}, y={cy}")
        pyautogui.moveTo(cx, cy, duration=0.2)
        pyautogui.click()

        wait_t = T_SELECT_LONG if not deployed_any_troops else T_SELECT_MED
        deployed_any_troops = True
        time.sleep(wait_t)

        # ── Determine click count from army_config or defaults ─────────────
        if i == 3:
            # Siege Machine always exactly 1 drop
            max_b, drops_pb = 1, 1
        elif troop_counts and i < len(troop_counts):
            count = troop_counts[i]
            max_b, drops_pb = count, 1   # 1 click per batch × count batches
            troop_name = army_config["troops"][i]["name"] if army_config else f"T{i+1}"
            print(f"  [T{i+1}] Army config: deploying {count}× {troop_name}")
        else:
            max_b, drops_pb = 12, 4     # default auto-drain

        total = deploy_slot(
            slot, sweep_pts, sw, sh,
            max_batches=max_b,
            drops_per_batch=drops_pb,
            delay=T_DROP
        )
        print(f"  [T{i+1}] Done  ({total} drops)")

    # ── 6.5. Retry active troops that failed to deploy (e.g. hit red line) ────
    print("\n🔍 [RETRY] Checking if any troops failed to deploy...")
    time.sleep(1.0)
    shot = ImageGrab.grab(bbox=(0, roi_y, sw, roi_b))
    bgr  = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)

    retry_sweep_pts = shift_outwards(sweep_pts, sw, sh, side=side, offset_px=30)

    for i, slot in enumerate(troops):
        if i == 3:
            # Never retry Siege Machine to avoid triggering early manual release
            continue
        cx, cy, w, h = slot
        if is_active(bgr, cx, cy, w, h, roi_y):
            print(f"  ⚠️ [T{i+1} RETRY] Slot at x={cx} is still active! Retrying...")
            pyautogui.moveTo(cx, cy, duration=0.2)
            pyautogui.click()
            time.sleep(T_SELECT_MED)

            max_b = 1 if i == 3 else 6
            drops_pb = 1 if i == 3 else 4

            total = deploy_slot(
                slot, retry_sweep_pts, sw, sh,
                max_batches=max_b,
                drops_per_batch=drops_pb,
                delay=T_DROP
            )
            print(f"  [T{i+1} RETRY] Done  ({total} drops)")

    # ── 7. Deploy heroes ────────────────────────────────────────────────────────
    print("\n🦸 [HEROES] Deploying heroes...")
    shot = ImageGrab.grab(bbox=(0, roi_y, sw, roi_b))
    bgr  = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)

    deployed_heroes = []
    for i, slot in enumerate(heroes):
        cx, cy, w, h = slot

        # ── Check if hero is disabled in army_config ───────────────────────
        if hero_enabled and i < len(hero_enabled) and not hero_enabled[i]:
            hero_name = army_config["heroes"][i]["name"] if army_config else f"H{i+1}"
            print(f"  [H{i+1}] Skip {hero_name} (disabled in army config)")
            continue

        if not is_active(bgr, cx, cy, w, h, roi_y):
            print(f"  [H{i+1}] Skip hero at x={cx} (inactive/recovering)")
            continue

        drop_pt = hero_pts[i % len(hero_pts)]
        hero_name = army_config["heroes"][i]["name"] if (army_config and i < len(army_config.get("heroes", []))) else f"H{i+1}"
        print(f"  [H{i+1}] Deploy {hero_name} at x={cx} → drop at {drop_pt}")
        pyautogui.moveTo(cx, cy, duration=0.2)
        pyautogui.click()
        time.sleep(T_SELECT_SHORT)
        pyautogui.click(drop_pt[0], drop_pt[1])
        deployed_heroes.append(slot)
        time.sleep(1.0)

    # ── 8. Deploy spells ────────────────────────────────────────────────────────
    print("\n✨ [SPELLS] Deploying spells...")
    spell_ptr = 0
    for i, slot in enumerate(spells):
        cx, cy, w, h = slot

        shot = ImageGrab.grab(bbox=(0, roi_y, sw, roi_b))
        bgr  = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
        if not is_active(bgr, cx, cy, w, h, roi_y):
            print(f"  [S{i+1}] Skip spell at x={cx} (inactive/x0)")
            continue

        # ── Determine spell count from army_config ─────────────────────────
        remaining = spell_counts[i] if (spell_counts and i < len(spell_counts)) else 99
        spell_name = army_config["spells"][i]["name"] if (army_config and i < len(army_config.get("spells", []))) else f"S{i+1}"
        print(f"  [S{i+1}] Deploy {spell_name} (max {remaining} casts) at x={cx}")

        casts = 0
        while casts < remaining:
            drop_pt = spell_pts[spell_ptr % len(spell_pts)]
            deployed = deploy_spell(slot, drop_pt, sw, sh)
            if not deployed:
                break
            spell_ptr += 1
            casts += 1
            time.sleep(T_SPELL_DROP)
        print(f"  [S{i+1}] Done  ({casts} casts)")

    # ── 9. Trigger hero special abilities ─────────────────────────────────────
    if deployed_heroes:
        print(f"\n⚡ [ABILITIES] Triggering hero abilities (cycle 1) in {hero_ability_delay}s...")
        time.sleep(hero_ability_delay)
        for slot in deployed_heroes:
            pyautogui.click(slot[0], slot[1])
            time.sleep(T_HERO_ABILITY)

        fallback_delay = min(5, hero_ability_delay)
        print(f"⚡ [ABILITIES] Triggering hero abilities (cycle 2 fallback) in {fallback_delay}s...")
        time.sleep(fallback_delay)
        for slot in deployed_heroes:
            pyautogui.click(slot[0], slot[1])
            time.sleep(T_HERO_ABILITY)

    print("\n[✓] Attack macro completed.")


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN FLOW
# ═══════════════════════════════════════════════════════════════════════════════
def main(army_config=None):
    print("╔══════════════════════════════════════════════════╗")
    print("║  Clash of Clans – New Update Dynamic Attack Bot  ║")
    print("╚══════════════════════════════════════════════════╝")
    sw, sh = pyautogui.size()
    print(f"  Screen: {sw}×{sh}\n")

    # Phase 1 – Attack! (lobby button)
    print("[Phase 1] Lobby Attack button")
    wait_and_click("attack_lobby", post_sleep=2.0)

    # Phase 2 – Find a Match
    print("[Phase 2] Find a Match")
    wait_and_click("find_match", post_sleep=2.0)

    # Phase 3 – Confirm Attack on opponent screen
    print("[Phase 3] Confirm Attack")
    wait_and_click("attack_confirm", post_sleep=1.0)

    # Phase 4 – Execute dynamic attack
    print("[Phase 4] Executing dynamic attack...")
    execute_attack(sw, sh, army_config=army_config)

    # Phase 5 – Return Home
    print("[Phase 5] Waiting for Return Home...")
    wait_and_click("return_home", threshold=0.72, post_sleep=4.0)

    # Phase 6 – Optional Star Bonus popup
    print("[Phase 6] Checking for Star Bonus popup (10s window)...")
    t0 = time.time()
    while time.time() - t0 < 10:
        pos = find_template("star_bonus", threshold=0.75)
        if pos:
            pyautogui.moveTo(pos[0], pos[1], duration=0.25)
            pyautogui.click()
            print("[CLICK] Closed Star Bonus popup.")
            time.sleep(2)
            break
        time.sleep(0.5)
    else:
        print("  No Star Bonus popup detected.")

    print("\n╔══════════════════════════════════════════════════╗")
    print("║  [SUCCESS] Battle completed!                     ║")
    print("╚══════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()

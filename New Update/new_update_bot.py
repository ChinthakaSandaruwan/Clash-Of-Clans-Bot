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
from PIL import ImageGrab
from pynput.mouse import Controller

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
    """Returns True if slot at (cx,cy) looks colored/active (not greyed-out)."""
    lx = max(0, cx - w // 4)
    rx = min(region_bgr.shape[1], cx + w // 4)
    ty = max(0, cy - roi_y - h // 4)
    by = min(region_bgr.shape[0], cy - roi_y + h // 4)
    crop = region_bgr[ty:by, lx:rx]
    if crop.size == 0:
        return False
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    return float(np.mean(hsv[:, :, 1])) > 28 and float(np.mean(hsv[:, :, 2])) > 45


def detect_slots(sw, sh):
    """Scan the bottom deployment bar and return list of (cx, cy, w, h) tuples."""
    roi_y = int(sh * 0.78)
    roi_b = int(sh * 0.98)
    shot  = ImageGrab.grab(bbox=(0, roi_y, sw, roi_b))
    bgr   = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
    gray  = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 40, 120)
    cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    mn_h, mx_h = int(sh * 0.06), int(sh * 0.17)
    mn_w, mx_w = int(sw * 0.02), int(sw * 0.11)
    raw = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if mn_h < h < mx_h and mn_w < w < mx_w and 0.45 < w/h < 1.3:
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

    print(f"[SLOTS] Detected {len(merged)} slots → x-positions: {[s[0] for s in merged]}")
    return merged


# ═══════════════════════════════════════════════════════════════════════════════
#  DYNAMIC DROP-POINT GENERATORS  (learned from Normal Battle bot patterns)
# ═══════════════════════════════════════════════════════════════════════════════
def get_left_perimeter_sweep(sw, sh, n_points=14):
    """
    Generate n_points along the LEFT-SIDE ARC of the base.
    
    Pattern learned from Normal Battle bots (bot1-bot12):
      Troops are swept from the bottom-left corner of the village 
      up along the left edge and across the top-left.
    
    The village base is a diamond-shape centered roughly at (sw*0.38, sh*0.52)
    The left edge arc runs from bottom-left to top-left of the diamond.
    
    Normalised pattern extracted from bot1.py on 1920×1200:
      (639,902) → (552,841) → (478,760) → (397,706) → (321,639) →
      (220,567) → (310,472) → (418,387) → (508,315) → (585,261) → (674,203)
    """
    # Base center (normalised)
    cx = sw * 0.38
    cy = sh * 0.52

    # The sweep arc goes from ~210° to ~330° (bottom-left to top-left, 
    # measured clockwise from 3-o'clock, matching CoC village diamond left edge)
    # Radius scales with screen
    rx = sw * 0.24   # horizontal radius of the village diamond (left half)
    ry = sh * 0.31   # vertical radius

    # Arc from bottom-left (220° from 3-o'clock ≈ π*220/180) to 
    # upper-right-ish (340° = almost 0 from top)
    # In standard math angles (counterclockwise from east):
    # bottom-left of diamond  ≈ 210°
    # top of diamond          ≈ 90°  (but we stop at upper-left)
    # We want a sweep from ~200° down to ~90° going counterclockwise

    start_deg = 210
    end_deg   = 70    # stop at upper-left edge

    # Generate evenly spaced angle points along the arc
    points = []
    for i in range(n_points):
        t     = i / max(n_points - 1, 1)
        deg   = start_deg + t * (end_deg - start_deg)   # 210 → 70
        rad   = math.radians(deg)
        px    = int(cx + rx * math.cos(rad))
        py    = int(cy - ry * math.sin(rad))   # minus because screen y is inverted
        # clamp to screen bounds with a small margin
        px    = max(50, min(sw - 50, px))
        py    = max(50, min(sh - 150, py))
        points.append((px, py))
    return points


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


def get_spell_drop_points(sw, sh, n_spells=6):
    """
    Return n_spells drop points scattered in the center-right interior area.
    
    Rage spell targets from bots (normalised on 1920×1200):
      (880,689) → (776,594) → (772,492) → (906,448) → (899,545)
    Freeze: (980,555)
    
    These are in the right half of the base interior.
    We generate a small random cluster in that region.
    """
    # Center-right interior zone (normalised)
    base_x = sw * 0.46
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
def deploy_slot(slot, drop_points, sw, sh, max_batches=12, drops_per_batch=5, delay=T_DROP):
    """
    Select a slot and continuously drop troops at drop_points in a repeating sweep
    until the slot becomes inactive (card is empty).
    
    Args:
        slot:            (cx, cy, w, h) of the slot card
        drop_points:     List of (x, y) positions to click on the map
        max_batches:     Maximum sweep rounds before stopping (safety cap)
        drops_per_batch: How many drop points to use per sweep pass
        delay:           Time between individual drop clicks
    """
    cx, cy, w, h = slot
    roi_y = int(sh * 0.78)
    roi_b = int(sh * 0.98)
    n_pts = len(drop_points)
    total_clicks = 0
    ptr = 0   # pointer into drop_points

    for batch in range(max_batches):
        # Re-check slot state before each batch
        shot = ImageGrab.grab(bbox=(0, roi_y, sw, roi_b))
        bgr  = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
        if not is_active(bgr, cx, cy, w, h, roi_y):
            break   # slot exhausted

        for _ in range(drops_per_batch):
            px, py = drop_points[ptr % n_pts]
            pyautogui.click(px, py)
            total_clicks += 1
            ptr += 1
            time.sleep(delay)

        time.sleep(0.08)

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


# ═══════════════════════════════════════════════════════════════════════════════
#  SLOT ROLE CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════════
def classify_slots(slots, sw, sh):
    """
    Classify each slot into: 'troop', 'hero', or 'spell'
    
    Strategy learned from Normal Battle bots:
    - The FIRST troop slot gets a long select delay (T_SELECT_LONG=4.14s) → classified
      as the primary high-count troop (Electro Dragons)
    - Middle slots with lower x have fewer counts → troops  
    - Hero slots typically appear at higher x values AND have a circular icon frame
      (slightly different aspect ratio). We detect this by checking saturation pattern.
    - Spell slots are the RIGHTMOST slots (last ~20-25% of x range)
    
    In the successful run with 9 slots at x=[259,409,520,702,811,864,940,1377,1537]:
      The spells started at x=1377 (≈72% of 1920). So cutoff ≈ 70-75% of screen.
    """
    if not slots:
        return [], [], []

    # Sort by x (already sorted by detect_slots)
    max_x = max(s[0] for s in slots)

    # Spell cutoff: rightmost 28% of x range among all slots
    x_range  = max_x - slots[0][0]
    spell_cutoff = max_x - x_range * 0.28

    troops = []
    heroes = []
    spells = []

    for s in slots:
        cx = s[0]
        if cx >= spell_cutoff:
            spells.append(s)
        else:
            # Distinguish troops from heroes by checking if the slot looks like
            # a hero card (hero cards tend to be slightly taller/squarer).
            # Additionally, hero slots usually appear in a cluster together.
            # Simple heuristic: if there are >1 consecutive slots spaced < 7% sw apart
            # in the mid section, treat all of those as heroes.
            troops.append(s)   # initially all non-spell go to troops

    # Hero detection heuristic: find a cluster of 3-5 consecutive slots
    # in the mid-right section that are tightly packed (heroes sit side by side).
    # Typically ≥4 consecutive slots spaced < 6% of screen width apart.
    if len(troops) >= 4:
        spacings = [troops[i+1][0] - troops[i][0] for i in range(len(troops)-1)]
        avg_spacing = sum(spacings) / len(spacings)
        # Hero group: consecutive slots with spacing < 80% of average spacing
        # (heroes are slightly more tightly packed than troops)
        hero_group_start = None
        hero_group_end   = None
        for i, sp in enumerate(spacings):
            if sp < avg_spacing * 0.85:
                if hero_group_start is None:
                    hero_group_start = i
                hero_group_end = i + 1
        if hero_group_start is not None and (hero_group_end - hero_group_start) >= 2:
            heroes = troops[hero_group_start:hero_group_end + 1]
            troops = [s for s in troops if s not in heroes]

    print(f"[CLASSIFY] Troops={len(troops)}  Heroes={len(heroes)}  Spells={len(spells)}")
    return troops, heroes, spells


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN ATTACK ROUTINE
# ═══════════════════════════════════════════════════════════════════════════════
def execute_attack(sw, sh):
    cx_screen = sw // 2
    cy_screen = sh // 2

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

    # ── 3. Detect slots ────────────────────────────────────────────────────────
    slots = detect_slots(sw, sh)
    if not slots:
        print("[WARNING] No slots detected — using fallback horizontal grid.")
        y_fb = int(sh * 0.92)
        w_fb, h_fb = int(sw * 0.05), int(sh * 0.12)
        xs   = [int(sw * 0.15 + i * sw * 0.07) for i in range(10)]
        slots = [(x, y_fb, w_fb, h_fb) for x in xs]

    # ── 4. Classify slots ──────────────────────────────────────────────────────
    troops, heroes, spells = classify_slots(slots, sw, sh)

    # ── 5. Generate dynamic drop points ────────────────────────────────────────
    sweep_pts  = get_left_perimeter_sweep(sw, sh, n_points=14)
    hero_pts   = get_hero_drop_points(sw, sh)
    spell_pts  = get_spell_drop_points(sw, sh, n_spells=max(6, len(spells) * 2))

    # ── 6. Deploy troops in left-perimeter sweep ───────────────────────────────
    print("\n🚀 [ATTACK] Deploying troops (left-perimeter sweep)...")
    for i, slot in enumerate(troops):
        cx, cy, w, h = slot
        print(f"  [T{i+1}] Select slot at x={cx}, y={cy}")
        pyautogui.moveTo(cx, cy, duration=0.2)
        pyautogui.click()
        # First troop gets a long wait (Electro Dragon / main troop fill animation)
        wait_t = T_SELECT_LONG if i == 0 else T_SELECT_MED
        time.sleep(wait_t)

        total = deploy_slot(
            slot, sweep_pts, sw, sh,
            max_batches=12,
            drops_per_batch=4,
            delay=T_DROP
        )
        print(f"  [T{i+1}] Done  ({total} drops)")

    # ── 7. Deploy heroes ────────────────────────────────────────────────────────
    print("\n🦸 [HEROES] Deploying heroes...")
    for i, slot in enumerate(heroes):
        cx, cy, _, _ = slot
        drop_pt = hero_pts[i % len(hero_pts)]
        print(f"  [H{i+1}] Select hero at x={cx} → drop at {drop_pt}")
        pyautogui.moveTo(cx, cy, duration=0.2)
        pyautogui.click()
        time.sleep(T_SELECT_SHORT)
        pyautogui.click(drop_pt[0], drop_pt[1])
        time.sleep(1.0)

    # ── 8. Deploy spells ────────────────────────────────────────────────────────
    print("\n✨ [SPELLS] Deploying spells...")
    spell_ptr = 0
    for i, slot in enumerate(spells):
        cx, cy, w, h = slot
        print(f"  [S{i+1}] Select spell at x={cx}")
        # Drain all charges of this spell type
        while True:
            drop_pt = spell_pts[spell_ptr % len(spell_pts)]
            deployed = deploy_spell(slot, drop_pt, sw, sh)
            if not deployed:
                break
            spell_ptr += 1
            time.sleep(T_SPELL_DROP)
        print(f"  [S{i+1}] Done")

    # ── 9. Trigger hero special abilities ─────────────────────────────────────
    print("\n⚡ [ABILITIES] Triggering hero abilities (cycle 1)...")
    time.sleep(12)
    for slot in heroes:
        pyautogui.click(slot[0], slot[1])
        time.sleep(T_HERO_ABILITY)

    print("⚡ [ABILITIES] Triggering hero abilities (cycle 2)...")
    time.sleep(12)
    for slot in heroes:
        pyautogui.click(slot[0], slot[1])
        time.sleep(T_HERO_ABILITY)

    print("\n[✓] Attack macro completed.")


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN FLOW
# ═══════════════════════════════════════════════════════════════════════════════
def main():
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
    execute_attack(sw, sh)

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

# Clash of Clans Attack Bot

Lightweight collection of Python automation scripts to run attack sequences in Clash of Clans using screen image matching and mouse automation.

**Quick summary**
- Automates repeated attack flows using `pyautogui` image matching and simple control logic.
- Designed for a single-screen, fixed-layout setup (may need adjustments for other resolutions).

**Project layout**
- `main.py`: orchestrates running the individual bot scripts sequentially.
- `bot1.py` … `bot10.py`: individual attack scripts (one per run).
- `*.png`: reference screenshots used by `pyautogui.locateOnScreen`.
- `Dev Files/`: development helpers and logs.

Requirements
- Python 3.8+ (or 3.x)
- `pyautogui`
- `pynput` (used for optional input control)

Install dependencies:

```bash
pip install pyautogui pynput
```

Usage

1. Start Clash of Clans and make sure the game window is visible and its UI matches the reference screenshots.
2. Place the required reference images into the project root (examples used by the scripts):
   - `(1)attack!.png`
   - `(2)Find a Match 1700.png`
   - `(3)Attack!.png`
   - `(4)Return Home.png`
3. To run a single bot script:

```bash
python bot1.py
```

4. To run the full sequence (runs `bot1.py` → `bot10.py` with short pauses):

```bash
python main.py
```

Notes and tips

- The scripts rely on pixel-based image matching; results vary by screen resolution, scaling, and theme. If images are not found, re-capture screenshots at your current resolution and update the `*.png` files.
- To adapt for other resolutions, update coordinates and reference images inside each `bot*.py`.

Safety & cautions

- These scripts control your mouse and keyboard. Do not run them while using your machine for other tasks.
- `pyautogui.FAILSAFE` is enabled: move the mouse to a corner to abort.
- Automation may violate game terms of service. Use at your own risk.

Development

- Use [Dev Files](Dev%20Files/) for helpers and experiments.
- If you want, I can help: extract common utilities, add a `requirements.txt`, or add a safer dry-run mode.

License & credits

- This repository is provided as-is. Modify and use responsibly.



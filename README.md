# Clash of Clans Attack Bot

This repository contains a set of Python automation scripts for running Clash of Clans attack sequences using screen image matching and mouse automation.

## Files

- `main.py` — Runs `bot1.py` through `bot10.py` sequentially, waiting 10 seconds between each bot.
- `bot1.py` through `bot10.py` — Individual bot scripts that perform a full attack sequence using `pyautogui` and image recognition.
- `*.png` — Reference screenshots used by `pyautogui.locateOnScreen` to find attack buttons and control flow.
- `Dev Files/` — Additional development files and logs.

## Requirements

- Python 3.x
- `pyautogui`
- `pynput`

Install dependencies with:

```bash
pip install pyautogui pynput
```

## Usage

1. Make sure Clash of Clans is running and visible on your screen.
2. Place the required reference images in the project folder:
   - `(1)attack!.png`
   - `(2)Find a Match 1700.png`
   - `(3)Attack!.png`
   - `(4)Return Home.png`
3. Run the full sequence:

```bash
python main.py
```

This will execute each bot script in order from `bot1.py` to `bot10.py`, pausing 10 seconds between each run.

## Notes

- Each bot script uses `pyautogui` image matching to click UI elements.
- The scripts assume a fixed screen layout and coordinate positions.
- Modify the bot scripts if your screen resolution or game UI positions differ.

## Caution

- These scripts control your mouse and keyboard automatically.
- Keep your system idle while the scripts run to avoid accidental interruptions.
- `pyautogui.FAILSAFE` is enabled, so moving the mouse to a screen corner will stop the script.

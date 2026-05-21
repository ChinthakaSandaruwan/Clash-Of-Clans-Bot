import subprocess
import sys
import time
from pathlib import Path

bot_files = [f"bot{i}.py" for i in range(1, 12)]
workspace_dir = Path(__file__).resolve().parent


def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

for index, bot_file in enumerate(bot_files, start=1):
    bot_path = workspace_dir / bot_file
    print(f"\n=== Starting Bot {index}: {bot_file} ===")

    if not bot_path.exists():
        print(f"ERROR: {bot_file} not found at {bot_path}")
        break

    result = subprocess.run([sys.executable, str(bot_path)], cwd=str(workspace_dir))
    print(f"{ordinal(index)} bot finished with exit code {result.returncode}.")

    if result.returncode != 0:
        print(f"Stopping sequence because {bot_file} returned non-zero exit code.")
        break

    if index < len(bot_files):
        print("Waiting 10 seconds before starting the next bot...")
        time.sleep(10)

print("\nAll configured bot runs completed.")

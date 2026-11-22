import logging
import builtins
import re
from colorama import Fore, Style
from datetime import datetime
from pathlib import Path

log_dir = Path("logs/")
log_dir.mkdir(parents=True, exist_ok=True)
original_print = builtins.print
ANSI_ESCAPE = re.compile(r'(?:\x1B\[|\x9B|\[)[0-?]*[ -/]*[@-~]')

def custom_print(*args, **kwargs):
    now = datetime.now()
    formatted_str = now.strftime("%H:%M:%S.%f")[:-3]
    formatted_str2 = now.strftime("%d.%m.%Y")
    log_file = str(log_dir) + "/" + str(formatted_str2) + ".log"
    timestamp = now.strftime("%H:%M:%S")
    clean_args = [ANSI_ESCAPE.sub("", str(arg)) for arg in args]
    with open(log_file, "a", encoding="utf-8") as f:
        original_print(f"[{timestamp}]", *clean_args, file=f, **kwargs)
    prefix = f"{Fore.LIGHTBLUE_EX}[{formatted_str}]{Style.RESET_ALL}"
    original_print(prefix, *args, **kwargs)

builtins.print = custom_print

original_emit = logging.StreamHandler.emit

def custom_emit(self, record):
    formatted = self.format(record)
    print(formatted)

logging.StreamHandler.emit = custom_emit

import asyncio
from DiscordJellyFinBot import main as botmain; 
from DiscordJellyFinBot import exit
from api import main as apimain

async def main():
    try:
        await asyncio.gather(
            apimain(),
            botmain()
        )
    finally:
        await exit()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
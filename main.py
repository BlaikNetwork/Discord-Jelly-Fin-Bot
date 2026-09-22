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
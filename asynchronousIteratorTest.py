import asyncio
from bleak import BleakScanner

async def main():
    a = BleakScanner()
    await a.start()

    try:
        async for n in a.advertisement_data():
            print(n)
    except KeyboardInterrupt:
        await a.stop()
        exit()
asyncio.run(main())
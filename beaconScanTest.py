import asyncio
from bleak import BleakScanner

async def main():
    while True:
        devices = await BleakScanner.discover()
        for d in devices:
            print(d)
# async def main():
#     manager =BleakScanner()
#     await manager.start()
#     await asyncio.sleep(5)
#     async for (beacon,adverisement) in manager.advertisement_data():
#             print(beacon)
asyncio.run(main())
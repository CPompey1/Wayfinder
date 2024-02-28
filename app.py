from BeaconManager import BeaconManager
import asyncio

from wayfinder import *


#tests closest beacon function by printing closest beacon, then subsequenyly printing all the beacon rssi's
async def main():
    manager = BeaconManager()
    await manager.initialize()
    filename = open("services.json")
    services_from_jason = json.load(filename)
    wayfinder = Wayfinder_UI(services_from_jason)
    await manager.close()
asyncio.run(main())
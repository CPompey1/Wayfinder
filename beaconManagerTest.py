from BeaconManager import BeaconManager
import asyncio


#tests closest beacon function by printing closest beacon, then subsequenyly printing all the beacon rssi's
async def main():
    manager = BeaconManager()
    await manager.initialize()
    beacons = manager.get_beacons()
    print(beacons)
    closest = manager.get_closest()
    print(closest)

    for n in beacons.keys():
        print(abs(beacons[n].rssi))
    await manager.close()
asyncio.run(main())
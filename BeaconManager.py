from bleak import BleakScanner, BleakClient
import bleak
import asyncio
class BeaconManager:

    
    async def __init__(self) -> None:
        self.scanner = BleakScanner() 
        self.beacons = {}
        temp = await self.scanner.discover()
        for beacon in temp:
            self.beacons[beacon.address] = beacon

        self.beacon_addresses = {}
        for beacon in self.beacons:
            self.beacon_addresses[be==]
        self.beaconUpdater = asyncio.create_task(self.update_beacons())
        return
     
    def get_closest(self):
        return min(self.beacons)
    
    def get_beacons(self):
        return self.beacons
    
    async def update_beacons(self):
        #advertisement (BLEDevice,AdvertisementData)
        for advertisement in await self.scanner.advertisement_data():
                self.beacons[advertisement[0].address] = advertisement[0]

    def close(self):
         self.beaconUpdater.cancel()
    

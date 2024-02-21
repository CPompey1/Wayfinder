from bleak import BleakScanner, BleakClient
import bleak
import asyncio
class BeaconManager:
    MAX_RSI = 200
    
    def __init__(self):
        self.scanner = BleakScanner() 
        self.beacons = {}
        self.closest = None #(bleDevice,rssi)

    async def initialize(self):
        # i = 0
        # temp = await self.scanner.discover()
        # for beacon in temp:
        #     if i == 0:
        #         smallest = (self.beacons[beacon],self.beacons[beacon].rssi)
        #     self.beacons[beacon.address] = beacon
        #     i+=1
        await self.scanner.start()
        self.beaconUpdater = asyncio.create_task(self.update_beacons())
        # temp = asyncio.run(self.beaconUpdater)
        self.loop = asyncio.get_event_loop()
        await asyncio.sleep(5)
     
    #Returns beacon with smallest rssi value
    def get_closest(self):
        return self.closest
    
    def get_beacons(self):
        return self.beacons
    
    async def update_beacons(self):
        #advertisement (BLEDevice,AdvertisementData)
        # for advertisement in await self.scanner.advertisement_data():
        #         self.beacons[advertisement[0].address] = advertisement[0]
        # temp = await self.scanner.discover()
        async for beacon in self.scanner.advertisement_data():
            self.beacons[beacon[0].address] = beacon[0]
            if self.closest == None or beacon[1].rssi < abs(self.closest[1]):
                self.closest = (beacon[0],abs(beacon[1].rssi)) 


    async def close(self):
        self.beaconUpdater.cancel()
        await self.scanner.stop()
    

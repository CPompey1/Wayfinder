from bleak import BleakScanner, BleakClient
import bleak
import asyncio
class BeaconManager:
    MAX_RSI = 200
    MAX_UNIQUE = 3
    def __init__(self):
        self.scanner = BleakScanner() 
        self.beacons = {}
        self.closest = [None,None,None] #[(bleDevice,macadress,,rssi)]
        # self.uniqueBeacons = [(None,None,None),(None,None,None),(None,None,None)] # [(BLEdevice,macadress,rssi) ]
        self.uniqueBeacons = {} #{key(macadress): value (bledevice,rssi)}
        self.numUnique = 0

    async def initialize_scanning(self):
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
    
    def clear_closest(self):
        self.closest = [None,None,None]

    def get_beacons(self):
        return self.beacons
    
    #returns a dictionary where each key contains a unque beacons macadress(or name) and the value is a tuple (bledevice,recent rssi) with its most recenetly seen rssi
    def get_unique_beacons(self):
        out = {}
        for i in range(len(self.uniqueBeacons[0])):
           #key (mac adress): value (bledevice,rssi) 
           out[self.uniqueBeacons[1][i]] = (self.uniqueBeacons[0][i],self.uniqueBeacons[2][i])
        return out
    def clear_unique_beacons(self):
        self.numUnique = 0
        self.uniqueBeacons = {}

    async def update_beacons(self):
        #advertisement (BLEDevice,AdvertisementData)
        # for advertisement in await self.scanner.advertisement_data():
        #         self.beacons[advertisement[0].address] = advertisement[0]
        # temp = await self.scanner.discover()
        async for beacon in self.scanner.advertisement_data():
            self.beacons[beacon[0].address] = beacon[0]
            # if self.closest == None or beacon[1].rssi < abs(self.closest[1]):
            #     self.closest = (beacon[0],abs(beacon[1].rssi)) 
            
            #If number of unqiue beacons is less than 3 and the adress doesnt already exist in unqie beacons
            if self.numUnique < BeaconManager.MAX_UNIQUE and not beacon[0].address in  self.uniqueBeacons.keys():
                self.uniqueBeacons[beacon[0].address] = (beacon[0],beacon[1].rssi)
                self.numUnique+=1

            for i in range(len(self.closest)):
                beaconTuple = self.closest[i]
                if beaconTuple == None or abs(beacon[1]) < abs(beaconTuple[2]):
                    self.closest[i] = (beacon[0].address,beacon[0],beacon[1].rssi)


    async def close(self):
        #might need to await
        self.beaconUpdater.cancel()
        await self.scanner.stop()
    
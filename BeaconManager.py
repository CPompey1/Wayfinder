import threading
from bleak import BleakScanner, BleakClient
import bleak
import asyncio
from globals import EMITTER_LOC_DICT,sharedData
import signal
class AdvertisementTimeoutException(Exception):
    pass

class BeaconManager:
    MAX_RSI = 200
    MAX_UNIQUE = 3


    def __init__(self):
        self.scanner = BleakScanner() 
        self.beacons = {}
        self.newBatch = 0
        self.closest = [None,None,None] #[(bleDevice,macadress,,rssi)]
        self.num_closest = 0
        self.closest_addr = [None,None,None]
        # self.uniqueBeacons = [(None,None,None),(None,None,None),(None,None,None)] # [(BLEdevice,macadress,rssi) ]
        self.uniqueBeacons = {} #{key(macadress): value (bledevice,rssi)}
        self.numUnique = 0
        self.closing = False
        self.lock = threading.Lock()
    async def initialize_scanning(self):

        await self.scanner.start()
        self.beaconUpdater = asyncio.create_task(self.update_beacons())

        await asyncio.sleep(5)
       
        
     
    #Returns beacon with smallest rssi value
    def get_closest(self):
        return self.closest

    def clear_closest(self):
        with self.lock: 
            # self.beaconUpdater.cancel()
            # print("Resetting task************************")
            # with open('locationData','a') as file:
            #     file.write(f'Restting task\n')
            # print("********************************RETTING*************************************************")
            # self.beaconUpdater = asyncio.create_task(self.update_beacons())
            self.closest = [None,None,None]
            # self.closest_addr = [None,None,None]
            # self.num_closest = 0  
        return
    
    def closest_full(self):
        with self.lock:
            if not None in self.beacons:
                return True
            else: return False
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


        with open('locationData','a') as file:
             file.write(f'STARTING UPDATE BEACOSN\n')
        async for beacon,ad_packet in self.scanner.advertisement_data() :
            if self.closing: return

            # print(f"Beacon Device {beacon}\n advertisement: {ad_packet}")

            beacon_addr = beacon.address

            beacon_rssi = ad_packet.rssi
            if beacon_addr == None: continue

            # #filter for only beacons in the emitter location dict
            if not beacon_addr in EMITTER_LOC_DICT.keys(): 
                continue
            

            self.beacons[beacon_addr] = (beacon,beacon_rssi)

            # #If number of unqiue beacons is less than 3 and the adress doesnt already exist in unqie beacons
            if self.numUnique < BeaconManager.MAX_UNIQUE and not beacon_addr in  self.uniqueBeacons.keys():
                self.uniqueBeacons[beacon_addr] = (beacon,beacon_rssi)
                self.numUnique+=1


            done = False

            with self.lock:
            # if not (beacon_addr in self.closest_addr and self.num_closest > 2): 
                for i in range(len(self.closest)):
                    beaconTuple = self.closest[i]
                    if done: break
                    if beaconTuple == None or abs(beacon_rssi) < abs(beaconTuple[2]):
                        self.newBatch = (self.newBatch + 1)%3
                        self.closest[i] = (beacon_addr,beaconTuple,abs(int(beacon_rssi)))
                        done = True

       

    async def batch_ready(self):
        pass
    async def get_num_closest(self) -> int:
        with self.lock:
            out = self.num_closest
        return out
    async def close(self):
        #might need to await
        self.closing = True
        self.update_beacons_thread.join()
        return
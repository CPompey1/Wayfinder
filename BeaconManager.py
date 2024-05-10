import threading
import time
from bleak import BleakScanner, BleakClient
import bleak
import asyncio
from globals import EMITTER_LOC_DICT, sharedData
import signal


# def print(input):
#     with open('logData.txt','a') as file:
#         file.write(f'{input}\n')
#     return
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
        # self.event_loop = asyncio.new_event_loop()

        await asyncio.sleep(1)
        # self.beaconUpdater = threading.Thread(target=self.update_beacons)
        await self.update_beacons()
        # with asyncio.Runner() as runner:
        #     asyncio.run(self.update_beacons())
        # self.beaconUpdater.start()
        
        # await self.beaconUpdater
       
        
     
    #Returns beacon with smallest rssi value
    def get_closest(self):
        with self.lock:
            out = self.closest
        return out

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
            if not None in self.closest:
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
        await self.scanner.start()
        await asyncio.sleep(1)
    # while True:
        # foundBeaocons = await self.scanner.discover(timeout=2)
        # print("starting update_beacons....")

        # with open('locationData','a') as file:
        #     file.write(f'STARTING UPDATE BEACOSN\n')
        
        # foundBeaocons = self.scanner.discovered_devices
        print("Starting update beacons*******************")
        while not sharedData.closing:
            
            discoveredDevices = self.scanner.discovered_devices_and_advertisement_data.copy()
            for key in discoveredDevices.keys():
                beacon, ad_packet = discoveredDevices[key]
                await self.handle_beacon(beacon, ad_packet)
            await asyncio.sleep(.200)
    async def handle_beacon(self,beacon,ad_packet):
            if sharedData.closing:
                return
            
            print("updating beacons*******************")
            await asyncio.sleep(.1)
            if self.closing: return

            # print(f"Beacon Device {beacon}\n advertisement: {ad_packet}")

            beacon_addr = beacon.address

            beacon_rssi = beacon.rssi
            if beacon_addr == None: return 

            # #filter for only beacons in the emitter location dict
            if not beacon_addr in EMITTER_LOC_DICT.keys(): 
                return
            
            
            if not beacon_addr in self.beacons.keys(): print("***************New Beacon***************!") 
            if beacon_addr in self.beacons.keys():
                    lastIdx = self.beacons[beacon_addr][2]
                    self.beacons[beacon_addr] = (beacon,beacon_rssi,lastIdx+1)
            else:
                self.beacons[beacon_addr] = (beacon,beacon_rssi,0)

            # #If number of unqiue beacons is less than 3 and the adress doesnt already exist in unqie beacons
            if self.numUnique < BeaconManager.MAX_UNIQUE and not beacon_addr in  self.uniqueBeacons.keys():
                self.uniqueBeacons[beacon_addr] = (beacon,beacon_rssi)
                self.numUnique+=1


            done = False
            beacon_exists = True
        
            with self.lock:
            # if not (beacon_addr in self.closest_addr and self.num_closest > 2): 
                #if beacon exists already
                for i in range(len(self.closest)):
                    beaconTuple = self.closest[i]
                    if done: break
                    if not beaconTuple == None and beacon_addr in beaconTuple:
                        self.closest[i] = (beacon_addr,beacon,abs(int(beacon_rssi)))
                        print("Updated a closest beacon")
                        done = True
                #if theres a None value
                for i in range(len(self.closest)):
                    beaconTuple = self.closest[i]
                    if done: break

                    if  beaconTuple == None:
                        self.newBatch = (self.newBatch + 1)%3
                        self.closest[i] = (beacon_addr,beacon,abs(int(beacon_rssi)))
                        print("added a new closest beacon")
                        
                        done = True
                #if theres a new closer beacon
                for i in range(len(self.closest)):
                    beaconTuple = self.closest[i]
                    if done: break

                    if abs(int(beacon_rssi)) < beaconTuple[2]:
                        self.closest[i] = (beacon_addr,beacon,abs(int(beacon_rssi)))
                        print("added a new closest beacon")
                        done = True



                    #Replace Nones
                    
                        

                            

        

    async def batch_ready(self):
        pass
    async def get_num_closest(self) -> int:
        with self.lock:
            out = self.num_closest
        return out
    async def close(self):
        #might need to await
        self.closing = True
        # self.update_beacons_thread.join()
        return
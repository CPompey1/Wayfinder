import time
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import Canvas
import ttkbootstrap as ttkint
from PIL import ImageTk, Image, ImageOps
import json
import threading
import asyncio
from BFS import BFS
# from MPU.run_mpu import MpuClass
from MPU.run_mpu import MpuClass
from globals import *
from BeaconManager import BeaconManager
from wayfinder import Wayfinder_UI
if not SIMULATION: from MPU.run_mpu import runMpu
from globals import EMITTER_LOC_DICT
from tra_localization import tra_localization


async def runNavigation(manager):
    await asyncio.sleep(5)
    # while not sharedData.closing:
        # while sharedData.navigation_started and not sharedData.closing:
    while(True):
            # await asyncio.sleep(.1)
            
            closest_beacons = manager.get_closest()
            all_beacons = manager.get_beacons()
            if manager.closest_full():
                print("********************************FULL*************************************************")
                print(f"Beacons: {all_beacons}")
                print(f"Closest Beacons: {closest_beacons}")    
                print("Entering localization")
                location = await tra_localization(closest_beacons,EMITTER_LOC_DICT)
                with sharedData.lock:
                    sharedData.estimated_location = location
                with open('locationData','a') as file:
                        file.write(f'Estimated Location: {location}\n')
                manager.clear_closest()
            else:
                # print("not full\n")
                pass
            yield
        # await asyncio.sleep(1)

async def main():
    # Read json file for services and rooms 
    filename = open("services.json")
    services_from_jason = json.load(filename)

    # self.mpu = MpuClass()
        # if not SIMULATION: 
            
        #     self.mpu_thread = threading.Thread(target=runMpu, daemon=True)
        #     self.mpu_thread.start()
        # else:
        #     self.mpu_thread = threading.Thread(target=sim_mpu, daemon=True)
        #     self.mpu_thread.start()
    # beaconManager = BeaconManager()
    beaconManager = BeaconManager()
    mpu = MpuClass()
    wayfinder = Wayfinder_UI(services_from_jason)
    # await wayfinder.start(),await mpu.runMpu()
    # beacon_task = asyncio.create_task(beaconManager.initialize_scanning())
    # navigatoin_task = asyncio.create_task(runNavigation(beaconManager))
    # wayfinder_ui_task = asyncio.create_task(wayfinder.start())
    # mpu_task = asyncio.create_task(mpu.runMpu())
    a = asyncio.gather(await asyncio.create_task(wayfinder.start()),
                       await asyncio.create_task(mpu.runMpu()),
                     await asyncio.create_task(beaconManager.initialize_scanning()),
                       await asyncio.create_task(runNavigation(beaconManager)),
                       )
    
    # wayfinder = Wayfinder_UI(services_from_jason)
    

    # self.mpu = MpuClass()
        # if not SIMULATION: 
            
        #     self.mpu_thread = threading.Thread(target=runMpu, daemon=True)
        #     self.mpu_thread.start()
        # else:
        #     self.mpu_thread = threading.Thread(target=sim_mpu, daemon=True)
        #     self.mpu_thread.start()
    
    # wayfinder.close()

asyncio.run(main())
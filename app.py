from BeaconManager import BeaconManager
import asyncio
import json
from wayfinder import Wayfinder_UI,draw_path
import threading
from globals import EMITTER_LOC_DICT
from tra_localization import tra_localization

#might wanna put in globals
class SharedData:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.estimated_location = 0
   

sharedData = SharedData()
wayfinderUI = None


#tests closest beacon function by printing closest beacon, then subsequenyly printing all the beacon rssi's
async def main():
    #initialize beacon manager
    manager = BeaconManager()
    await manager.initialize_scanning()
    
    #load json files
    filename = open("services.json")
    services_from_jason = json.load(filename)
    # navigation_thread = threading.Thread(target=runNavigation,args=(manager,))    
    # navigation_thread.start()
    navigation_task = asyncio.create_task(runNavigation(manager))
    #start UI
    # wayfinderUI_task = asyncio.create_task(Wayfinder_UI(services_from_jason))
    
    wayfinder = Wayfinder_UI(services_from_jason)
    # wayfinder.start()
    asyncio.create_task(wayfinder.run())

    loop = asyncio.get_event_loop()
    # await asyncio.gather(asyncio.create_task(runNavigation(manager)),
    #                      asyncio.create_task(Wayfinder_UI(services_from_jason)))
    # wayfinderUI = Wayfinder_UI(services_from_jason)
    # await navigation_task
    # await fuckit_task
    # await asyncio.gather(asyncio.create_task(runNavigation(manager)),
    #                      wayfinderUI = asyncio.create_task(Wayfinder_UI(services_from_jason)))

    # asyncio.create_subprocess_exec()
    # navigation_thread.join()
    print("Ending")

    #await manager.close()

async def runNavigation(manager):
    with open("data",'a') as file:
        file.write(f"WHATS POPPINI")
    while True:
        closest_beacons = manager.get_closest()
        print("navigating")
        if not None in closest_beacons:
            print("Entering localization")
            # location = await tra_localization(closest_beacons,EMITTER_LOC_DICT)
            # print(location)
            manager.clear_closest()
            print("********************************FULL*************************************************")
        else:
            print("not full\n")



def fuckit():
    while True:
        print("Fuckit")
asyncio.run(main())
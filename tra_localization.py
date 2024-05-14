import threading
from scipy.optimize import minimize
import numpy as np
from BeaconManager import BeaconManager
import math
import time
import asyncio

from MPU.run_mpu import MpuClass
from globals import EMITTER_LOC_DICT,sharedData,SIMULATION

#Emitter locaiton dictionary
#Key        :   Value
#Mac Address:   emitter location(x,y,z(height))


# def print(input):
#     with open('logData.txt','a') as file:
#         file.write(f'{input}\n')
#     return

beaconManager = None
file1 = None
closestBeacons =  None
#signal_a, b, c should be int, name_a, b, c should be string. Emitter_location_dic is a dictionary which key: name of emitter(string)  value: location(list)

async def main():
    global beaconManager
    sharedData.closing = False
    #overrite with empty bytes
    with open('locationData','w') as file:
        file.write(f'')

    beaconManager = BeaconManager()
    mpu = MpuClass()
    # loop = asyncio.get_event_loop()
    localization_thread = threading.Thread(target=localization,args=(beaconManager,))
    localization_thread.start()
    # a = await asyncio.gather(*[beaconManager.update_beacons(),localization(beaconManager)])
    # a = asyncio.create_task(localization(beaconManager))
    b = asyncio.create_task(beaconManager.update_beacons())
    # c = asyncio.create_task(mpu.sim_mpu())
    
    # await a
    await b
    # await c

    # print(a)

        
def localization(beaconManager):
    
    position_averaging = []
    average = (50.0,-30.0,200.0)
    i = 0
    time.sleep(1)
    start_time = time.time()
    while (not sharedData.closing):
        time.sleep(.01)
        try:
            if beaconManager.closest_full():
                closestBeacons = beaconManager.get_closest()
                #print("********************************FULL*************************************************")
                end_time = time.time()
                print(f"*********Took {end_time-start_time} seconds *********")
                with open('locationData','a') as file:
                    file.write(f"*********Took {end_time-start_time} seconds *********\n")
                # print(f"Beacons: {beaconManager.get_beacons()}")
                # print(f"Closest Beacons: {beaconManager.get_closest()}")    
                print("Entering localization")
                
                location = tra_localization(closestBeacons,EMITTER_LOC_DICT)
                if len(location) ==0: continue
                
                if(len(position_averaging) == 0):
                    for i in range(0,50,1):
                        position_averaging.append(location)
                    average = location
                else:
                    last_position = position_averaging.pop(0)
                    average = (average[0] - (last_position[0]/50) + (location[0]/50), average[1] - (last_position[1]/50) + (location[1]/50), average[2] - (last_position[2]/50) + (location[2]/50))
                    position_averaging.append(location)

                sharedData.set_estimated_location(average)
                with open('locationData','a') as file:
                    file.write(f'Estimated Location: {location}\n')
                beaconManager.clear_closest()
                start_time = time.time()
            else:
                pass
                #print("not full\n")
            
            
            # with open('locationData','a') as file:
            #         file.write(f'Iteration: {i}\n')

        except KeyboardInterrupt:
            print("CLOSING")
            beaconManager.close()
            file1.close()
            return
        
        

    
def tra_localization(cloest3_beacon_list, emitter_location_dic) -> list[float]:
    
    #cloest3_beacon_list = beaconManager.closest
    indoor_scaling = 0.85
    try:
        # point a, b, c is the location of the emitter
        point_a = emitter_location_dic[cloest3_beacon_list[0][0]]
        point_b = emitter_location_dic[cloest3_beacon_list[1][0]]
        point_c = emitter_location_dic[cloest3_beacon_list[2][0]]

        # Example known points (x, y, z)
        points = np.array([point_a, point_b, point_c])

        # distance is the distance from each emitter
        dis_a = 51.044 * indoor_scaling * math.log(int(cloest3_beacon_list[0][2])) - 200.8
        dis_b = 51.044 * indoor_scaling * math.log(int(cloest3_beacon_list[1][2])) - 200.8
        dis_c = 51.044 * indoor_scaling * math.log(int(cloest3_beacon_list[2][2])) - 200.8
    except Exception as e:
        # print(e)
        return []

    # Example distances from the unknown point to each of the known points
    distances = np.array([dis_a, dis_b, dis_c])

    # Objective function: sum of squared differences between actual and calculated distances
    def itera_guessing(unknown, points, distances):
        return sum((np.linalg.norm(unknown - points[i]) - distances[i])**2 for i in range(len(points)))

    # Initial guess for the unknown point
    initial_guess = np.mean(points, axis=0)

    # Minimize the objective function
    result = minimize(itera_guessing, initial_guess, args=(points, distances))

    # Extract the estimated location of the unknown point
    estimated_location = result.x

    return (estimated_location[0], estimated_location[1], estimated_location[2]/100)
#asyncio.run(main())
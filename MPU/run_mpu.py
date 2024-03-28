import os
import sys
import time
from globals import SharedData
import smbus
import numpy as np

import MPU9255
import programKalman 



def runMpu():
    address = 0x68
    bus = smbus.SMBus(1)
    imu = MPU9255.MPU9255(bus, address)
    imu.begin()
    # imu.caliberateAccelerometer()
    # print ("Acceleration calib successful")
    # imu.caliberateMag()
    # print ("Mag calib successful")
    # or load your calibration file
    # imu.loadCalibDataFromFile("/home/pi/calib_real_bolder.json")

    sensorfusion = programKalman.programKalman()

    imu.readSensor()
    imu.computeOrientation()
    sensorfusion.roll = imu.roll
    sensorfusion.pitch = imu.pitch
    sensorfusion.yaw = imu.yaw

    count = 0
    currTime = time.time()
    while True and not SharedData.closing:
        
        imu.readSensor()
        imu.computeOrientation()
        newTime = time.time()
        dt = newTime - currTime
        currTime = newTime

        sensorfusion.computeAndUpdateRollPitchYaw(imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2], imu.GyroVals[0], imu.GyroVals[1], imu.GyroVals[2],\
                                                    imu.MagVals[0], imu.MagVals[1], imu.MagVals[2], dt)

        print("Kalmanroll:{0} KalmanPitch:{1} KalmanYaw:{2} ".format(sensorfusion.roll, sensorfusion.pitch, sensorfusion.yaw))

        time.sleep(0.01)

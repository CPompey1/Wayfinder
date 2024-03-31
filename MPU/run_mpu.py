import os
import sys
import threading
import time
from globals import IMU_ADDR, IMU_BUS, SIMULATION, sharedData
if not SIMULATION: import smbus
import numpy as np

from MPU import MPU9255
from MPU import programKalman 


class MpuClass:
    def __init__(self):
        if SIMULATION:
            return
        self.bus = smbus.SMBus(IMU_BUS)
        self.imu = MPU9255.MPU9255(self.bus,IMU_ADDR)
        self.imu.begin()
        
        self.sensorfusion = programKalman.programKalman()
        self.currTime = time.time()

        self._read_sensor()

        self.mpu_thread = threading.Thread(target=runMpu)
        self.mpu_thread.start()
    
    def get_values(self):
        if SIMULATION: 
            return(1,1,1)
        
        with sharedData.lock:
            sharedData.imu_orientation = (self.sensorfusion.roll,self.sensorfusion.pitch,self.sensorfusion.yaw)
        
        return sharedData.values

    def _read_sensor(self):
        self.imu.readSensor()
        self.imu.computeOrientation()
        self.sensorfusion.roll = self.imu.roll
        self.sensorfusion.pitch = self.imu.pitch
        self.sensorfusion.yaw = self.imu.yaw

    def kalman_filter(self):
        while True and not sharedData.closing and not SIMULATION:

            self.imu.readSensor()
            self.imu.computeOrientation()
            newTime = time.time()
            dt = newTime - currTime
            currTime = newTime

            self.sensorfusion.computeAndUpdateRollPitchYaw(self.imu.AccelVals[0], self.imu.AccelVals[1], self.imu.AccelVals[2], self.imu.GyroVals[0], self.imu.GyroVals[1], self.imu.GyroVals[2],\
                                                        self.imu.MagVals[0], self.imu.MagVals[1], self.imu.MagVals[2], dt)
            time.sleep(0.01)
    
    def close(self):
        if not sharedData.closing: sharedData.closing = True
        self.mpu_thread.join()


    


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

    currTime = time.time()
    while True and not sharedData.closing:
        
        imu.readSensor()
        imu.computeOrientation()
        newTime = time.time()
        dt = newTime - currTime
        currTime = newTime

        sensorfusion.computeAndUpdateRollPitchYaw(imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2], imu.GyroVals[0], imu.GyroVals[1], imu.GyroVals[2],\
                                                    imu.MagVals[0], imu.MagVals[1], imu.MagVals[2], dt)

        print("Kalmanroll:{0} KalmanPitch:{1} KalmanYaw:{2} ".format(sensorfusion.roll, sensorfusion.pitch, sensorfusion.yaw))


        time.sleep(0.01)
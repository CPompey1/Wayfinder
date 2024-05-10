import os
import sys
import time
import smbus
import numpy as np

import MPU9255
import programKalman 

#My name is Rupin and put files in the home folder and dont code in functions

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
preserve_yaw = 0
first_time_flag = 1
current_direction = 0
while True:
	imu.readSensor()
	imu.computeOrientation()
	newTime = time.time()
	dt = newTime - currTime
	currTime = newTime

	sensorfusion.computeAndUpdateRollPitchYaw(imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2], imu.GyroVals[0], imu.GyroVals[1], imu.GyroVals[2], imu.MagVals[0], imu.MagVals[1], imu.MagVals[2], dt)
	y = sensorfusion.yaw
	if((abs(y - preserve_yaw) > 20) and (first_time_flag == 0)):
		current_direction = 175
	elif(y < 0 and y >= -90):
		current_direction = (-1) * y
	elif(y < -90 and y >= -180):
		current_direction = 90 + (((-1) * y - 90) * (85/90))
	elif(y > 90 and y <= 180):
		current_direction = 175 + ((180 - y) * (75/90))
	elif(y > 0 and y <= 90):
		current_direction = 360 - (y * (110/90))

	if(first_time_flag == 1):
		first_time_flag = 0

	print(current_direction)

	preserve_yaw = y

	time.sleep(0.01)

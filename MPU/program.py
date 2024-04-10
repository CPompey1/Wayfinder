import FaBo9Axis_MPU9250
import time
import sys
import numpy as np

def composeOmega(gyro):
    omega = np.zeros((4,4))
    omega[0][1] = -gyro[0,0]
    omega[0][2] = -gyro[1,0]
    omega[0][3] = -gyro[2,0]
    
    omega[1][0] = gyro[0,0]
    omega[1][2] = gyro[2,0]
    omega[1][3] = -gyro[1,0]
    
    omega[2][0] = gyro[1,0]
    omega[2][1] = -gyro[2,0]
    omega[2][3] = gyro[0,0]
    
    omega[3][0] = gyro[2,0]
    omega[3][1] = gyro[1,0]
    omega[3][2] = -gyro[0,0]
    return omega

def composeJacobian_1(q):
    jacb = np.zeros((3,4))
    jacb[0][0] = -2*q[2,0]
    jacb[0][1] = 2*q[3,0]
    jacb[0][2] = -2*q[0,0]
    jacb[0][3] = 2*q[1,0]
    
    jacb[1][0] = 2*q[1,0]
    jacb[1][1] = 2*q[0,0]
    jacb[1][2] = 2*q[3,0]
    jacb[1][3] = 2*q[2,0]
    
    jacb[2][0] = 2*q[0,0]
    jacb[2][1] = -2*q[1,0]
    jacb[2][2] = -2*q[2,0]
    jacb[2][3] = 2*q[3,0]
    return jacb

def composeJacobian_2(q):
    jacb = np.zeros((3,4))
    jacb[0][0] = 2*q[3,0]
    jacb[0][1] = 2*q[2,0]
    jacb[0][2] = 2*q[1,0]
    jacb[0][3] = 2*q[0,0]

    jacb[1][0] = 2*q[0,0]
    jacb[1][1] = -2*q[1,0]
    jacb[1][2] = -2*q[2,0]
    jacb[1][3] = -2*q[3,0]

    jacb[2][0] = -2*q[1,0]
    jacb[2][1] = -2*q[0,0]
    jacb[2][2] = 2*q[3,0]
    jacb[2][3] = 2*q[2,0]
    return jacb

#The estimated gravity
def composeGravity(q):
    h = np.zeros((3,1))
    h[0] = 2*q[1,0]*q[3,0] - 2*q[0,0]*q[2,0]
    h[1] = 2*q[0,0]*q[1,0] + 2*q[2,0]*q[3,0]
    h[2] = q[0,0]*q[0,0] - q[1,0]*q[1,0] - q[2,0]*q[2,0]+q[3,0]*q[3,0]
    return h

#The estimated magnetic field
def composeMagnet(q):   
    h = np.zeros((3,1))
    h[0] = 2*q[1,0]*q[2,0] + 2*q[0,0]*q[3,0]
    h[1] = q[0,0]*q[0,0] - q[1,0]*q[1,0] - q[2,0]*q[2,0] - q[3,0]*q[3,0]
    h[2] = 2*q[2,0]*q[3,0] - 2*q[0,0]*q[1,0]
    return h

mpu9250 = FaBo9Axis_MPU9250.MPU9250()
dt = 0.01
I_4 = np.identity(4)
q_pri = np.matrix([[1],[0],[0],[0]])
q_cor = np.matrix([[1],[0],[0],[0]])
q_post = np.matrix([[1],[0],[0],[0]])
P_pri = np.zeros((4,4))
P_post = np.zeros((4,4))
Q = np.matrix([[0.001,0,0,0],[0,0.001,0,0],[0,0,0.001,0],[0,0,0,0.0001]])
R = np.matrix([[1,0,0],[0,1,0],[0,0,0.01]])
lol = 100
x0 = 0
x1 = 0
x2 = 0
x3 = 0
x4 = 0
x5 = 0
xAdj = 0.0
yAdj = 0.0
zAdj = 0.0
gyroX = 0.1
gyroY = 0.1
gyroZ = 0.1

try:
    while(True):
        accel_values = mpu9250.readAccel()
        #print (" ax = " , ( accel_values['x'] ))
        #print (" ay = " , ( accel_values['y'] ))
        #print (" az = " , ( accel_values['z'] ))

        gyro_values = mpu9250.readGyro()
        #print (" gx = " , ( gyro_values['x'] / 57.2958 ))
        #print (" gy = " , ( gyro_values['y'] / 57.2958 ))
        #print (" gz = " , ( gyro_values['z'] / 57.2958 ))

        mag_values = mpu9250.readMagnet()
        #print (" mx = " , ( mag_values['x'] ))
        #print (" my = " , ( mag_values['y'] ))
        #print (" mz = " , ( mag_values['z'] ))

        gyroX = np.round((gyro_values['x'] / 57.2958) - xAdj, 2);
        gyroY = np.round((gyro_values['y'] / 57.2958) - yAdj, 2);
        gyroZ = np.round((gyro_values['z'] / 57.2958) - zAdj, 2);
        gyro = np.matrix([[gyroX],[gyroX],[gyroX]])
        accel = np.matrix([[accel_values['x']],[accel_values['y']],[accel_values['z']]])
        magnet = np.matrix([[mag_values['x']],[mag_values['y']],[mag_values['z']]])
        
        omega = composeOmega(gyro)
        A = I_4 + 0.5*dt*omega
        q_pri = A*q_post
        P_pri = A*P_post*np.transpose(A) + Q
        
        H = composeJacobian_1(q_pri)
        K = P_pri*np.transpose(H)*np.linalg.inv((H*P_pri*np.transpose(H) + R))
        h = composeGravity(q_pri)
        q_cor = K*(accel - h)
        q_cor[3] = 0
        q_post = q_cor + q_pri
        P_post = (I_4 - K*H)*P_pri

        H = composeJacobian_2(q_pri)
        K = P_pri*np.transpose(H)*np.linalg.inv((H*P_pri*np.transpose(H)+R))
        h = composeMagnet(q_pri)
        q_cor = K*(magnet - h)
        q_cor[1] = 0
        q_cor[2] = 0
        q_post = q_cor + q_post
        P_post = (I_4 - K*H)*P_post

        X = np.zeros((3,1))
        X[0] = np.arctan2(2*(q_post[2]*q_post[3]+q_post[0]*q_post[1]), q_post[0]*q_post[0]-q_post[1]*q_post[1]-q_post[2]*q_post[2]+q_post[3]*q_post[3])
        X[1] = np.arcsin(2*(q_post[0]*q_post[2]-q_post[1]*q_post[3])/(q_post[0]*q_post[0]+q_post[1]*q_post[1]+q_post[2]*q_post[2]+q_post[3]*q_post[3]))
        X[2] = np.arctan2(2*(q_post[1]*q_post[2]+q_post[0]*q_post[3]), q_post[0]*q_post[0]+q_post[1]*q_post[1]-q_post[2]*q_post[2]-q_post[3]*q_post[3])

        if(np.abs(X[0] * 57.2958 - x0) > 5 or np.abs(X[1] * 57.2958 - x1) > 5 or np.abs(X[2] * 57.2958 - x2) > 5):
            x0 = X[0] * 57.2958
            x1 = X[1] * 57.2958
            x2 = X[2] * 57.2958
            print((X[0] - x3) * 57.2958, end = " ")
            print((X[1] - x4) * 57.2958, end = " ")
            print((X[2] - x5) * 57.2958)
            #print ("gx = " , ( gyro_values['x']), end = ", ")
            #print ("gy = " , ( gyro_values['y']), end = ", ")
            #print ("gz = " , ( gyro_values['z']))
        lol = lol - 1
        
        #if (lol == 0):
        #    xAdj = gyroX
        #    yAdj = gyroY
        #    zAdj = gyroZ
        if (lol == -100):
            x3 = X[0]
            x4 = X[1]
            x5 = X[2]
        
        time.sleep(0.01)
        

except KeyboardInterrupt:
    sys.exit()

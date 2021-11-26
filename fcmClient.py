#!/usr/bin/env python3
'''
ArduPilot sitl and FlightLab connector
based on robot.py from ardupilot JSON examples
based on fcmClientSimulink.slx
'''

from os import times
import socket
import struct
import json
import time
import argparse
import os.path
from typing import final
import numpy as np

from helicopter import Helicopter

G = -9.80665 #normal gravity
FT = 0.3048 #ft2meter
DEG = 0.0174532925 #deg2rad
last_print = 0 #print in console
last_print2 = 0 #print to file

clamp = lambda n, minn, maxn: max(min(maxn, n), minn)

##
#xb = 79.540
#xb = 50 #60.64954972257144
#xa = 69.104
#xa = 50 #60.64795164131181
#xc = 51.316
#xc = 25 #39.93111249885035
#xp = 81.074
#xp = 62 #70.42098240571202
windx = 0.0
windy = 0.0
windz = 0.0

mode = 'init'
#xbtrim = 0.01 * DEG #-0.0658 in hover
#xatrim = 0.01 * DEG # 0.02
#xctrim = -10 * DEG #6.53
#xptrim = 0.01 * DEG #6.3

xbtrim = 50
xatrim = 50
xctrim = 40
xptrim = 46

direct = 0.0

parser = argparse.ArgumentParser(description="AP-FL Connector")
parser.add_argument("--ip", default='10.21.0.81', help="fcmserver ip") #172.22.2.112
parser.add_argument('--config', '-c', dest='config', \
  help='Config .json file, default archer_new.json', \
  default=os.path.join(os.path.dirname(__file__), 'archer_new.json'))
args = parser.parse_args()

sock_AP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_AP.bind(('', 9002))
sock_AP.settimeout(0.1)

sock_FL = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_FL.bind(('', 7101))
sock_FL.settimeout(0.1)

#parse_format_FL = 'ii80d' #format of FL out sw4
parse_format_FL = 'ii54d' #format of FL out Archer
parse_format_AP = 'HHI16H' #format of AP out
magic = 18458

last_SITL_frame = -1
connected = False
frame_count = 0

heli_config = json.load(open(args.config, 'r'))
heli = Helicopter(heli_config)
print('Created Helicopter with config ' + args.config)

timestr = time.strftime("%Y%m%d-%H%M%S") + '.log'
print('Loging into file ' + timestr)
assert not os.path.isfile(timestr) #check if log file already exists


with open(timestr, 'w') as outfile:
  line = 't,frame,xb,xa,xc,xp,'\
          'pwm1,pwm2,pwm3,pwm4,'\
          'p,q,r,accx,accy,accz,x,y,z,roll,pitch,yaw,vx,vy,vz,'\
          'theta1,theta2,b1s1,a1s1\n' # 25 columns # deleted xd,windx,windy,windz,pwm5,
  outfile.write(line)
  while True:

    # Receive control from AP
    try:
        control, address_AP = sock_AP.recvfrom(1024)
    except Exception as ex:
        time.sleep(0.01)
        continue
    
    if len(control) != struct.calcsize(parse_format_AP):
      print("got packet of len %u, expected %u" % (len(control), struct.calcsize(parse_format_AP)))
      continue

    control_decoded = struct.unpack(parse_format_AP,control)

    if magic != control_decoded[0]:
      print("Incorrect protocol magic %u should be %u" % (control_decoded[0], magic))
      continue

    frame_rate_hz = control_decoded[1]
    frame_count = control_decoded[2]
    pwm = control_decoded[3:]

    # Check if the frame is in expected order
    if frame_count < last_SITL_frame:
      ## As for now break the program
      try:
        sock_FL.sendto(struct.pack('<ii16d', 0,0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0), (args.ip, 7100) )
      finally:
        raise NameError('Err in frame count')
      # Controller has reset, reset physics also
      #FIXME
      #sock_FL.sendto(struct.pack('<ii18d', 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), (args.ip, 7100) )
      #print('Controller reset')   
    ## For now lest have this is turned of
    # elif frame_count == last_SITL_frame: 
      #try:
      #  sock_FL.sendto(coerce, (args.ip, 7100) )
      #except:
      #  sock_FL.sendto(struct.pack('<ii18d', 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), (args.ip, 7100) )
      #print('Duplicate input frame')
      #continue
    elif frame_count != last_SITL_frame + 1 and connected:
      print('Missed {0} input frames'.format(frame_count - last_SITL_frame - 1))
    last_SITL_frame = frame_count

    if not connected:
      connected = True
      print('Connected to {0}'.format(str(address_AP)))
    
    frame_count += 1

    #pwm->controlFL
    control_pwm = np.array([
      int(pwm[0]),
      int(pwm[2]),
      int(pwm[1])
    ]) #according to Marek aileron, elevator, collective is motor 1, 3, 2
    pitch = np.rad2deg(heli.calc_pitch(control_pwm))
    angles = (pitch[0], pitch[1], pitch[2], heli.calc_tail(pwm[3])) #coll, cyc pitch +nose up, cyc roll +right, pedal +E

    #TODO wind

    #TODO push prop
    #xd = 0.0
    
    #Send control to FL

    #TODO struct for Archer

    #FIXME change degree to percent
    xc = 7.142857142857143 * angles[0] + 14.285714285714286 #coll
    xc = clamp(xc, 0.0, 100.0)
    xb = 6.25 * angles[1] + 50.0 #long
    xb = clamp(xb, 0.0, 100.0)
    xa = 10.0 * angles[2] + 50.0 #lat
    xa = clamp(xa, 0.0, 100.0)
    xp = 2.0 * angles[3] + 40.0 #ped
    xp = clamp(xp, 0.0, 100.0)

    ## ! ## FIXME
    #xa = 100.0 - xa
    #xb = 100.0 - xb

    if mode == 'init':
      coerce = struct.pack('ii16d', 1, 0, xbtrim, xatrim, xctrim, xptrim, direct, 2116.2, 518.67, windx, windy, windz, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0)
      if angles[0] <= 0:
        mode = 'acro'
        print('MODE ACRO')
    elif mode == 'acro':
      coerce = struct.pack('ii16d', 1, 0, xbtrim, xatrim, xctrim, xptrim, direct, 2116.2, 518.67, windx, windy, windz, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0)
      if angles[0] > 0.5:
        mode = 'flight'
        print('MODE FLIGHT')
    else:
      coerce = struct.pack('ii16d', 1, 0, xb, xa, xc, xp, direct, 2116.2, 518.67, windx, windy, windz, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0)
    
    #constat values for FL are hardcoded and explained in fcmtest.py
    #coerce = struct.pack('<ii18d',  #little endian
    #                      1, 0,
    #                     xb, xa, xc, xp, 110.0, 0.0, 2.0, 0.0, 0.0, #long (nose), lat, coll, pedal
    #                      0.0, 0.0, 0.0, 0.0, 0.0, -1.0, windx, windy, windz)

    #assert len(coerce) == 152  #expected packet length in sw4_simulink
    
    sock_FL.sendto(coerce, (args.ip, 7100) )

    #Receive state from FL
    try:
        state, address_FL = sock_FL.recvfrom(1024)
    except Exception as ex:
        time.sleep(0.01)
        continue

    port_FL = address_FL[1]

    if len(state) != struct.calcsize(parse_format_FL):
        print("got packet of len %u, expected %u" % (len(state), struct.calcsize(parse_format_FL)))
        continue

    state_decoded = struct.unpack(parse_format_FL,state)

    #gyro = state_decoded[20:23] #body axis pqr roll pitch yaw +right +up +E rad/s
    #accel = ([FT * x for x in state_decoded[14:17]]) #body axis m/sec2 "NED" +forward + right +down
    #tim = state_decoded[81] #sec
    #pos = ([FT * x for x in state_decoded[2:5]]) #NED m
    #euler = state_decoded[5:8] #rad
    #vel = ([FT * x for x in state_decoded[8:11]]) #m/s NED

#FIXME tutaj gyro i acc powinny byc body prawda? a nie inertial

    gyro = state_decoded[20:23] #body axis pqr roll pitch yaw +right +up +E rad/s
    accel = ([FT * x for x in state_decoded[14:17]]) #body axis m/sec2 "NED" +forward + right +down
    tim = state_decoded[55] #sec
    pos = ([FT * x for x in state_decoded[2:5]]) #NED m
    euler = state_decoded[5:8] #rad phi theta psi
    vel = ([FT * x for x in state_decoded[8:11]]) #m/s NED
    deflect = state_decoded[43:47]

    #add gravity vector to accel
    accel[0] = accel[0] - np.sin(euler[1]) * G
    accel[1] = accel[1] + np.cos(euler[1]) * np.sin(euler[0]) * G
    accel[2] = accel[2] + np.cos(euler[1]) * np.cos(euler[0]) * G

    ##
    #gyro = (0,0,0)
    #accel = (0,0,-9.81)
    #vel = (0,0,0)
    #euler = (0,0,0)
    #pos = (0,0,0)
    
    # build JSON format and send to AP
    IMU_fmt = {
      "gyro" : gyro,
      "accel_body" : accel
    }
    JSON_fmt = {
      "timestamp" : tim,
      "imu" : IMU_fmt,
      "position" : pos,
      "attitude" : euler,
      "velocity" : vel
    }
    JSON_string = "\n" + json.dumps(JSON_fmt,separators=(',', ':')) + "\n"

    sock_AP.sendto(bytes(JSON_string,"ascii"), address_AP)

    #Saving to CSV file #TODO pwm[4] for xd control

    #'t,frame,'\
    #      'xb,xa,xc,xp,xd,'\
    #      'windx,windy,windz,'\
    #      'pwm1,pwm2,pwm3,pwm4,pwm5,'\
    #      'p,q,r,accx,accy,accz,x,y,z,roll,pitch,yaw,vx,vy,vz,'\
    #      'theta1,theta2,b1s1,a1s1\n' 30 columns

    if frame_count % 20 == 0 or frame_count <= 10:
      outfile.write(f'{tim},{frame_count},{angles[1]},{angles[2]},{angles[0]},{angles[3]},'\
        f'{pwm[0]},{pwm[1]},{pwm[2]},{pwm[3]},'\
        f'{gyro[0]},{gyro[1]},{gyro[2]},{accel[0]},{accel[1]},{accel[2]},'\
        f'{pos[0]},{pos[1]},{pos[2]},{euler[0]},{euler[1]},{euler[2]},'\
        f'{vel[0]},{vel[1]},{vel[2]},{deflect[0]},{deflect[1]},{deflect[2]},{deflect[3]},\n')
      #last_print2 = state_decoded[55] #FIXME bylo bez decoded!
    if frame_count % 50 == 0:
      print(frame_rate_hz)

    #if frame_count % 5000 == 0:
      #print(JSON_string)
      #last_print = state_decoded[55] #FIXME bylo bez decoded!
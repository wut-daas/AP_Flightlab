#!/usr/bin/env python3
'''
ArduPilot sitl and FlightLab connector
based on robot.py from ardupilot JSON examples
based on fcmClientSimulink.slx
'''

import socket
import struct
import json
import time
import argparse
import os.path

FT = 0.3048

##
xb = 79.540
xa = 69.104
xc = 51.316
xp = 81.074
windx = 0.0
windy = 0.0
windz = 0.0

parser = argparse.ArgumentParser(description="AP-FL Connector")
parser.add_argument("--ip", default='172.22.2.112', help="fcmserver ip")
parser.add_argument('--config', '-c', dest='config', help='Config .json file, default archer.json', \
  default=os.path.join(os.path.dirname(__file__), 'archer.json'))
args = parser.parse_args()

sock_AP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_AP.bind(('', 9002))
sock_AP.settimeout(0.1)

sock_FL = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_FL.bind(('', 7101))
sock_FL.settimeout(0.1)

parse_format_FL = 'ii80d' #format of FL out
parse_format_AP = 'HHI16H' #format of AP out
magic = 18458

last_SITL_frame = -1
connected = False
frame_count = 0

heli_config = json.load(open(args.config, 'r'))
heli = Helicopter(heli_config)
print('Created Helicopter with config ' + args.config)

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
    print("Incorrect protocol magic %u should be %u" % (control[0], magic))
    continue

  frame_rate_hz = control_decoded[1]
  frame_count = control_decoded[2]
  pwm = control_decoded[3:]

  # Check if the fame is in expected order
  if frame_count < last_SITL_frame:
    raise NameError('Err in frame count')
  #elif frame_count == last_SITL_frame:
    print('Duplicate input frame')
    continue
  elif frame_count != last_SITL_frame + 1 and connected:
    print('Missed {0} input frames'.format(frame_count - last_SITL_frame - 1))
  last_SITL_frame = frame_count

  if not connected:
    connected = True
    print('Connected to {0}'.format(str(address_AP)))
  frame_count += 1

  #TODO pwm->controlFL

  #TODO wind
  
  #Send control to FL 
  #constat values for FL are hardcoded and explained in fcmtest.py
  coerce = struct.pack('<ii18d',  #little endian
                        1, 0,
                        xb, xa, xc, xp, 110.0, 0.0, 2.0, 0.0, 0.0, #long (nose), lat, coll, pedal
                        0.0, 0.0, 0.0, 0.0, 0.0, -1.0, windx, windy, windz)

  assert len(coerce) == 152  #expected packet length in simulink
  
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

  gyro = state_decoded[20:23] #body axis pqr roll pitch yaw +right +up +E rad/s
  accel = ([FT * x for x in state_decoded[14:17]]) #body axis m/sec2 "NED" +forward + right +down
  tim = state_decoded[81] #sec
  pos = ([FT * x for x in state_decoded[2:5]]) #NED m
  euler = state_decoded[5:8] #rad
  vel = ([FT * x for x in state_decoded[8:11]]) #m/s NED

  gyro = (0.0,0.0,0.0)
  accel = (0.0,0.0,0.0)
  vel = (0.0,0.0,0.0)
  euler = (0.0,0.0,0.0)
  pos = (0.0,0.0,0.0)
  
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

  #TODO zapis do pliku csv
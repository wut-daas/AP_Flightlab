#!/usr/bin/env python3
'''
based on robot.py from ardupilot JSON examples
based on fcmClientSimulink.slx
'''

import socket
import struct
import json

import time

import argparse

parser = argparse.ArgumentParser(description="fcmClient settings")
parser.add_argument("--fps", type=float, default=1000.0, help="physics frame rate")

args = parser.parse_args()

RATE_HZ = args.fps
TIME_STEP = 1.0 / RATE_HZ

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 9002))
sock.settimeout(0.1)

sockFL = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockFL.bind(('', 7101))
sockFL.settimeout(0.1)

while True:

  py_time = time.time()

  try:
      control,address = sock.recvfrom(100)
  except Exception as ex:
      time.sleep(0.01)
      continue

  parse_format = 'HHI16H'
  magic = 18458

  if len(control) != struct.calcsize(parse_format):
    print("got packet of len %u, expected %u" % (len(control), struct.calcsize(parse_format)))
    continue


  decoded = struct.unpack(parse_format,control)

  if magic != decoded[0]:
      print("Incorrect protocol magic %u should be %u" % (decoded[0], magic))
      continue

  frame_rate_hz = decoded[1]
  frame_count = decoded[2]
  pwm = decoded[3:]

  try:
      state,address = sockFL.recvfrom(100)
  except Exception as ex:
      time.sleep(0.01)
      continue

  #parse_format = 'ii24d9d3d8d20d4d4d3d5d' #according to simulink
  parse_formatFL = '24d3d8d16d4d4d3d5d' #according to configure file
  
  if len(state) != struct.calcsize(parse_formatFL):
    print("got packet of len %u, expected %u" % (len(state), struct.calcsize(parse_formatFL)))
    continue

  decoded = struct.unpack(parse_format,state)
  
  # build JSON format
  IMU_fmt = {
    "gyro" : gyro,
    "accel_body" : accel
  }
  JSON_fmt = {
    "timestamp" : phys_time,
    "imu" : IMU_fmt,
    "position" : pos,
    "attitude" : euler,
    "velocity" : velo
  }
  JSON_string = "\n" + json.dumps(JSON_fmt,separators=(',', ':')) + "\n"

  # Send to AP
  sock.sendto(bytes(JSON_string,"ascii"), address)
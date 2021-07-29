#!/usr/bin/env python3
'''
test communication between ap
'''

import socket
import struct
import json

import time

from math import sin, cos, pi

RATE_HZ = 60
TIME_STEP = 1.0 / RATE_HZ

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 9002))
sock.settimeout(0.1)

last_SITL_frame = -1
connected = False
frame_count = 0
frame_time = time.time()
print_frame_count = 1000
time_now = 0
radius = 20
oscilation = 10

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

  if frame_rate_hz != RATE_HZ:
      print("New frame rate %u" % frame_rate_hz)
      RATE_HZ = frame_rate_hz
      TIME_STEP = 1.0 / RATE_HZ

  # Check if the fame is in expected order
  if frame_count < last_SITL_frame:
    # Controller has reset, reset physics also
    time_now = 0
    print('Controller reset')
  elif frame_count == last_SITL_frame:
    # duplicate frame, skip
    print('Duplicate input frame')
    continue
  elif frame_count != last_SITL_frame + 1 and connected:
    print('Missed {0} input frames'.format(frame_count - last_SITL_frame - 1))
  last_SITL_frame = frame_count
  
  if not connected:
    connected = True
    print('Connected to {0}'.format(str(address)))
  frame_count += 1

  # forced vehicle movement for testing
  
  time_now += TIME_STEP
  gyro = (0,0,0)
  accel = (0,0,0)
  velo = (0,0,0)
  alpha = 2 * pi * ((time_now % oscilation) / oscilation)
  pos = (R * cos(alpha), R * sin(alpha), 10)

  # build JSON format
  IMU_fmt = {
    "gyro" : gyro,
    "accel_body" : accel
  }
  JSON_fmt = {
    "timestamp" : time_now,
    "imu" : IMU_fmt,
    "position" : pos,
    "attitude" : euler,
    "velocity" : velo
  }
  JSON_string = "\n" + json.dumps(JSON_fmt,separators=(',', ':')) + "\n"

  # Send to AP
  sock.sendto(bytes(JSON_string,"ascii"), address)

  # Track frame rate
  if frame_count % print_frame_count == 0:
    now = time.time()
    total_time = now - frame_time
    print("%.2f fps T=%.3f dt=%.3f" % (print_frame_count/total_time, phys_time, total_time))
    frame_time = now

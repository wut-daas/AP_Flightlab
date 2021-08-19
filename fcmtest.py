import socket
import struct
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind(('172.22.2.112', 7100)) #port by instruction
ip = '172.22.2.112'
#ip = '194.29.154.3'
port = 7101 #21022
sock.bind(('', port)) #port of shell
#sock.connect((ip,port))
sock.settimeout(0.1)

last_print = 0

instr_status = 1
handshake = 0
xb = 79.540
xa = 69.104
xc = 51.316
xp = 81.074
englever = 110.0
trim = 0.0
clutch = 2.0
usrin = 0.0
ftrigger = 0.0

t1 = 0.0
t2 = 0.0
t3 = 0.0
t4 = 0.0
t5 = 0.0
t6 = -1.0

windx = 0.0
windy = 0.0
windz = 0.0

parse_format = 'ii80d' # format of FL out

while True: 

    data = struct.pack('<ii18d',  # little endian
                        instr_status, handshake,
                        xb, xa, xc, xp, englever, trim, clutch, usrin, ftrigger,
                        t1, t2, t3, t4, t5, t6, windx, windy, windz)

    assert len(data) == 152  # expected packet length in simulink

    sock.sendto(data, (ip,7100) )

    try:
        data, address = sock.recvfrom(1024)
    except Exception as ex:
        time.sleep(0.01)
        continue

    if (ip, port) != address:
        print('Different address received, new address: (%s, %s)' % (address[0], address[1]))
        ip = address[0]
        port = address[1]

    if len(data) != struct.calcsize(parse_format):
        print("got packet of len %u, expected %u" % (len(data), struct.calcsize(parse_format)))
        continue

    decoded = struct.unpack(parse_format,data)

    #print("POS: ", decoded[2:5], " ATT: ", decoded[5:8], " CTRL: ", decoded[77:81], " TIME: ", decoded[81])

    # Track frame rate
    if decoded[81] - last_print > 0.1:
        print("VEL: ", decoded[8:11],)
        last_print = decoded[81]

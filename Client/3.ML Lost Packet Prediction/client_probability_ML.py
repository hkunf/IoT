# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 12:36:05 2021

@author: vamshi
"""
# generate constant public and private key
# shuffle tag list based on seed and attach to message list
### UDP client

import socket
import os
import hashlib
import random
import pyRAPL
from ESHA256 import getESHA256

# Message to be sent has to be sent in 'bytesToSend'
serverAddressPort = ("127.0.0.1", 20001)
bufferSize = 1024

def calc_delay(signal):
    rate = 0.18 * (float(signal) + 46) / 70  # Bandwidth = 0.18M, tx power signals = 46 dBm and 23 dBm, divide by difference (gain) of 70dBm
    return rate

rate_cmd = 'iwconfig wlan0 rate %sM" % calc_delay(signal)'
os.system(rate_cmd)


def prepend(lst, str):
    # Using format()
    str += '{0}'
    lst = [str.format(i) for i in lst]
    return lst

pyRAPL.setup()
filename = 'E-Client.csv'
if os.path.exists(filename):
    os.remove(filename)
csv_output = pyRAPL.outputs.CSVOutput(filename)

@pyRAPL.measureit(number=1, output=csv_output)
def Client():
    ESHA = True

    m = []
    h = []
    t = []
    e = []
    s = []

    message1 = '33'  # 'Lorem Ipsum text'
    message2 = '34'
    message3 = '35'
    message4 = '36'

    # Split bytesToSend to 4 fragments and store in msg[]
    m.append(message1)
    m.append(message2)
    m.append(message3)
    m.append(message4)

    print(m)
    print(message1)
    # Calculate hash
    print(m)
    msg_hash = getESHA256(message1, ESHA)

    # Fragment message
    frag = 4

    # Fragment hash
    length = len(msg_hash)
    n = int(length / frag)
    i = 0
    while i < frag:
        h.append(msg_hash[i * n:(i + 1) * n])
        i += 1

    str = '0x'
    h = prepend(h, str)
    print(f"\nHK Prepend 0x h = {h}")

    # Calculate tags from hash fragments
    t.append(hex(int(h[0], 16)))
    t.append(hex(int(h[1], 16) ^ int(h[0], 16)))
    t.append(hex(int(h[2], 16) ^ int(h[1], 16) ^ int(h[0], 16)))
    t.append(hex(int(h[3], 16) ^ int(h[2], 16) ^ int(h[1], 16) ^ int(h[0], 16)))

    print(f"\nHK t = {t}")

    random.shuffle(t)  # shuffle with default RNG

    print(f"\nHK t = {t}")

    # Append message, tag, and signature
    e = [x + y for x, y in zip(m, t)]
    print(f"\nHK e = {e}")

    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # send packets
    UDPClientSocket.sendto(e[0].encode(), serverAddressPort)
    UDPClientSocket.sendto(e[1].encode(), serverAddressPort)
    UDPClientSocket.sendto(e[2].encode(), serverAddressPort)
    UDPClientSocket.sendto(e[3].encode(), serverAddressPort)

    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    msg = "Message from Server {}".format(msgFromServer[0])
    print(msg)

for _ in range(1):
    Client()

csv_output.save()
print("\nEnd...")

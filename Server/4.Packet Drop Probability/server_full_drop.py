# -*- coding: utf-8 -*-
"""
Spyder Editor
"""

### UDP server

import socket
import os
import hashlib
import math
import pyRAPL
from ESHA256 import getESHA256

# Constants
frag = 4

# Set IP, port, and buffer size
localIP = "192.168.1.71"
localPort = 3003
bufferSize = 4096

# Set transmission rate to simulate NB-IoT performance
def calc_delay(signal):
    rate = 0.18 * (float(signal) + 46) / 40  # Bandwidth = 0.18M, rx power signals = 46 dBm and 23 dBm, divide by difference (gain) of 40dBm
    return rate

rate_cmd = 'iwconfig wlan0 rate %sM" % calc_delay(signal)'
os.system(rate_cmd)

# Declare message to be sent to sender upon receiving a packet
msgFromServer = "Success..."
bytesToSend = str.encode(msgFromServer)

# Message when SINR is very low
M = "All packets not received"
feedback = str.encode(M)

# When number of times packets dropped is equal to 2
M1 = "Packets dropped twice, chances of packet drop attack"
feedback1 = str.encode(M1)

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and IP
UDPServerSocket.bind((localIP, localPort))

print("UDP listening")
pyRAPL.setup()
filename = 'ServerFull.csv'

if os.path.exists(filename):
    os.remove(filename)

csv_output = pyRAPL.outputs.CSVOutput(filename)

@pyRAPL.measureit(number=250, output=csv_output)
def Server():
    ESHA = False
    t = []
    h = []
    c = []
    
    # Listen for incoming datagrams - full authentication
    i = 0
    z = 0
    
    while i < frag:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        cipher = bytesAddressPair[0].decode()
        address = bytesAddressPair[1]
        if len(cipher) > 0:
            z += 1
            i += 1   
            msg = cipher[0:14]
            c.append(cipher[14:])    
        else:           	
            UDPServerSocket.sendto(M.encode(), address)
            c.clear()
            i = 0
            
    
    UDPServerSocket.sendto(bytesToSend, address)
    msg_hash = getESHA256(msg, ESHA)
    length = len(msg_hash)
    n = int(length / frag)
    i = 0

    while i < frag:
        h.append(msg_hash[i * n:(i + 1) * n])
        i += 1

    t.append(hex(int(h[0], 16)))
    t.append(hex(int(h[1], 16) ^ int(h[0], 16)))
    t.append(hex(int(h[2], 16) ^ int(h[1], 16) ^ int(h[0], 16)))
    t.append(hex(int(h[3], 16) ^ int(h[2], 16) ^ int(h[1], 16) ^ int(h[0], 16)))

    print(f"\nHK T = {t}\n")
    print(f"\nHK C = {c}\n")
    
    i=0
    for i in range(4):
        if c[i] == t[i]:  # SHA 256
            print(f"message {i + 1} verified")
        else:
            print(f"message {i + 1} not verified")

for _ in range(1):
    Server()

csv_output.save()
print("\nEnd...")


# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 12:36:05 2021

@author: vamshi
"""

# Generate constant public and private key

# Frequent communications - full hash, less communications - truncated hash (75% length of full hash)
# Light-weight node and less communications - truncated hash (50% length of full hash)

### UDP client

import socket
import os
import hashlib
import pyRAPL
from ESHA256 import getESHA256

# Message to be sent has to be sent in 'bytesTo Send'
serverAddressPort = ("192.168.1.71", 3003)
bufferSize = 1024

def calc_delay(signal):
    rate = 0.18 * (float(signal) + 46) / 70  # Bandwidth = 0.18M, tx power signals = 46 dBm and 23 dBm, divide by difference (gain) of 70dBm
    return rate

rate_cmd = 'iwconfig wlan0 rate %sM" % calc_delay(signal)'
os.system(rate_cmd)

def prepend(list, str):
    # Using format()
    str += '{0}'
    list = [str.format(i) for i in list]
    return list

pyRAPL.setup()
filename = 'Client.csv'
if os.path.exists(filename):
    os.remove(filename)
csv_output = pyRAPL.outputs.CSVOutput(filename)

@pyRAPL.measureit(number=250, output=csv_output)
def Client():
    ESHA = False
    message1 = 'LoremIpsumtext'
    message2 = 'LoremIpsumtext'
    message3 = 'LoremIpsumtext'
    message4 = 'LoremIpsumtext'
    message = ''

    # Calculate hash
    msg_hash = getESHA256(message1, ESHA)

    # Fragment message
    frag = 4

    m = []
    h = []
    t = []
    e = []

    # Split bytesToSend to 4 fragments and store in msg[]
    m.append(message1)
    m.append(message2)
    m.append(message3)
    m.append(message4)

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

    # Append message, tag and signature
    e = [x + y for x, y in zip(m, t)]
    print(f"\nHK e = {e}")

    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    q = 0
    # Send packets
    while q < 3:
        if q == 0:
            UDPClientSocket.sendto(e[0].encode(), serverAddressPort) 
            UDPClientSocket.sendto(e[1].encode(), serverAddressPort)
            UDPClientSocket.sendto(e[2].encode(), serverAddressPort)
            UDPClientSocket.sendto(message.encode(), serverAddressPort)
            msgFromServer = UDPClientSocket.recvfrom(bufferSize)
            msg = "\nMessage from Server {}".format(msgFromServer[0])
            print(msg)
            print("Retransmitting packets again")                
        elif q == 1:   
            UDPClientSocket.sendto(e[0].encode(), serverAddressPort) 
            UDPClientSocket.sendto(e[1].encode(), serverAddressPort)
            UDPClientSocket.sendto(e[2].encode(), serverAddressPort)
            UDPClientSocket.sendto(message.encode(), serverAddressPort) 
            msgFromServer = UDPClientSocket.recvfrom(bufferSize)
            msg = "\nMessage from Server {}".format(msgFromServer[0])
            print(msg)
            print("Packets dropped twice, chances of packet drop attack\nMessages stored for next transaction")                          
        else:
            UDPClientSocket.sendto(e[0].encode(), serverAddressPort)
            UDPClientSocket.sendto(e[1].encode(), serverAddressPort)
            UDPClientSocket.sendto(e[2].encode(), serverAddressPort)
            UDPClientSocket.sendto(e[3].encode(), serverAddressPort)
            msgFromServer = UDPClientSocket.recvfrom(bufferSize)
            msg = "\nMessage from Server {}".format(msgFromServer[0])
            print(msg)            
                  
        q += 1
    

for _ in range(1):
    Client()

csv_output.save()
print("\nEnd...")


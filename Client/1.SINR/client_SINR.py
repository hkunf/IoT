# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 12:36:05 2021

@author: vamshi
"""

# generate constant public and private key


# frequent communications - full hash, less communications - truncated hash (75% length of full hash)
# light-weight node and less communications - truncated hash (50% length of full hash)


### UDP client

import socket
import os
import hashlib
import pyRAPL
from ESHA256 import getESHA256


# message to be sent has to be sent in 'bytesTo Send'
serverAddressPort   = ("192.168.1.71", 3003)
bufferSize          = 1024

def calc_delay(signal):
   rate = 0.18 * ( float(signal) + 46 ) / 70    # bandwidth = 0.18M, tx power signals = 46 dBm and 23 dBm,divide by difference (gain) of 70dBm
   return(rate)

rate_cmd = 'iwconfig wlan0 rate %sM" % calc_delay(signal)'
os.system(rate_cmd)

def prepend(list, str):
    # Using format()
    str += '{0}'
    list = [str.format(i) for i in list]
    return(list)

pyRAPL.setup()
filename = 'Client.csv'
if os.path.exists(filename):
    os.remove(filename)
csv_output = pyRAPL.outputs.CSVOutput(filename)
@pyRAPL.measureit(number=250,output=csv_output)

def Client():
    ESHA = False

    message1 = 'LoremIpsumtext'
    message2 = 'LoremIpsumtext'
    message3 = 'LoremIpsumtext'
    message4 = 'LoremIpsumtext'

    # calculate hash
    # msg_hash = hashlib.sha256(message1).hexdigest()
    msg_hash = getESHA256(message1, ESHA)

    # fragment message
    # HK frag = int(input('Input number of fragments = '))
    frag = 4

    m = []
    h = []
    t = []
    e = []
    s = []

    # split bytesToSend to 4 fragments and store in msg[]
    m.append(message1)
    m.append(message2)
    m.append(message3)
    m.append(message4)

    # fragment hash
    # split bytesToSend to 4 fragments and store in msg[]
    # length = len(hashlib.sha256(message1).hexdigest())
    length = len(msg_hash)
    n = int(length/frag)
    i = 0
    while (i<frag) :
        h.append(msg_hash[i*n:(i+1)*n])
        i = i + 1


    str = '0x'
    h = prepend(h, str)
    print(f"\nHK Prepend 0x h = {h}")


    # calculate tags from hash fragments
    t.append(hex(int(h[0],16)))
    t.append(hex(int(h[1],16)^int(h[0],16)))
    t.append(hex(int(h[2],16)^int(h[1],16)^int(h[0],16)))
    t.append(hex(int(h[3],16)^int(h[2],16)^int(h[1],16)^int(h[0],16)))

    print(f"\nHK t = {t}")


    # append message, tag and signature
    e = [x + y for x, y in zip(m, t)]
    # e = [x + y for x, y in zip(h, t)]
    print(f"\nHK e = {e}")

    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    #    send hash
    # UDPClientSocket.sendto(msg_hash.encode(), serverAddressPort)


    # send packets
    while(True):
        UDPClientSocket.sendto(e[0].encode(), serverAddressPort)
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        msg = "Message from Server {}".format(msgFromServer[0])
        print(msg)
        if (msgFromServer[0] == "SINR Error"):
            print("Retransmitting packets again")
            continue
    
        UDPClientSocket.sendto(e[1].encode(), serverAddressPort)
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        msg = "Message from Server {}".format(msgFromServer[0])
        print(msg)
        print("Retransmitting packets again")
    
        UDPClientSocket.sendto(e[1].encode(), serverAddressPort)
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        msg = "Message from Server {}".format(msgFromServer[0])
        print(msg)


        UDPClientSocket.sendto(e[2].encode(), serverAddressPort)
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        msg = "Message from Server {}".format(msgFromServer[0])
        print(msg)
        if (msgFromServer[0] == "SINR Error"):
            print("Retransmitting packets again")
            continue

        UDPClientSocket.sendto(e[3].encode(), serverAddressPort)
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        msg = "Message from Server {}".format(msgFromServer[0])
        print(msg)
        if (msgFromServer[0] == "SINR Error"):
            print("Retransmitting packets again")
            continue
    
        break

for _ in range(1):
    Client()
csv_output.save()
print("\nEnd...")


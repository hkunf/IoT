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
import timeit
import time
import math
from ESHA256 import getESHA256

# message to be sent has to be sent in 'bytesTo Send'
serverAddressPort = ("192.168.1.71", 3003)
bufferSize = 1024

def calc_delay(signal):
    rate = 0.18 * (float(signal) + 46) / 70  # bandwidth = 0.18M, tx power signals = 46 dBm and 23 dBm, divide by difference (gain) of 70dBm
    return rate

rate_cmd = 'iwconfig wlan0 rate %sM" % calc_delay(signal)'
os.system(rate_cmd)


def ConvertSecondsToBytes(numSeconds):
    return numSeconds * maxSendRateBytesPerSecond

#def ConvertBytesToSeconds(numBytes):
#    return float(numBytes) / maxSendRateBytesPerSecond

def ConvertBytesToSeconds(numBytes, maxSendRateBytesPerSecond):
    return float(numBytes) / maxSendRateBytesPerSecond

def prepend(lst, string):
    # Using format()
    string += '{0}'
    lst = [string.format(i) for i in lst]
    return lst

pyRAPL.setup()
filename = 'Client.csv'
if os.path.exists(filename):
    os.remove(filename)
csv_output = pyRAPL.outputs.CSVOutput(filename)

@pyRAPL.measureit(number=250, output=csv_output)
def Client():
    ESHA = False

    # increase in data rate decreases transmission delay
    # We'll limit ourself to a 40KB/sec maximum send rate
    maxSendRateBytesPerSecond = (30 * 1024)    
    M = 0.608  # number of levels a single symbol can take - for C = 30*1024, B = 180kHz

    # at the schedule specified by (maxSendRateBytesPerSecond)
    bytesAheadOfSchedule = 0
    prevTime = None  

    message1 = 'LoremIpsumtext'
    message2 = 'LoremIpsumtext'
    message3 = 'LoremIpsumtext'
    message4 = 'LoremIpsumtext'

    # calculate hash
    msg_hash = getESHA256(message1, ESHA)

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
    length = len(msg_hash)
    n = int(length / frag)
    i = 0
    while (i < frag):
        h.append(msg_hash[i * n:(i + 1) * n])
        i += 1

    str = '0x'
    h = prepend(h, str)
    print(f"\nHK Prepend 0x h = {h}")

    # calculate tags from hash fragments
    t.append(hex(int(h[0], 16)))
    t.append(hex(int(h[1], 16) ^ int(h[0], 16)))
    t.append(hex(int(h[2], 16) ^ int(h[1], 16) ^ int(h[0], 16)))
    t.append(hex(int(h[3], 16) ^ int(h[2], 16) ^ int(h[1], 16) ^ int(h[0], 16)))

    print(f"\nHK t = {t}")

    # append message, tag and signature
    e = [x + y for x, y in zip(m, t)]
    print(f"\nHK e = {e}")

    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # send packets
    while True:
        now = time.time()
        if prevTime is not None:
            bytesAheadOfSchedule -= ConvertSecondsToBytes(now - prevTime)
        prevTime = now
        numBytesSent = UDPClientSocket.sendto(e[0].encode(), serverAddressPort)

        # 1
        start = timeit.default_timer()
        UDPClientSocket.sendto(e[0].encode(), serverAddressPort)
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        msg = "Message from Server {}".format(msgFromServer[0])
        print(msg)
        stop = timeit.default_timer()

        if numBytesSent > 0:
            bytesAheadOfSchedule += numBytesSent
            if bytesAheadOfSchedule > 0:
                time.sleep(ConvertBytesToSeconds(bytesAheadOfSchedule, maxSendRateBytesPerSecond))           
             
        ss = stop - start
        print(ss)
        if ss > 1.5:
            print("High transmission delay. Vary parameters")
            # if time greater than permitted value, vary parameters and transmit next packet
            maxSendRateBytesPerSecond = 2 * (180 ** 3) * math.log(2 * M * 1.02, 2)  # increase M by 10%

        # 2
        start = timeit.default_timer()
        UDPClientSocket.sendto(e[1].encode(), serverAddressPort)
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        msg = "Message from Server {}".format(msgFromServer[0])
        print(msg)
        stop = timeit.default_timer()

        if numBytesSent > 0:
            bytesAheadOfSchedule += numBytesSent
            if bytesAheadOfSchedule > 0:
                time.sleep(ConvertBytesToSeconds(bytesAheadOfSchedule, maxSendRateBytesPerSecond))
    		
        ss = stop - start
        print(ss)
        if ss > 1.5:
            print("High transmission delay. Vary parameters")
            # if time greater than permitted value, vary parameters and transmit next packet
            maxSendRateBytesPerSecond = 2 * (180 ** 3) * math.log(2 * M * 1.02, 2)  # increase M by 10%

        # 3
        start = timeit.default_timer()
        UDPClientSocket.sendto(e[2].encode(), serverAddressPort)
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        msg = "Message from Server {}".format(msgFromServer[0])
        print(msg)
        stop = timeit.default_timer()

        if numBytesSent > 0:
            bytesAheadOfSchedule += numBytesSent
            if bytesAheadOfSchedule > 0:
                time.sleep(ConvertBytesToSeconds(bytesAheadOfSchedule, maxSendRateBytesPerSecond)) 

        ss = stop - start
        print(ss)
        if ss > 1.5:
            print("High transmission delay. Vary parameters")
            # if time greater than permitted value, vary parameters and transmit next packet
            maxSendRateBytesPerSecond = 2 * (180 ** 3) * math.log(2 * M * 1.02, 2)  # increase M by 10%

        # 4
        start = timeit.default_timer()
        UDPClientSocket.sendto(e[3].encode(), serverAddressPort)
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        msg = "Message from Server {}".format(msgFromServer[0])
        print(msg)
        stop = timeit.default_timer()

        if numBytesSent > 0:
            bytesAheadOfSchedule += numBytesSent
            if bytesAheadOfSchedule > 0:
                time.sleep(ConvertBytesToSeconds(bytesAheadOfSchedule, maxSendRateBytesPerSecond))
    		
        ss = stop - start
        print(ss)
        if ss > 1.5:
            print("High transmission delay. Vary parameters")
            # if time greater than permitted value, vary parameters and transmit next packet
            maxSendRateBytesPerSecond = 2 * (180 ** 3) * math.log(2 * M * 1.02, 2)  # increase M by 10%
        break
        #time.sleep(1)

for _ in range(1):
    Client()
csv_output.save()
print("\nEnd...")


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

# message used = 'abcdefghijkl'
frag = 4

# SINR
PS = 5.5   # output signal power with input signal
PN = 5.4   # output signal power without input signal

# set IP, port and buffer size
localIP     = "192.168.1.71"
localPort   = 3003
bufferSize  = 4096

# set transmission rate to simulate NB-IoT performance
def calc_delay(signal):
   rate = 0.18 * ( float(signal) + 46 ) / 40    # bandwidth = 0.18M, rx power signals = 46 dBm and 23 dBm,divide by difference (gain) of 40dBm
   return(rate)

rate_cmd = 'iwconfig wlan0 rate %sM" % calc_delay(signal)'
os.system(rate_cmd)


# declare message to be sent to sender upon receiving a packet
msgFromServer       = "Hello UDP Client"
bytesToSend         = str.encode(msgFromServer)
 

# message when SINR is very low
M = "SINR Error"
feedback = str.encode(M) #("Required SINR is -15dB. Increase PS")


# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort)) 

print("UDP listening")
pyRAPL.setup()
filename = 'ServerFull.csv'
if os.path.exists(filename):
    os.remove(filename)
csv_output = pyRAPL.outputs.CSVOutput(filename)
@pyRAPL.measureit(number=250,output=csv_output)

def Server():
	ESHA = False
 	
	cipher_array = []
	tag1 = []
	tag2 = []
	tag3 = []
	tag4 = []
	t = []
	h = []
	c = []


	# Listen for incoming datagrams - full authentication
	z = 1
	i = 0
	while(i<frag):

	    # seperate message-tag packet from client address
	    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
	    cipher = bytesAddressPair[0].decode()
	    address = bytesAddressPair[1]
		
	    # SINR calculation
	    if (z == 2):
		    PN = 2
	    else:
		    PN = 5.4
		
	    SINR = 10*math.log10((PS-PN)/PN)

	    if ((SINR < -15) and (SINR > -25)):
		    msg = cipher[0:14]
		    c.append(cipher[14:])	    
		    # Sending a reply to client
		    UDPServerSocket.sendto(bytesToSend, address)
		    i = i + 1
		    z = z + 1
	    else:
		    UDPServerSocket.sendto(feedback, address)
		    print("\nmessage 2 dropped due to low SINR")
		    i = 1
		    z = z + 1
		    #i = i + 1
		    continue    

	msg_hash = getESHA256(msg,ESHA)
	length = len(msg_hash)
	n = int(length/frag)
	i = 0
	while (i<frag) :
	    h.append(msg_hash[i*n:(i+1)*n])
	    i = i + 1

	t.append(hex(int(h[0],16)))
	t.append(hex(int(h[1],16)^int(h[0],16)))
	t.append(hex(int(h[2],16)^int(h[1],16)^int(h[0],16)))
	t.append(hex(int(h[3],16)^int(h[2],16)^int(h[1],16)^int(h[0],16)))

	print(f"\nHK T = {t}\n")
	print(f"\nHK C = {c}\n")

	if (c[0] == t[0]):  # sha 256
	    print("message 1 verified")
	else:
	    print("message 1 not verified")
	    
	if (c[1] == t[1]):  # sha 256
	    print("message 2 verified")
	else:
	    print("message 2 not verified")


	if (c[2] == t[2]):  # sha 256
	    print("message 3 verified")
	else:
	    print("message 3 not verified")


	if (c[3] == t[3]):  # sha 256
	    print("message 4 verified")
	else:
	    print("message 4 not verified")

for _ in range(1):
    Server()
csv_output.save()
print("\nEnd...")

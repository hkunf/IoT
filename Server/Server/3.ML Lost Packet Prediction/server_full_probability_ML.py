# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

### UDP server

import socket
import os
import hashlib
import random
import pyRAPL
from ESHA256 import getESHA256

frag = 4

# Compare strings
def comp_str2(x, y):
    z = x
    ch = 0
    if len(x) == len(y):
        for i in range(len(x)):
            if x[i] != y[i]:
                print(f"Strings are not equal. They do not match by {len(x) - i} characters")
                ch = 1
                break
        if ch == 0:
            print("Strings are equal")
    else:
        print("String lengths are not equal. All tag bits not received")
        z = y
        z = y.ljust(64 - len(y) + len(y), '0')
        for i in range(len(z)):
            if x[i] == z[i]:
                continue
            else:
                print(f"Strings match by {100 * i / len(x):.2f}%")
                print(len(z), i)
                ch = 1
                break

def comp_str(x, y):
    # If lengths are equal, compare character by character
    if len(x) == len(y):
        for i in range(len(x)):
            if x[i] != y[i]:
                print(f"Strings are not equal. They do not match at position {i + 1} (1-based index).")
                return
        print("Strings are equal.")
    else:
        print("String lengths are not equal. Padding shorter string to match length of 64...")
        
        # Ensure both strings are padded to length 64 (if necessary)
        if len(x) < 64:
            x = x.ljust(64, '0')
        if len(y) < 64:
            y = y.ljust(64, '0')
        
        # Now compare character by character up to length 64
        for i in range(64):
            if x[i] != y[i]:
                match_percent = (i / 64) * 100  # Calculate percentage of match up to the point of difference
                print(f"Strings match by {match_percent:.2f}% up to position {i + 1}.")
                return
        
        # If no difference found up to 64 characters
        print("Strings match exactly up to length 64.")

# Machine learning - polynomial regression to predict missing values or when message is not verified
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import numpy as np

poly_reg = PolynomialFeatures(degree=4)

# Visualizing the Polynomial Regression results
def viz_polynomial(X, y, N):
    X_poly = poly_reg.fit_transform(X)
    pol_reg = LinearRegression()
    pol_reg.fit(X_poly, y)
    print(pol_reg.predict(poly_reg.fit_transform([[N]])))
    return

# Function to convert hexadecimal string to integer
def hex_to_int(hex_str):
    return int(hex_str, 16)

# Set IP, port and buffer size
localIP = "127.0.0.1"
localPort = 20001
bufferSize = 1024

# Set transmission rate to simulate NB-IoT performance
def calc_delay(signal):
    rate = 0.18 * (float(signal) + 46) / 40  # bandwidth = 0.18M, rx power signals = 46 dBm and 23 dBm, divide by difference (gain) of 40dBm
    return rate

rate_cmd = 'iwconfig wlan0 rate %sM" % calc_delay(signal)'
os.system(rate_cmd)

# Declare message to be sent to sender upon receiving a packet
msgFromServer = "Hello UDP Client"
bytesToSend = str.encode(msgFromServer)

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and IP
UDPServerSocket.bind((localIP, localPort))

print("UDP listening")
pyRAPL.setup()
filename = 'E-ServerFull.csv'

if os.path.exists(filename):
    os.remove(filename)

csv_output = pyRAPL.outputs.CSVOutput(filename)

@pyRAPL.measureit(number=1, output=csv_output)
def Server():
    ESHA = True
    msg = []
    t = []
    h = []
    c = []

    # Listen for incoming datagrams - full authentication
    i = 0
    while i < frag:
        # Separate message-tag packet from client address
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        cipher = bytesAddressPair[0].decode()
        address = bytesAddressPair[1]

        # Separate message from message-tag, store message in list 'c', calculate hash of message
        msg.append(cipher[0:2])  # [0:16]
        c.append(cipher[2:])  # c.append(cipher[12:])

        print(f"HK msg = {msg[i]}")
        print(f"HK cipher = {c[i]}")
        
        # Sending a reply to client
        UDPServerSocket.sendto(bytesToSend, address)
        i += 1        


    hsh = getESHA256(str(msg[0]), ESHA)
    # Calculate length of each fragment and divide hash into 4 fragments. Store in h
    n = int(len(hsh) / 4)

    j = 0
    while j < 4:
        h.append(hsh[j * n:(j + 1) * n])
        j += 1

    t.append(hex(int(h[0], 16)))
    t.append(hex(int(h[1], 16) ^ int(h[0], 16)))
    t.append(hex(int(h[2], 16) ^ int(h[1], 16) ^ int(h[0], 16)))
    t.append(hex(int(h[3], 16) ^ int(h[2], 16) ^ int(h[1], 16) ^ int(h[0], 16)))

    print(f"HK T = {t}")
    print(f"HK C = {c}")
    
    # Convert the hex strings to integers
    c_int = [hex_to_int(x) for x in c]

    # Verify tags with the cipher of each message stored in list 'c'
    # As tags are in str, they have to be converted using hex(). As the resulting output is also str, tag values were individually declared

    # Check lengths of tags to see if all of them have been received
    # tag1[0]
    
    if c[0] == t[0]:
        print("message 1 verified")
    else:
        print("message 1 not verified")
        # Use AI to predict value
        viz_polynomial(np.array([2, 3, 4]).reshape(-1, 1), np.array([c_int[1], c_int[2], c_int[3]]), 1)
        comp_str(str(c[0]), str(t[0]))

    # tag2[0]^tag1[1]
    if c[1] == t[1]:
        print("message 2 verified")
    else:
        print("message 2 not verified")
        viz_polynomial(np.array([1, 2, 3]).reshape(-1, 1), np.array([c_int[0], c_int[1], c_int[2]]), 4)
        comp_str(str(c[1]), str(t[1]))
        
    # tag3[0]^tag2[1]^tag1[2]
    if c[2] == t[2]:
        print("message 3 verified")
    else:
        print("message 3 not verified")
        viz_polynomial(np.array([1, 2, 4]).reshape(-1, 1), np.array([c_int[0], c_int[1], c_int[3]]), 3)
        comp_str(str([2]), str(t[2]))

    # tag4[0]^tag3[1]^tag2[2]^tag1[3]
    if c[3] == t[3]:
        print("message 4 verified")    
    else:
        print("message 4 not verified")
        viz_polynomial(np.array([1, 3, 4]).reshape(-1, 1), np.array([c_int[0], c_int[2], c_int[3]]), 2)
        comp_str(str(c[3]), str(t[3]))
        

for _ in range(1):
    Server()

csv_output.save()
print("\nEnd...")

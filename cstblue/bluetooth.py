# Import Libraries
from ctypes import (CDLL, get_errno)
from ctypes.util import find_library
import os
from socket import socket, AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI, SOL_HCI, HCI_FILTER
import struct
import sys
import time


btlib = find_library("bluetooth")
bluez = CDLL(btlib, use_errno=True)

class BluetoothError(Exception):
    pass

class BluetoothScanner(object):
    
    def __init__(self):
        self.device_id = None
        self.socket = None
        
    def initialize(self):
        self.get_device_id()
        self.create_socket()
        self.set_scan_parameters()
        
    def get_device_id(self):
        self.device_id = bluez.hci_get_route(None)
    
    def create_socket(self):
        if self.device_id is None:
            raise BluetoothError("no device set. was 'get_device_id' run?")
                
        self.socket = socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI)
        self.socket.bind((self.device_id,))   # Check out use of Tuple
        
         # allows LE advertising events
        hci_filter = struct.pack(
            "<IQH",
            0x00000010,
            0x4000000000000000,
            0
        )
        self.socket.setsockopt(SOL_HCI, HCI_FILTER, hci_filter)
        
    def set_scan_parameters(self):
        err = bluez.hci_le_set_scan_parameters(self.socket.fileno(), 0, 0x10, 0x10, 0, 0, 1000);
        if err < 0:
            raise BluetoothError("Set scan parameters failed. Are you root? Is device already scanning?")
        
    def enable_scanning(self):
        err = bluez.hci_le_set_scan_enable(
            self.socket.fileno(),
            1,  # 1 - turn on;  0 - turn off
            0, # 0-filtering disabled, 1-filter out duplicates
            1000  # timeout
        )
        if err < 0:
            raise BluetoothError("Unknown error enabling scanning.")
        
    def disable_scanning(self):
        err = bluez.hci_le_set_scan_enable(
            self.socket.fileno(),
            0,  # 1 - turn on;  0 - turn off
            0, # 0-filtering disabled, 1-filter out duplicates
            1000  # timeout
        )
        if err < 0:
            raise BluetoothError("Unknown error enabling scanning.")
                                 
    def scan_forever(self):
        try:
            self.enable_scanning()
            while True:
                data = self.socket.recv(1024)
                # print bluetooth address from LE Advert. packet
                now = time.time()
                addr = ':'.join("{0:02x}".format(x) for x in data[12:6:-1])
                rssi = int(data[-1])
                print(addr, rssi, now)
        finally:
            self.disable_scanning()
            
if __name__ == '__main__':
    bs = BluetoothScanner()
    bs.initialize()
    bs.scan_forever()
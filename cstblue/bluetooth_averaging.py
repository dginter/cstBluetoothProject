# Import Libraries
from ctypes import (CDLL, get_errno)
from ctypes.util import find_library
import os
from socket import socket, AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI, SOL_HCI, HCI_FILTER
import struct
import sys
import time
import math

btlib = find_library("bluetooth")
bluez = CDLL(btlib, use_errno=True)


class BluetoothData:
    """This class serves the purpose of neatly storing mac, rssi, and time information and retrieving it."""

    def __init__(self, mac):
        self.MAC = mac
        self.RSSI = []
        self.Time = []

    def average_rssi(self):
        """Gets the average of all the rssi stored."""
        total = 0
        for rssi in self.RSSI:
            total += rssi
        return round(total / len(self.RSSI), 4)

    def average_time(self):
        """Gets the average of all the timestamps stored."""
        total = 0
        for time in self.Time:
            total += time
        return round(total / len(self.Time), 1)

    def add_rssi(self, rssi):
        """Converts the rssi value into an integer and appends it to the rssi list."""
        rssi = int(rssi)
        self.RSSI.append(rssi)

    def add_time(self, time):
        """Converts the timestamp value into a float and appends it to the timestamp list."""
        time = float(time)
        self.Time.append(time)

    def get_averaged_data(self):
        """Returns mac address, averaged RSSI and timestamp as a list [MAC, RSSI, TIME]."""
        averaged_rssi = self.average_rssi()
        averaged_time = self.average_time()

        return [self.MAC, averaged_rssi, averaged_time]


def average_data(data_list: list):
    # Prepares a dictionary to store the BluetoothData objects.
    bluetooth_data = {}

    for mac, rssi, time_stamp in data_list:

        # Checks if a mac address is not already in the dictionary.
        if mac not in bluetooth_data:
            # Make a BluetoothData object and stores the mac, rssi, and time
            bluetooth_data[mac] = BluetoothData(mac)

        # Appends the rssi and time info into the BluetoothData object associated with the mac address.
        bluetooth_data[mac].add_rssi(rssi)
        bluetooth_data[mac].add_time(time_stamp)

    # Iterates through the bluetooth_data dictionray values.
    for bluetooth_object in bluetooth_data.values():
        mac, rssi, time = bluetooth_object.get_averaged_data()
        print(mac, rssi, time)


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
        self.socket.bind((self.device_id,))  # Check out use of Tuple

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
            0,  # 0-filtering disabled, 1-filter out duplicates
            1000  # timeout
        )
        if err < 0:
            raise BluetoothError("Unknown error enabling scanning.")

    def disable_scanning(self):
        err = bluez.hci_le_set_scan_enable(
            self.socket.fileno(),
            0,  # 1 - turn on;  0 - turn off
            0,  # 0-filtering disabled, 1-filter out duplicates
            1000  # timeout
        )
        if err < 0:
            raise BluetoothError("Unknown error enabling scanning.")

    def scan_forever(self):
        try:
            self.enable_scanning()
            while True:
                gathered_data = []
                current_time = time.time()

                while time.time() < math.ceil(current_time):
                    data = self.socket.recv(1024)
                    now = time.time()
                    addr = ':'.join("{0:02x}".format(x) for x in data[12:6:-1])
                    rssi = int(data[-1])
                    # print bluetooth address from LE Advert. packet
                    # print(addr, rssi, now)
                    # appends gathered data into a list
                    gathered_data.append([addr, rssi, now])
                # averages data within the gathered_data list
                average_data(gathered_data)
        finally:
            self.disable_scanning()


if __name__ == '__main__':
    bs = BluetoothScanner()
    bs.initialize()
    bs.scan_forever()

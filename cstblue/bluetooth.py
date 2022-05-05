# Import Libraries
from ctypes import (CDLL)
from ctypes.util import find_library
from socket import socket, AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI, SOL_HCI, HCI_FILTER
import struct
import time
import math
from logger import *
import config

system_ac = "SCAN"

btlib = find_library("bluetooth")
bluez = CDLL(btlib, use_errno=True)


class BluetoothError(Exception):
    pass


class BluetoothScanner(object):

    def __init__(self, queue):
        self.queue = queue
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
        # hci_filter = struct.pack(
        #     "<IQH",
        #     0x00000010,
        #     0x4000000000000000,
        #     0
        # )

        PASS_ALL = struct.pack("IIIh2x", 0xffffffff, 0xffffffff, 0xffffffff, 0)

        self.socket.setsockopt(SOL_HCI, HCI_FILTER, PASS_ALL) #hci_filter)

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
            LOG.info(f"[{system_ac}] Bluetooth scanner started @ {get_current_time()}")
            while True:
                gathered_data = []
                current_time = time.time()

                while time.time() < math.floor(current_time) + config.AVERAGE_FREQ:
                    data = self.socket.recv(1024)
                    now = time.time()
                    addr = ':'.join("{0:02x}".format(x) for x in data[12:6:-1])
                    rssi = int(data[-1])
                    # appends gathered data into a list
                    gathered_data.append([addr, rssi, now])
                # averages data within the gathered_data list
                self.queue.put(gathered_data)
                LOG.debug(f"[{system_ac}] {len(gathered_data)} sets of data put into scanner queue @ {get_current_time()}")
        finally:
            self.disable_scanning()


def scanner_worker(queue):
    """Start bluetooth scanner."""
    
    bs = BluetoothScanner(queue)
    bs.initialize()
    bs.scan_forever()

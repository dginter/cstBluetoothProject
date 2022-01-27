from multiprocessing import Manager, Process
from bluetooth import scanner_worker
from db import db_worker
# from bluetooth_scanner import
import math
from logger import *

system_ac = "CTRL"


class BluetoothData:
    """This class serves the purpose of neatly storing mac, rssi, and time information and retrieving it."""

    def __init__(self, mac, time_stamp):
        self.MAC = mac
        self.Time = math.floor(time_stamp)
        self.RSSI = []

    def average_rssi(self):
        """Get average of all the rssi stored."""
        total = 0
        for rssi in self.RSSI:
            total += rssi
        return round(total / len(self.RSSI), 4)

    def add_rssi(self, rssi):
        """Convert rssi value into an integer and append it to the rssi list."""
        rssi = int(rssi)
        self.RSSI.append(rssi)

    def get_data(self):
        """Return mac address, averaged RSSI and current second as a list [MAC, RSSI, TIME]."""
        averaged_rssi = self.average_rssi()

        return [self.MAC, averaged_rssi, self.Time]


class Controller:
    """Main controller.

        Activates the bluetooth scanner and database writer, manages the queues, aggregates data, and transfers
        data from the bluetooth scanner to the database writer.
    """
    
    def __init__(self):
        self.scan_queue = Manager().Queue()
        self.scanner_process = Process(target=scanner_worker, args=(self.scan_queue,))

        self.db_queue = Manager().Queue()
        self.db_process = Process(target=db_worker, args=(self.db_queue,))

    def start(self):
        """Start the controller."""
        self.start_scanner()
        self.start_db_writer()
        self.read_scanner_queue()

    def aggregate_data(self, data_list):
        """Aggregate and average bluetooth data."""
        # Prepares a dictionary to store the BluetoothData objects.
        bluetooth_data = {}

        for mac, rssi, time_stamp in data_list:

            # Checks if a mac address is not already in the dictionary.
            if mac not in bluetooth_data:
                # Make a BluetoothData object and stores the mac, rssi, and time
                bluetooth_data[mac] = BluetoothData(mac, time_stamp)

            # Appends the rssi and time info into the BluetoothData object associated with the mac address.
            bluetooth_data[mac].add_rssi(rssi)

        # Sends off data to the db writer.
        self.db_queue.put(bluetooth_data)
        LOG.debug(f"[{system_ac}] {len(bluetooth_data)} sets of aggregated data put into database queue @ "
                  f"{get_current_time()}")

    def start_scanner(self):
        """Start the bluetooth scanner."""
        self.scanner_process.start()
        LOG.info(f"[{system_ac}] Starting scanner @ {get_current_time()}")

    def start_db_writer(self):
        """Start the database writer."""
        self.db_process.start()
        LOG.info(f"[{system_ac}] Starting database writer @ {get_current_time()}")

    def read_scanner_queue(self):
        """Start reading from the bluetooth scanner queue."""
        LOG.info(f"[{system_ac}] Started reading from scanner queue @ {get_current_time()}")
        while True:
            # Gets data from the bluetooth scanner
            data = self.scan_queue.get()

            # aggregates the data and forwards it to the db writer
            self.aggregate_data(data)


if __name__ == "__main__":
    bluetooth_processor = Controller()
    bluetooth_processor.start()


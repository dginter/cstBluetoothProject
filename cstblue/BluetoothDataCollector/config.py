"""Configuration settings

Attributes:
    USER (str): Username for database account.
    PASS (str): Password for database account.
    HOST (str): IP address of the mysql server host.
    DB (str): Name of the database being accessed.
        
    UNIQUE_ID (str): Unique identifier for the raspberry pi.
    
    AVERAGE_FREQ (int): The amount of time in seconds that the bluetooth scanner gathers data in one sitting before forwarding it to the scanner.
"""

USER = "bt1"
PASS = "blueToothTracking_1"
HOST = "10.24.250.4"
DB = "blueTooth01"

DATABASE_TABLE = "data"

UNIQUE_ID = "pi_00"

AVERAGE_FREQ = 3

"""Configuration settings

Attributes:
    USER (str): Username for database account.
    PASS (str): Password for database account.
    HOST (str): IP address of the mysql server host.
    DB (str): Name of the database being accessed.
        
    UNIQUE_ID (str): Unique identifier for the raspberry pi.
    
    AVERAGE_FREQ (int): The amount of time in seconds that the bluetooth scanner gathers data in one sitting before forwarding it to the scanner.
"""

USER = ""
PASS = ""
HOST = ""
DB = ""

DATABASE_TABLE = ""

UNIQUE_ID = ""

AVERAGE_FREQ = 3

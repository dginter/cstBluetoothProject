from logger import *
import mysql.connector
from mysql.connector import errorcode
import config
from datetime import datetime

system_ac = "DB"


class DatabaseWriter:
    """Database writer.

    Manages database connection, executes mysql commands, and writes bluetooth data into the database.
    """
    
    def __init__(self, queue):
        self.queue = queue
        self._connection = None
        
    def get_sql_connection(self):
        """Get connection to the database and get a new one if needed."""
        if self._connection is None or not self._connection.is_connected():
            try:
                LOG.info(f'[{system_ac}] Attempting to open db connection: {config.USER}@{config.HOST} '
                         f'@ {get_current_time()}')
                self._connection = mysql.connector.connect(user=config.USER, password=config.PASS,
                                                           host=config.HOST, database=config.DB)
            except mysql.connector.Error as err:
                prefix = "failed to connect to database: "
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    log_message = f"{prefix}Something is wrong with your user name or password"
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    log_message = f"{prefix}Database does not exist"
                else:
                    log_message = f"[{system_ac}] {prefix}{err} @ {get_current_time()}"
                LOG.error(log_message)
                raise err

        return self._connection

    def execute_sql_command(self, sql_command):
        """Execute sql command."""
        connection = self.get_sql_connection()
        cursor = connection.cursor()
        cursor.execute(sql_command)
        connection.commit()
        results = cursor.fetchall()
        cursor.close()
        return results

    def db_write(self, data):
        """Write bluetooth data into the database."""
        bluetooth_data = [bluetooth_object.get_data() for bluetooth_object in data.values()]
        values = ",\n".join(f"('{config.UNIQUE_ID}', '{mac}', {rssi}, {time})" for mac, rssi, time in bluetooth_data)
        self.execute_sql_command(f"INSERT INTO {config.DATABASE_TABLE} VALUES {values}")
        LOG.debug(f"[{system_ac}] {len(data)} sets of data put into database @ {get_current_time()}")

    def read_from_queue(self):
        """Read from queue given by the controller and write data into the database."""
        LOG.info(f"[{system_ac}] Started reading from database queue @ {get_current_time()}")
        while True:
            data = self.queue.get()
            LOG.debug(f"[{system_ac}] Read {len(data)} sets of data @ {get_current_time()}")
            self.db_write(data)


def db_worker(queue):
    """Start the database writer."""
    db_writer = DatabaseWriter(queue)
    db_writer.read_from_queue()




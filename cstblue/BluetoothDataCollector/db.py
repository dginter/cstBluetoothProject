import logging
import os
import mysql.connector
from mysql.connector import errorcode
import config

LOG_LEVEL = logging.DEBUG

LOG = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(LOG_LEVEL)
LOG.addHandler(console)
LOG.setLevel(LOG_LEVEL)
PASSWORD = os.environ.get('API_PASSWORD')


class DatabaseWriter:

    def __init__(self, queue):
        self.queue = queue
        self._connection = None

    def get_sql_connection(self):
        if self._connection is None or not self._connection.is_connected():
            try:
                LOG.info(f'attempting to open db connection: {config.USER}@{config.HOST}')
                self._connection = mysql.connector.connect(user=config.USER, password=config.PASS,
                                                           host=config.HOST, database=config.DB)
            except mysql.connector.Error as err:
                prefix = "failed to connect to database: "
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    log_message = f"{prefix}Something is wrong with your user name or password"
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    log_message = f"{prefix}Database does not exist"
                else:
                    log_message = f"{prefix}{err}"
                LOG.error(log_message)
                raise err

        return self._connection

    def execute_sql_command(self, sql_command):
        connection = self.get_sql_connection()
        cursor = connection.cursor()
        cursor.execute(sql_command)
        connection.commit()
        results = cursor.fetchall()
        cursor.close()
        return results

    def db_write(self, data):

        for bluetooth_object in data.values():
            mac, rssi, time_stamp = bluetooth_object.get_data()

            query = f"""
                        INSERT INTO data VALUES (
                            '{mac}',
                            {rssi},
                            {time_stamp}
                    """

            self.execute_sql_command(query)

        print("finished writing")

    def read_from_queue(self):
        while True:
            data = self.queue.get()
            self.db_write(data)



def db_worker(queue):
    db_writer = DatabaseWriter(queue)
    db_writer.read_from_queue()




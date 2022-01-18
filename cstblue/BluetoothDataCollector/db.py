import mysql.connector
import config


class DatabaseWriter:

    def __init__(self, queue):
        self.queue = queue
        self.connection = mysql.connector.connect(user=config.USER, password=config.PASS,
                                                  host=config.HOST, database=config.DB)
        self.cursor = self.connection.cursor()

    def db_write(self, data):

        for bluetooth_object in data.values():
            mac, rssi, time_stamp = bluetooth_object.get_data()

            query = f"""
                        INSERT INTO data VALUES (
                            '{mac}',
                            {rssi},
                            {time_stamp}
                        )
                    """

            self.cursor.execute(query)

        self.connection.commit()
        print("finished writing")

    def read_from_queue(self):
        while True:
            data = self.queue.get()
            self.db_write(data)


def db_worker(queue):
    db_writer = DatabaseWriter(queue)
    db_writer.read_from_queue()

import logging
import os
from datetime import datetime


def get_current_time():
    """Return current time in formatted form."""
    current_hour = int(datetime.now().strftime("%H"))
    day_portion = "AM" if current_hour < 12 else "PM"
    current_time = datetime.now().strftime(f"%H:%M:%S {day_portion}")
    return current_time


LOG_LEVEL = logging.DEBUG

LOG = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(LOG_LEVEL)

formatter = logging.Formatter("[%(asctime)s;%(levelname)s] %(message)s")
console.setFormatter(formatter)

LOG.addHandler(console)
LOG.setLevel(LOG_LEVEL)
PASSWORD = os.environ.get('API_PASSWORD')

import time
import random

import pz.constants as cns
from pz.database import DBCommunicator


if __name__ == "__main__":
    comm = DBCommunicator(cns.DB_ADDRESS, cns.DATABASE_NAME)
    while True:
        point = {x: random.random()* 25 for x in cns.VARS_STRING}
        comm.write(point, cns.MEASURE_NAME)
        time.sleep(1)
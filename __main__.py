import time
import pz.constants as cnst
from influxdb import InfluxDBClient


CONST_S_TO_NS_COEF = 1000000000

params = "*" # "a, b, c"
dbaddr = "localhost"
print("params used: ")
print("--dbaddr: ", dbaddr)
print("--dbname: ", cnst.DATABASE_NAME)
print("--dbmes: ", cnst.MEASURE_NAME)
print("-----------------------------")
time_a = None
time_b = None
print("(a, b), time to select")
print("input time in s from epoch(a), set empty if not needed")
inp = input()
if inp != "":
    time_a = int(inp) * CONST_S_TO_NS_COEF
    print("input time in s from epoch(b), set empty if not needed")
    inp = input()
    if inp != "":
        time_b = int(inp) * CONST_S_TO_NS_COEF

query_string = "SELECT " + params + " FROM " + cnst.MEASURE_NAME
if time_a is not None:
    query_string += ' WHERE  "time" > ' + str(time_a)
if time_b is not None:
    query_string += ' AND "time" < ' + str(time_b)
print(query_string)
conn = InfluxDBClient(dbaddr, database=cnst.DATABASE_NAME)
tm = time.time()
ms = conn.query(query_string, epoch='s')
tm = time.time() - tm
for a in ms.get_points():
    print(a)
print("------")
print(tm)

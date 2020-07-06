from influxdb import InfluxDBClient


class DBCommunicator:
    def __init__(self, host='localhost', db='yourdb'):
        self._connection = InfluxDBClient(host=host, database=db)

    def write(self, point: {}, mes: str):
        rm = [{
            "measurement": mes,
            "fields": point
        }]
        self._connection.write_points(rm)

    def get_points(self, mes):
        rd = self._connection.query(
            f"SELECT * FROM \"{mes}\";",
            epoch="s"
        )
        return list(rd.get_points())

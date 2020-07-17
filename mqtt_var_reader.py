import paho.mqtt.client as mqtt
from .variable import MpVarMass, Variable
from multiprocessing import Process


class MQTTReader:
    def __init__(self, topic, variable, var_mas: MpVarMass):
        self._topic = topic
        self._variable = variable
        self._var_mas = var_mas

    def connect(self, host: str):
        te = self
        cli = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            te._var_mas.add_var(te._create_mqtt_var())
            cli.subscribe(te._topic + "/" + te._variable + "/")

        def on_message(client, userdata, msg):
            te._var_mas.set_var(te._create_mqtt_var(float(msg.payload)))

        cli.on_connect = on_connect
        cli.on_message = on_message
        cli.connect(host)
        cli.loop_forever()

    def _create_mqtt_var(self, value: float = 0):
        return Variable(self._variable, value, simmulate_flag=False)


class MQTTVarsManager:
    _mqtt_readers = {}
    _var_mas: MpVarMass = None

    @classmethod
    def set_vmas(cls, var_mas: MpVarMass):
        cls._var_mas = var_mas

    @classmethod
    def add_reader(cls, variable_name, topic_name, mqtt_host_address):
        if cls._var_mas is None:
            raise Exception("set_vmas not called")
        if variable_name in cls._mqtt_readers:
            return False
        mr = MQTTReader(topic_name, variable_name, cls._var_mas)
        cls._mqtt_readers[variable_name] = Process(target=mr.connect, args=(mqtt_host_address, ))
        cls._mqtt_readers[variable_name].start()
        return True

    @classmethod
    def rem_reader(cls, variable_name):
        if variable_name not in cls._mqtt_readers:
            return False
        k = cls._mqtt_readers.pop(variable_name)
        k.terminate()
        k.join()
        return True
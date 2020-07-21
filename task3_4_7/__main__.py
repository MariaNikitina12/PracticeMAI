import time
import string
import random
import hashlib
from multiprocessing import Process

from flask import Flask, request, jsonify
from .variable import TimingSimulVariable, MpVarMass, Saver
from .mqtt_var_reader import MQTTVarsManager
from .oath_simple import OAuthSimple
from .authdb import FakeDatabase
from database import DBCommunicator
import constants as cnst


app = Flask(__name__)
var_holder = MpVarMass()
db = DBCommunicator(cnst.DB_ADDRESS, cnst.DATABASE_NAME)
MQTTVarsManager.set_vmas(var_holder)
auth = OAuthSimple()
fdb = FakeDatabase()


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


@auth.get_user
def get_user(name):
    return fdb.get_user(name)


@auth.get_header_token
def get_header_token():
    hd = request.headers.get('Authorization', None)
    if hd is None:
        return hd
    sm = str(hd).split(" ")
    if sm[0] != 'Bearer':
        return None
    return sm[1]


@auth.set_unauthorised_handler
def ua_handler():
    return jsonify(req="UNAUTHORIZED"), 401


@app.route('/auth/', methods=['POST'])
def authf():
    nm = request.form.get('name', None)
    ps = request.form.get('ps', None)
    if nm is None or ps is None:
        return jsonify(req="BAD1")
    us = fdb.get_user(str(nm))
    if us is None:
        return jsonify(req="BAD2")
    hs = hashlib.sha256()
    hs.update(str(ps).encode())
    if hs.hexdigest() != us.h_pass:
        return jsonify(req="BAD3")
    fdb.set_user_secr(us.name, get_random_string(30), time.time()+60*60*24)
    return {"token": auth.create_token(fdb.get_user(us.name)).decode()}


class Const:
    write_procc = None
    saver = None
    sim_procc = None


@app.route("/start_serv/")
def start_serv():
    freq = request.args.get("freq", 2.0)
    if Const.sim_procc is None and Const.write_procc is None:
        Const.sim_procc = Process(target=var_holder.sim, args=())
        Const.saver = Saver(var_holder, db, freq)
        Const.write_procc = Process(target=Saver.run, args=(Const.saver, cnst.MEASURE_NAME))
        Const.sim_procc.start()
        Const.write_procc.start()
        return jsonify(req="OK")
    return jsonify(req="BAD")


@app.route("/stop_serv/")
def stop_serv():
    if Const.sim_procc is not None and Const.write_procc is not None:
        Const.write_procc.terminate()
        Const.sim_procc.terminate()
        Const.sim_procc.join()
        Const.write_procc.join()
        Const.write_procc = Const.sim_procc = None
        return jsonify(req="OK")
    return jsonify(req="BAD")


@app.route("/add/")
def add():
    name = request.args.get("nm", None)
    bv = request.args.get("bv", None)
    if name is None or bv is None:
        return jsonify(req="BAD PARAMS")
    freq = request.args.get("freq", 1.0)
    rng = request.args.get("rng", 2.0)
    return jsonify(req=var_holder.add_var(TimingSimulVariable(freq, name, float(bv), True, rng)))


@app.route("/add_mosquitto/")
@auth.auth_required
def addm():
    name = request.args.get("nm", None)
    topic = request.args.get("tp", None)
    if name is None or topic is None:
        return jsonify(req="BAD PARAMS")
    return jsonify(req=MQTTVarsManager.add_reader(name, topic, 'mqtt_cont',))


@app.route("/rem/")
def rem():
    name = request.args.get("nm", None)
    if name is None:
        return jsonify(req="BAD PARAMS")
    return jsonify(req=var_holder.del_var(name))


@app.route("/getall/")
def lst():
    t = var_holder.var_list()
    return jsonify(count=len(t), arg=t)


app.run('0.0.0.0', "8010", debug=False)

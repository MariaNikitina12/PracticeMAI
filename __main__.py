from multiprocessing import Process

from flask import Flask, request, jsonify
from pz.task3.variable import TimingSimulVariable, Variable, MpVarMass, Saver
from pz.database import DBCommunicator
import pz.constants as cnst

app = Flask(__name__)
var_holder = MpVarMass()
db = DBCommunicator(cnst.DB_ADDRESS, cnst.DATABASE_NAME)


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

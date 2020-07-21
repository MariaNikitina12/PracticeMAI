import random
import time
from multiprocessing import Manager
from database import DBCommunicator


class Variable:
    def __init__(self, name: str, beg_value: float, simmulate_flag=True, change_per=2):
        self.name = name
        self.value = beg_value
        self.sim = simmulate_flag
        self.change_per = change_per

    def simulate(self, time_spend):
        if self.sim:
            self.value += (-1+2*random.random()) * self.change_per
        return 0.2


class TimingSimulVariable(Variable):
    def __init__(self, sim_freq: float, name: str, beg_value: float, simmulate_flag=True, change_per=2.0):
        super().__init__(name, beg_value, simmulate_flag, change_per)
        self.sim_time = 1.0 / sim_freq
        self.cur_time = self.sim_time

    def simulate(self, time_spend):
        self.cur_time -= time_spend
        if self.cur_time <= 0:
            self.cur_time = self.sim_time
            super().simulate(time_spend)
        return self.cur_time


class MpVarMass:
    def __init__(self):
        self._lc = Manager().Lock()
        self._vrs = Manager().dict()

    def lock_func(self, f, *args, **kwargs):
        self._lc.acquire(blocking=True)
        ret = f(*args, **kwargs)
        self._lc.release()
        return ret

    def _set_var(self, var: Variable):
        vr = self._vrs.copy()
        if var.name not in vr:
            return False
        self._vrs[var.name] = var
        return True

    def set_var(self, var: Variable):
        return self.lock_func(self._set_var, var)

    def _add_var(self, var: Variable):
        vr = self._vrs.copy()
        if var.name in vr:
            return False
        self._vrs[var.name] = var
        return True

    def add_var(self, var: Variable):
        return self.lock_func(self._add_var, var)

    def _del_var(self, name):
        vr = self._vrs.copy()
        if name in vr:
            self._vrs.pop(name)
            return True
        return False

    def del_var(self, name):
        return self.lock_func(self._del_var, name)

    def _sim_iter(self, time_spend):
        vr = self._vrs.copy()
        tsp = 0.2
        for a in vr:
            wt = vr[a].simulate(time_spend)
            print(a, vr[a].value)
            self._vrs[a] = vr[a]
            if wt < tsp:
                tsp = wt
        return tsp

    def sim(self):
        swt = 0
        while True:
            swt = self.lock_func(self._sim_iter, swt)
            time.sleep(swt)

    def var_list(self):
        self._lc.acquire()
        vr = self._vrs.copy()
        self._lc.release()
        rm = {}
        for a in vr:
            rm[a] = float(vr[a].value)
        return rm


class Saver:
    def __init__(self, vc: MpVarMass, db: DBCommunicator,freq: float = 2.0):
        self._sleep_time = 1 / freq
        self._data_from = vc
        self._db = db

    def run(self, mes):
        while True:
            vd = self._data_from.var_list()
            if vd:
                self._db.write(vd, mes)
            time.sleep(self._sleep_time)

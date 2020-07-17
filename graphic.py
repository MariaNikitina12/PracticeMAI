import matplotlib.pyplot as plt


class ZipVar:
    def __init__(self, name: str,  tm: [], val: []):
        self.timestamps = tm
        self.value = val
        self.name = name


class Drawer:
    def __init__(self):
        self._fig = None
        self._ax = None
        self._fig, self._ax = plt.subplots()
        self.vars = []

    def update_vars(self, vars_list: []):
        self.vars = vars_list

    def draw(self):
        self._ax.cla()
        if not self.vars:
            return
        for a in self.vars:
            self._ax.plot(a.timestamps, a.value, label=a.name)
        plt.tight_layout()
        plt.legend(loc='lower left')

    def pause(self):
        plt.pause(1)


class SingletonDrawer:
    _drw = None

    def __new__(cls, *args, **kwargs):
        if not cls._drw:
            cls._drw = Drawer()
        return cls._drw

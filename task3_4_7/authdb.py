from typing import Optional


class User:
    def __init__(self):
        self.name = ''
        self.h_pass = b''
        self.secr = ''
        self.expires = ''


class DataBase:
    def get_user(self, name) -> Optional[User]:
        pass

    def set_user_secr(self, name, sercr, exp) -> None:
        pass


class FakeDatabase(DataBase):
    users = {
        "Mari": {
            "h_pass": 'ae2b9ceb610e704a1795f276da72fc2057b9601263211449284b6dac3784d2ef',
            "secr": "",
            "exp": None
        }
    }

    def get_user(self, name) -> Optional[User]:
        if name not in self.users:
            return None
        us = User()
        us.h_pass = self.users[name]['h_pass']
        us.name = name
        us.expires = self.users[name]['exp']
        us.secr = self.users[name]['secr']
        return us

    def set_user_secr(self, name, sercr, exp) -> None:
        if name not in self.users:
            return
        self.users[name]['secr'] = sercr
        self.users[name]['exp'] = exp

import hashlib
import jwt
import time


class OAuthSimple:
    def _get_user(self, name):
        pass

    def _get_header_token(self):
        pass

    def get_user(self, f):
        self._get_user = f
        return f

    def get_header_token(self, f):
        self._get_header_token = f
        return f

    def _unauth_hanlder(self):
        pass

    def set_unauthorised_handler(self, f):
        self._unauth_hanlder = f
        return f

    def auth_required(self, f):
        def decorator():
            token = self._get_header_token()
            try:
                user_mas = jwt.decode(token, 'secret', algorithms=['HS256'])
            except Exception:
                return self._unauth_hanlder()
            name = user_mas.get('name', None)
            if name is None:
                return self._unauth_hanlder()
            user = self._get_user(str(name))
            if user is None:
                return self._unauth_hanlder()
            if user.secr != user_mas.get('secret', ''):
                return self._unauth_hanlder()
            try:
                if time.time() - float(user.expires) > 0:
                    raise Exception('ad')
            except Exception:
                return self._unauth_hanlder()
            return f()
        return decorator


    def create_token(self, user):
        print(user.name, user.secr)
        return jwt.encode({'name': user.name, 'secret': user.secr}, 'secret', algorithm='HS256')


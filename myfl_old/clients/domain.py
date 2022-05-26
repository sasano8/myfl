class DomainNode:
    def __init__(self, host):
        self.host = host

    def login(self, user, pw):
        ...

    def logout(self, user, pw):
        ...

    @property
    def users(self):
        return Users()


class Users:
    ...

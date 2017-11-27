class User:
    def __init__(self, name, email=None, exclusions=[]):
        self.name = name
        self.match = None
        self.exclusions = exclusions

        self.email = email

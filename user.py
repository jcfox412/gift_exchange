class User:
    def __init__(self, name, match, email=None):
        self.name = name
        self.match = match

        self.email = email

        if self.email is None:
            self.email = self.format_gmail_email(self.name)

    def format_gmail_email(self, user):
        return "@".join([user, "gmail.com"])

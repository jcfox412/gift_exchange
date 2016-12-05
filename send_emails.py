import os
import sys
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from user import User

class SecretSanta:

    def __init__(self, user):
        self.user = user
        pwd = self.get_password()
        self.server = self.setup_smtp_server(pwd)

        self.from_email = self.format_gmail_email(user)

    def get_password(self):
        pwd_key = "EMAIL_PWD"
        try:
            pwd = os.environ[pwd_key]
            return pwd
        except KeyError:
            print "Unable to access environment from %s environment variable." % pwd_key
            sys.exit()

    def format_gmail_email(self, user):
        return "@".join([user, "gmail.com"])

    def setup_smtp_server(self, pwd):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(self.user, pwd)
            return server
        except:
            print("failed to setup smtp server: ", sys.exc_info()[0])
            sys.exit()

    def close_smtp_server(self):
        self.server.close()

    def send_email(self, user):
        FROM = self.from_email
        TO = user.email

        msg = self.format_email_message(user)

        try:
            self.server.sendmail(FROM, TO, msg.as_string())
            print "successfully sent email for match from %s to %s" % (user.name, user.match)
        except:
            print "failed to send email for match from %s to %s" % (user.name, user.match)
            sys.exit()

    def format_email_message(self, user):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Zappi Gift Exchange 2016!"
        msg['From'] = self.from_email
        msg['To'] = user.email

        text = self.format_email_plaintext(user)
        html = self.format_email_html(user)

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        return msg

    def format_email_plaintext(self, user):
        return """
Hi {name},

Thanks for participating in the 2016 Zappi gift exchange! Last year's exchange was pretty great, so let's try it out again this year! This is an automated message to tell you that you will be getting a gift for {match}. Don't tell them!

Like last year, here are some guidelines for your gift:
    - Please keep your gift to less than $20
    - Gifts should be non-perishable (people may be traveling with these)
    - Be creative!

If you have any suggestions for your secret santa, please put them here: LINK_HERE. If you have any further questions, please just send an email to EMAIL_HERE.

Thanks!

This is an automated message sent by the Zappi Gift Exchange.
        """.format(
            name=user.name,
            match=user.match,
        )

    def format_email_html(self, user):
        return """
<html>
    <head>
    </head>
    <body>
        <p>Hi {name},</p>
        <p>Thanks for participating in the 2016 Zappi gift exchange! Last year's
        exchange was pretty great, so let's try it out again this year!
        This is an automated message to tell you that you will be getting
        a gift for <b>{match}</b>. Don't tell them!</p></br ></br />
        <p>Like last year, here are some guidelines for your gift:<p>
        <ul>
            <li>Please keep your gift to less than $20</li>
            <li>Gifts should be non-perishable (people may be traveling with these)</li>
            <li>Be creative!</li>
        </ul>
        <p>If you have any suggestions for your secret santa, please put them <a href="LINK_HERE">here</a>.
        If you have any further questions, please just send an email to EMAIL_HERE.</p>
        <p>Thanks!</p>
        <p>This is an automated message sent by the Zappi Gift Exchange.</p>
    </body>
</html>
        """.format(
            name=user.name,
            match=user.match,
        )

# Setup gmail authentication
user = "USERNAME_HERE"
secretSanta = SecretSanta(user)

# setup users
user1 = User("Name1", "Match1", "my_email1@gmail.com")
user1 = User("Name2", "Match2", "my_email2@gmail.com")

participants = [user1, user2]

for participant in participants:
    secretSanta.send_email(participant)

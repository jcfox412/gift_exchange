from datetime import datetime
import os
from random import shuffle
import sys
import smtplib
import yaml

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from user import User

class SecretSanta:
    def __init__(self):
        self.email_sender = self.get_email_sender()
        self.participants = []
        pwd = self.get_password()
        self.server = self.setup_smtp_server(pwd)

        self.wish_list_link = self.get_wish_list_link()
        self.exchange_name = self.get_exchange_name()
        self.year = self.get_year()

    def get_email_sender(self):
        email_sender_key = "EMAIL_SENDER"
        try:
            email_sender = os.environ[email_sender_key]
            return email_sender
        except KeyError:
            print("Unable to access email sender from %s environment variable." % email_sender_key)
            sys.exit()

    def get_password(self):
        pwd_key = "EMAIL_PWD"
        try:
            pwd = os.environ[pwd_key]
            return pwd
        except KeyError:
            print("Unable to access gmail password from %s environment variable." % pwd_key)
            sys.exit()

    def get_wish_list_link(self):
        wish_list_key = "SECRET_SANTA_WISH_LIST"
        try:
            wish_list = os.environ[wish_list_key]
            return wish_list
        except KeyError:
            print("Unable to access wish list link from %s environment variable." % wish_list_key)
            sys.exit()

    def get_exchange_name(self):
        exchange_name_key = "SECRET_SANTA_EXCHANGE_NAME"
        try:
            exchange_name = os.environ[exchange_name_key]
            return exchange_name
        except KeyError:
            print("Unable to access exchange name from %s environment variable." % exchange_name_key)
            sys.exit()

    def get_year(self):
        year_key = "SECRET_SANTA_YEAR"
        try:
            year = os.environ[year_key]
            return year
        except KeyError:
            year = str(datetime.now().year)
            print("Unable to access year from %s environment variable. Defaulting to current year (%s)." % (year_key, year))
            return year

    def setup_smtp_server(self, pwd):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(self.email_sender, pwd)
            return server
        except:
            print("failed to setup smtp server: ", sys.exc_info()[0])
            sys.exit()

    def close_smtp_server(self):
        self.server.close()

    def load_participants_from_json(self, filename):
        with open(filename, "r") as data_file:
            data = yaml.safe_load(data_file)
        for p in data["participants"]:
            user = User(p["name"], p["email"], p["exclusions"])
            self.participants.append(user)

    def calculate_matches(self, num_attempts):
        for i in range(num_attempts):
            print("Calculating matches - attempt number %s..." % str(i+1))

            givers = list(self.participants)
            receivers = list(self.participants)

            shuffle(givers)
            shuffle(receivers)

            self.try_matching(givers, receivers)
            if self.check_matches():
                print("All participants matched!")
                return True
            else:
                self.reset_matches()
        print("No matches found :(")
        return False

    def try_matching(self, givers, receivers):
        for giver in givers:
            for j in range(len(receivers)):
                receiver = receivers[j]
                if receiver.name not in giver.exclusions and receiver != giver:
                    giver.match = receiver
                    receivers.pop(j)
                    break

    def check_matches(self):
        for participant in self.participants:
            if participant.match is None:
                return False
        return True

    def reset_matches(self):
        for participant in self.participants:
            participant.match = None
        return

    def send_emails(self):
        for participant in self.participants:
            self.send_email(participant)

    def send_email(self, user):
        FROM = self.email_sender
        TO = user.email

        msg = self.format_email_message(user, FROM, TO)

        try:
            self.server.sendmail(FROM, TO, msg.as_string())
            print("successfully sent email for match from %s to %s" % (user.name, user.match.name))
        except:
            print("failed to send email for match from %s to %s" % (user.name, user.match.name))
            sys.exit()

    def format_email_message(self, user, from_email, to_email):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "{exchange_name} {year}!".format(exchange_name=self.exchange_name, year=self.year)
        msg['From'] = from_email
        msg['To'] = to_email

        text = self.format_email_plaintext(user, from_email)
        html = self.format_email_html(user, from_email)

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        return msg

    def format_email_plaintext(self, user, from_email):
        return """
Hi {name},

Thanks for participating in the {year} {exchange_name}! This year's exchange is now completely automated, so I can finally feel a little less like I'm playing god with everyone's matches, haha.

This is an automated message to tell you that you will be getting a gift for {match}. Don't tell them!

Like years past, here are some guidelines for your gift:
    - Please keep your gift to less than $20
    - Gifts should be non-perishable (people may be traveling with these)
    - Be creative!

If you have any suggestions for your secret santa, please put them here: {wish_list}. If you have any further questions, please just send an email to {from_email}.

Thanks!

This is an automated message sent by the {exchange_name}.
        """.format(
            year=self.year,
            exchange_name=self.exchange_name,
            name=user.name,
            match=user.match.name,
            wish_list=self.wish_list_link,
            from_email=from_email,
        )

    def format_email_html(self, user, from_email):
        return """
<html>
    <head>
    </head>
    <body>
        <p>Hi {name},</p>
        <p>Thanks for participating in the {year} {exchange_name}! This
        year's exchange is now completely automated, so I can finally feel a
        little less like I'm playing god with everyone's matches, haha.</p></br ></br />

        <p>This is an automated message to tell you that you will be getting
        a gift for <b>{match}</b>. Don't tell them!</p></br ></br />
        <p>Like years past, here are some guidelines for your gift:<p>
        <ul>
            <li>Please keep your gift to less than $20</li>
            <li>Gifts should be non-perishable (people may be traveling with these)</li>
            <li>Be creative!</li>
        </ul>
        <p>If you have any suggestions for your secret santa, please put them <a href="{wish_list}">here</a>.
        If you have any further questions, please just send an email to {from_email}.</p>
        <p>Thanks!</p>
        <p>This is an automated message sent by the {exchange_name}.</p>
    </body>
</html>
        """.format(
            year=self.year,
            exchange_name=self.exchange_name,
            name=user.name,
            match=user.match.name,
            wish_list=self.wish_list_link,
            from_email=from_email,
        )

secretSanta = SecretSanta()
secretSanta.load_participants_from_json("participants.json")
matches_calculated = secretSanta.calculate_matches(num_attempts=3)

if matches_calculated:
    secretSanta.send_emails()

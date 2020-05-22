import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import json

with open('settings.json','r') as file:
    settings = json.load(file)
with open(os.path.join(sys.path[0], "password.key"), "r") as f:
    sender_password = f.read()

class Email:

    def __init__(self, productTitle, item_url, item_price, target_price):
        self.productTitle = productTitle
        self.item_url = item_url
        self.item_price = item_price
        self.target_price = target_price

        server = smtplib.SMTP('smtp.gmail.com', 587)

        server.ehlo()
        server.starttls()
        server.login(settings['email'], sender_password)

        self.server = server

        msg = MIMEMultipart()
        msg['From'] = settings['email']

        self.msg = msg

    def sendEmail(self):
        self.msg['To'] = settings['email']
        self.msg['Subject'] = f'Price drop on {self.productTitle}!'

        content = open(os.path.join(sys.path[0], "emailTemplate", "priceDropTemplate.html"), "r").read().format(
            productTitle=self.productTitle, item_url=self.item_url, item_price=self.item_price,
            target_price=self.target_price)
        self.msg.attach(MIMEText(content, 'html'))

        content = self.msg.as_string()
        self.server.sendmail(settings['email'], settings['email'], content)
        self.server.close()



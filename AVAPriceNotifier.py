#!/usr/bin/python3

import requests
import smtplib
import ssl
import datetime
from html.parser import HTMLParser

'''
1- Get data from website
2- Send email
3- Repeat every few hours
'''

class AVAParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []
        self.found = False
        self.recording = 0

    def handle_starttag(self, tag, attrs):

        if tag == "ul":
            for name, value in attrs:
                if name == "class" and value == "sidebar-apartment-prices":
                    self.recording = True

    def handle_endtag(self, tag):
        if tag == "ul" and self.recording:
            self.recording = False

    def handle_data(self, data):
        if self.recording:
            self.data.append(data)


def create_message(data):
    current_time = datetime.datetime.now()
    day = current_time.day
    month = current_time.month
    hours = current_time.hour
    minutes = current_time.minute
    message = "Subject: AVA North Station Prices\n" \
              "Hi, \n\n" \
              "The prices for AVA North Station on {0}/{1} at {2}:{3} are:\n" \
              "".format(month, day, hours, minutes)
    for price in data:
        message += price + "\n"
    return message


def send_email(message, receivers):
    port = 465
    password = "DevelopmentNEU20"
    context = ssl.create_default_context()
    sender = "ajgc.development@gmail.com"

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("ajgc.development@gmail.com", password)
        for to in receivers:
            server.sendmail(sender, to, message)
    return


def run():
    res = requests.get("https://www.avaloncommunities.com/massachusetts/boston-apartments/avalon-north-station")
    parser = AVAParser()
    parser.feed(res.text)
    message = create_message(parser.data)
    to = ["ajgc98@gmail.com", "marcef1996@gmail.com"]
    send_email(message, to)


if __name__ == '__main__':
    run()

#!/usr/bin/python3

import requests
import smtplib
import ssl
import datetime
import json
import re
import os
from html.parser import HTMLParser

'''
1- Get data from website
2 - Read, compare, and write to json
3- Send email
4- Repeat every few hours
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


def parse_data(data):
    pattern = re.compile(r'(?P<type>\w+).*\$(?P<price>\d+)')
    new_prices = {}
    for line in data:
        match = pattern.search(line)
        if match:
            bedroom_type = match.group('type')
            price = match.group('price')
            if bedroom_type == "Studio":
                new_prices["Studio"] = int(price)
            elif bedroom_type == "1":
                new_prices["One"] = int(price)
            elif bedroom_type == "2":
                new_prices["Two"] = int(price)
            elif bedroom_type == "3":
                new_prices["Three"] = int(price)

    return new_prices


def compare_prices(other_prices):
    price_lowered = {"Studio": False, "One": False, "Two": False, "Three": False}
    with open('bedroom_prices.json') as previous_prices_json:
        previous_prices = json.load(previous_prices_json)
        if previous_prices["Studio"] > other_prices["Studio"]:
            price_lowered["Studio"] = True
        if previous_prices["One"] > other_prices["One"]:
            price_lowered["One"] = True
        if previous_prices["Two"] > other_prices["Two"]:
            price_lowered["Two"] = True
        if previous_prices["Three"] > other_prices["Three"]:
            price_lowered["Three"] = True
        print(previous_prices)
        print(other_prices)
        print(price_lowered)

def create_message(data):
    current_time = datetime.datetime.now()
    day = current_time.day
    month = current_time.strftime("%b")
    hours = current_time.strftime("%H")
    minutes = current_time.strftime("%M")
    message = "Subject: AVA North Station Prices\n" \
              "Hi, \n\n" \
              "The prices for AVA North Station on {0},{1} at {2}:{3} are:\n" \
              "".format(month, day, hours, minutes)
    for price in data:
        message += price + "\n"
    return message


def send_email(message, receivers):
    port = 465
    password = os.getenv("AJGC_SECRET")
    context = ssl.create_default_context()
    sender = "ajgc.development@gmail.com"

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("ajgc.development@gmail.com", password)
        for to in receivers:
            server.sendmail(sender, to, message)
    return



def run():
    res = requests.get(
        "https://www.avaloncommunities.com/massachusetts/boston-apartments/avalon-north-station")
    parser = AVAParser()
    parser.feed(res.text)
    new_prices = parse_data(parser.data)
    compare_prices(new_prices)
    message = create_message(parser.data)
    to = ["ajgc98@gmail.com", "marcef1996@gmail.com"]
    send_email(message, to)


if __name__ == '__main__':
    run()

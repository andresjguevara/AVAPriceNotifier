#!/usr/bin/python3

import requests
import smtplib
import ssl
import datetime
import json
import re
import os
from enum import Enum
from html.parser import HTMLParser

'''
1- Get data from website
2 - Read, compare, and write to json
3- Send email
4- Repeat every few hours
'''


class PriceChange(Enum):
    DECREASED = 0,
    NO_CHANGE = 1,
    INCREASED = 2

    def __str__(self):
        if self.value == 0:
            return str("Decrease in price")
        if self.value == 2:
            return str("Increase in price")
        if self.value == 1:
            return str("No change in price")


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


def compare_prices(new_prices):
    price_change = {"Studio": PriceChange.NO_CHANGE, "One": PriceChange.NO_CHANGE,
                    "Two": PriceChange.NO_CHANGE, "Three": PriceChange.NO_CHANGE}
    with open(os.curdir + '/bedroom_prices.json') as previous_prices_json:
        previous_prices = json.load(previous_prices_json)
        if previous_prices["Studio"] != new_prices["Studio"]:
            if previous_prices["Studio"] > new_prices["Studio"]:
                price_change["Studio"] = PriceChange.DECREASED
            else:
                price_change["Studio"] = PriceChange.INCREASED

        if previous_prices["One"] != new_prices["One"]:
            if previous_prices["One"] > new_prices["One"]:
                price_change["One"] = PriceChange.DECREASED
            else:
                price_change["One"] = PriceChange.INCREASED

        if previous_prices["Two"] != new_prices["Two"]:
            if previous_prices["Two"] > new_prices["Two"]:
                price_change["Two"] = PriceChange.DECREASED
            else:
                price_change["Two"] = PriceChange.INCREASED

        if previous_prices["Three"] != new_prices["Three"]:
            if previous_prices["Three"] > new_prices["Three"]:
                price_change["Three"] = PriceChange.DECREASED
            else:
                price_change["Three"] = PriceChange.INCREASED

        return price_change


def update_prices(new_prices):
    with open(os.curdir + '/bedroom_prices.json', 'w') as updated_prices:
        json.dump(new_prices, updated_prices)


def create_message(data, price_status):
    subject = "AVA PRICE CHANGE: "
    is_there_a_change = False
    for bedroom_type, status in price_status.items():
        if status != PriceChange.NO_CHANGE:
            is_there_a_change = True
            subject += bedroom_type + " "
            if bedroom_type != "Studio":
                subject += "Bedroom/ "

    # If no prices changed, then just return
    if not is_there_a_change:
        return None

    current_time = datetime.datetime.now()
    day = current_time.day
    month = current_time.strftime("%b")
    hours = current_time.strftime("%H")
    minutes = current_time.strftime("%M")
    message = "Subject: {0}\n" \
              "Hi, \n\n" \
              "The prices for AVA North Station on {1},{2} at {3}:{4} are:\n" \
              "".format(subject, month, day, hours, minutes)

    if price_status["Studio"] != PriceChange.NO_CHANGE:
        message += str(price_status["Studio"]) + ": " + data[0] + "\n"
    if price_status["One"] != PriceChange.NO_CHANGE:
        message += str(price_status["One"]) + ": " + data[1] + "\n"
    if price_status["Two"] != PriceChange.NO_CHANGE:
        message += str(price_status["Two"]) + ": " + data[2] + "\n"
    if price_status["Three"] != PriceChange.NO_CHANGE:
        message += str(price_status["Three"]) + ": " + data[3] + "\n"
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
    change_in_price = compare_prices(new_prices)
    update_prices(new_prices)
    message = create_message(parser.data, change_in_price)
    to = ["ajgc98@gmail.com", "marcef1996@gmail.com"]
    if message:
        send_email(message, to)


if __name__ == '__main__':
    run()

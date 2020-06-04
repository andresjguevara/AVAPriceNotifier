#!/usr/bin/python3

import requests
from html.parser import HTMLParser

'''
1- Connect to host
2- Send get request
3 - Parse HTML
4- Check for min price
5- Send email
6- Repeat every few hours
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
                    # print("Apartment Data")

    def handle_endtag(self, tag):
        if tag == "ul" and self.recording:
            self.recording = False

    def handle_data(self, data):
        if self.recording:
            self.data.append(data)



def run():
    res = requests.get("https://www.avaloncommunities.com/massachusetts/boston-apartments/avalon-north-station")
    parser = AVAParser()
    parser.feed(res.text)
    print(parser.data)


if __name__ == '__main__':
    run()

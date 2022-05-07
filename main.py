from msilib.schema import Error
import threading
import xml.etree.ElementTree as ET
import json
import requests
import time
from functools import partial

from tkinter import *


DEFAULT_URL = 'https://www.smartcrm.smartedgebusiness.com/suitecrm/index.php?entryPoint=generateLead'


def find(name, ext, url, uids, filename='AvayaOnexPortalClientLog.log'):
    with open(filename, 'r') as f:
        log = f.read()

    lines = log.splitlines()
    tagName = 'additionalCallInfo'
    i = 0
    for line in lines:
        i += 1
        if 'booleanFlag="true"><additionalCallInfo><callingPartyInfo external' in line:
            a = line.index(tagName)-1
            b = a + 2 + line[a + 2:].index(tagName) + len(tagName) + 1
            xmlPart = line[a:b]
            #print(str(a) + "  " + str(b))
            #print('line : ' + str(i) + "\n" + xmlPart)
            root = ET.fromstring(xmlPart)
            # print(root.tag)

            for child in root:
                if child.tag == 'callingPartyInfo':
                    calling = child
                elif child.tag == 'calledPartyInfo':
                    called = child
                elif child.tag == 'uniqueCallId':
                    uid = child.text

            if uid in uids:
                continue
            uids.add(uid)
            mobNum = '-1'
            if calling.attrib['callerName'] == name and calling.attrib['number'] == ext:
                mobNum = called.attrib['number']

            elif called.attrib['callerName'] == name and called.attrib['number'] == ext:
                mobNum = calling.attrib['number']
            if mobNum == '-1':
                print('Extension number mismatch')
                continue
            x = {"Mobile": str(mobNum), "ReferredBy": name,
                 "action": "generateLead"}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"}
            response = requests.post(url, headers=headers, json=x)
            print("Sent request for unique caller id = " +
                  str(uid) + " , json = " + str(x))
            print("Received response : json = " + str(response.json()) + '\n')


def start(nameField, extField, urlField):
    global running
    if running:
        print('Already running')
        return
    running = True
    name = nameField.get()
    ext = extField.get()
    url = urlField.get()
    uids = set()

    def loop():
        while running:
            find(name, ext, url, uids)
            time.sleep(1)
        print('Program Stopped.')
    thread = threading.Thread(target=loop)
    thread.start()


def stop():
    global running  # dirty but works
    running = False


# window
tkWindow = Tk()
tkWindow.geometry('400x150')
tkWindow.title('Log App')

nameLabel = Label(tkWindow, text="Name").grid(row=0, column=0)
name = StringVar()
nameEntry = Entry(tkWindow, textvariable=name).grid(row=0, column=1)

extLabel = Label(tkWindow, text="Extension Number").grid(row=1, column=0)
ext = StringVar()
extEntry = Entry(tkWindow, textvariable=ext).grid(row=1, column=1)


urlLabel = Label(tkWindow, text="Post URL").grid(row=2, column=0)
url = StringVar()
url.set(DEFAULT_URL)
urlEntry = Entry(tkWindow, textvariable=url).grid(row=2, column=1)

start = partial(start, name, ext, url)


running = False
startButton = Button(tkWindow, text="Start",
                     command=start).grid(row=4, column=0)

stopButton = Button(tkWindow, text="Stop",
                    command=stop).grid(row=5, column=0)

# testButton = Button(tkWindow, text="Test",
#                     command=test).grid(row=5, column=0)

tkWindow.mainloop()
running = False

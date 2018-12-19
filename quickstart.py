#!/usr/bin/python
# -*- coding: utf-8 -*-

# import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_Stepper

"""
Shows basic usage of the Google Calendar API. Creates a Google Calendar API
service object and outputs a list of the next 10 events on the user's calendar.
"""

from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
import time
import Adafruit_CharLCD as LCD
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, \
    Adafruit_StepperMotor
import time
import atexit
 
class EST5EDT(datetime.tzinfo):

    def utcoffset(self, dt):
        return datetime.timedelta(hours=-5) + self.dst(dt)

    def dst(self, dt):
        d = datetime.datetime(dt.year, 3, 8)        #2nd Sunday in March
        self.dston = d + datetime.timedelta(days=6-d.weekday())
        d = datetime.datetime(dt.year, 11, 1)       #1st Sunday in Nov
        self.dstoff = d + datetime.timedelta(days=6-d.weekday())
        if self.dston <= dt.replace(tzinfo=None) < self.dstoff:
            return datetime.timedelta(hours=1)
        else:
            return datetime.timedelta(0)

    def tzname(self, dt):
        return 'EST5EDT'

dt = datetime.datetime.now(tz=EST5EDT())

# Setup the Calendar API

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))

# Initialize the LCD using the pins

lcd = LCD.Adafruit_CharLCDPlate()
lcd.clear()
lcd.message(dt.strftime('%I:%M%p \n%m/%d/%y'))

print('Press Ctrl-C to quit.')

# create a default object, no changes to I2C address or frequency

mh = Adafruit_MotorHAT()


# recommended for auto-disabling motors on shutdown!

def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)


atexit.register(turnOffMotors)

myStepper = mh.getStepper(200, 1)  # 200 steps/rev, motor port #1
myStepper.setSpeed(50)  # 30 RPM

myStepper.step(540, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.MICROSTEP)

StepperPosition = 0;

positions = {
  'available': 270,
  'meeting soon': 100,
  'in a meeting': 440
}


def setNeedle(destination):
	global StepperPosition
	print(destination)
	print (StepperPosition)
	movementInterval = positions[destination] - StepperPosition
	if movementInterval > 0:
		myStepper.step(movementInterval, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.MICROSTEP)
	else:
		print('negative movements')
		myStepper.step(abs(movementInterval), Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.MICROSTEP)
	if positions[destination]:
	  StepperPosition = positions[destination]
	print (StepperPosition)

while True:
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    maxTimeThreshold = (datetime.datetime.utcnow()
                        + datetime.timedelta(hours=12)).isoformat() \
        + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 5 events')
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax=maxTimeThreshold,
        maxResults=5,
        singleEvents=True,
        orderBy='startTime',
        ).execute()
    events = events_result.get('items', [])
    if not events:
        dt = datetime.datetime.now(tz=EST5EDT())
        print('No upcoming events found.')
        lcd.clear()
        lcd.message(dt.strftime('%I:%M%p \n%m/%d/%y'
                    ))
        setNeedle('available')
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'
                    ].get('date'))
            print(start, event['summary'])
            lcd.clear()
            lcd.message(event['summary'])
            setNeedle('in a meeting')
            # DEMO MODE
            #setNeedle('available')
            #time.sleep(5)
            #setNeedle('meeting soon')
            #time.sleep(5)
            #setNeedle('in a meeting')

  # Loop through each button and check if it is pressed.

    time.sleep(60)


			
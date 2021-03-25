# FROM: https://bitbucket.org/kingmray/django-google-calendar/src/master/

import sys
import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
# import pytz

BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
CLIENT_SECRET_FILE = 'client_secrets.json' 
SCOPE = 'https://www.googleapis.com/auth/calendar'
SCOPES = [SCOPE]
APPLICATION_NAME = 'Google Calendar API Python'
    

def build_service():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CLIENT_SECRET_FILE,
        scopes=SCOPES
    )
    http = credentials.authorize(httplib2.Http())
    service = build('calendar', 'v3', http=http, cache_discovery=False)
    return service


def create_event(calendar_id, start, end, desc, ):
    service = build_service()
    event = service.events().insert(calendarId=calendar_id, body={
        'description':desc,
        'summary':desc,
        'start':{'dateTime':  start},
        'end':{'dateTime':  end},
    }).execute()
    return event['id']


def update_event(calendar_id, event_id, start, end, desc):
    service = build_service()
    try:
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    except HttpError as e:
        if e.resp.status==404:
            return create_event(calendar_id, start, end, desc)
    event["start"]={'dateTime':start}
    event["end"]={'dateTime':end}
    event["summary"]= desc
    event["description"]= desc
    updated_event = service.events().update(calendarId=calendar_id, eventId=event['id'], body=event).execute()
    return updated_event["id"]


create_event(
    calendar_id='2vnbp73e7is89rn8d3at26q3bo@group.calendar.google.com',
    start='2019-10-11T15:00:00.603111+00:00',
    end='2019-10-11T15:00:00.603111+00:00',
    desc='foobar')

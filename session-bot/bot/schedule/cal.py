import requests
import logging
import re
import os
import sys
import json
import datetime
import dateutil.parser
from .session import Session
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

from ...util import config

logger = logging.getLogger('session-bot')

def get_calendar():
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    SERVICE_ACCOUNT_INFO = config.config['google']['service_account']

    creds = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId=config.config['google']['cal_id'], timeMin=now,
                                          maxResults=1, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

def get_next_session():
    sys.stdout.flush()
    now = datetime.datetime.now()
    cal_session = Session()
    sessions = get_calendar()
    next_session = sessions[0]
    try:
        cal_session.start = dateutil.parser.parse(next_session['start']['dateTime'])
        cal_session.calendar_url = next_session['htmlLink']
        if 'location' in next_session and next_session['location'][:8] == "https://":
            cal_session.url = next_session['location']
        else:
            cal_session.url = cal_session.calendar_url

        # Clean up description
        description = next_session['description'].replace("&nbsp;", " ")
        description = description.replace("<br>", "\n")

        # Get Session attributes
        cal_session.title = get_title(description, next_session['summary'])
        cal_session.description = get_description(description)
        cal_session.speaker = get_speaker(description)
        cal_session.img_url = get_img(description)
    except Exception as e:
        logger.warning(f"Exception: {e}")

    return cal_session


def get_content(text, question):
    if question not in text:
        return None
    try:
        start_index = text.find(question) + len(question)
        end_index = text.find('\n', start_index)
        content = text[start_index:end_index]
        if len(content) < 256 and question != "Thumbnail: ":
            return content
        else:
            return content
    except Exception as e:
        logger.warning("Content not found in Calendar description")
        logger.warning(f"Exception: {e}")
        return None

def get_title(content, summary):
    question = 'What is the title of this session?: '
    title = get_content(content, question)
    if title == None:
        return summary
    return title

def get_description(content):
    question = 'Please describe this session in 3-5 sentences. This will be shared with the fellows: '
    description = get_content(content, question)
    if description == None:
        return ""
    return description

def get_speaker(content):
    question = "Speaker: "
    return get_content(content, question)

def get_img(content):
    question = "Thumbnail: "
    url = get_content(content, question)
    if url != None:
        regex = re.compile('(?<=href=").*?(?=")')
        urls = regex.findall(url)
        if len(urls) > 0:
            return urls[0]
    return url

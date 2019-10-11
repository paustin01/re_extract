'''
AWS re:Invent Session Information Downloader
'''

import os
import re
from time import sleep

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SESSION_TYPES = {
    "2624": "Builders Session",
    "2623": "Chalk Talk",
    "2": "Session",
    "2523": "Workshop",
    "2723": "20-Minute Presentation"
}

TOPICS = {
    "32821": "Alexa",
    "32822": "Analytics",
    "32851": "Architecture",
    "32852": "Artificial Intelligence & Machine Learning",
    "32853": "Blockchain",
    "32854": "Compute",
    "32855": "Containers",
    "32856": "Databases",
    "32857": "DevOps",
    "32859": "End User Computing & Business Apps",
    "32860": "Enterprise",
    "32861": "IoT",
    "32862": "Management Tools & Governance",
    "32863": "Marketplace",
    "32864": "Media Solutions",
    "32865": "Mobile",
    "32866": "Networking & Content Delivery",
    "32867": "Open Source",
    "32868": "Partner",
    "32870": "Robotics",
    "32871": "Security, Compliance, and Identity",
    "32872": "Serverless",
    "32873": "Storage",
    "32874": "We Power Tech",
    "32875": "Windows & .Net"
}

# Get environment variables
load_dotenv(dotenv_path='.env')
USERNAME = os.environ["REINVENT_USERNAME"]
PASSWORD = os.environ["REINVENT_PASSWORD"]
CHROME_DRIVER = os.environ["CHROMEDRIVER_PATH"]
REQ_VERIFY = bool(os.environ["VERIFY_SSL_CERTS"].lower() == 'true')

# Initialize headless chrome
CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument("--headless")
CHROME_OPTIONS.add_argument(f"user-agent={os.environ['CHROMEDRIVER_USER_AGENT']}")
CONTENT_TO_PARSE = ''

DRIVER = webdriver.Chrome(chrome_options=CHROME_OPTIONS, executable_path=CHROME_DRIVER)

def login(chrome_driver, username, password):
    '''
    Handle user login to the reinvent session catalog.
    Utilizes headless chrome, passing in username and password
    '''
    chrome_driver.get("https://www.portal.reinvent.awsevents.com/connect/login.ww")
    cookie_button = chrome_driver.find_element_by_id("cookieAgreementAcceptButton")
    DRIVER.implicitly_wait(5)
    cookie_button.click()
    username_field = chrome_driver.find_element_by_id("loginUsername")
    username_field.send_keys(username)
    password_field = chrome_driver.find_element_by_id("loginPassword")
    password_field.send_keys(password)
    login_button = chrome_driver.find_element_by_id("loginButton")
    login_button.click()

def session_details(_session_id):
    '''
    Calls the API on the reinvent event website which returns session times.
    Outputs a JSON object with time and room information for a specific session.
    '''
    details_url = 'https://www.portal.reinvent.awsevents.com/connect/dwr/call/' \
                  'plaincall/ConnectAjax.getSchedulingJSON.dwr'

    data = {
        "callCount": 1,
        "windowName": "",
        "c0-scriptName": "ConnectAjax",
        "c0-methodName": "getSchedulingJSON",
        "c0-id": 0,
        "c0-param0": "number:" + _session_id,
        "c0-param1": "false",
        "batchId": 5,
        "instanceId": 0,
        "page": "%2Fconnect%2Fsearch.ww",
        "scriptSessionId": "1234567"
    }
    headers = {'Content-Type': 'text/plain', 'User-Agent': os.environ['CHROMEDRIVER_USER_AGENT']}
    response = requests.post(details_url, headers=headers, data=data, verify=REQ_VERIFY)
    returned = response.content.decode('utf-8').replace("\\", '')

    if 'startTime' in returned:
        timestamp = re.search(r"startTime\":(\".*?\")", returned, re.DOTALL | re.MULTILINE).group(1)
        day = timestamp.replace('"', '').split(", ")[0]
        date = timestamp.replace('"', '').split(", ")[1]
        start_time = timestamp.replace('"', '').split(", ")[2]
    else:
        day = 'Unknown'
        date = 'Unknown'
        start_time = 'Unknown'

    if 'endTime' in returned:
        end_time = re.search(r"endTime\":(\".*?\")", returned, re.DOTALL | re.MULTILINE).group(1)
        end_time = end_time.replace('"', '')
    else:
        end_time = 'Unknown'

    if 'room' in returned:
        text = re.search(r"room\":(\".*?\")", returned, re.DOTALL | re.MULTILINE).group(1)
        text = text.replace('"', '').replace('|', ',')
        venue = text.split(',')[0].strip()
        room = ','.join(text.split(',')[1:]).strip()
    else:
        venue = 'Unknown'
        room = 'Unknown'

    time_information = {
        "day": day,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "venue": venue,
        "room": room
    }

    return time_information

# Open a blank text file to write sessions to
OUTPUT_FILE = 'sessions.txt'

# Create a header row for the file. Note the PIPE (|) DELIMITER.
with open(OUTPUT_FILE, "w") as myfile:
    myfile.write("Session ID|Title|Type|Topic|Day|Date|Start|End|Venue|Room|Interest|Abstract\n")

# Login to the reinvent website
login(DRIVER, USERNAME, PASSWORD)

# Getting content by session type, instead of the entire set, because sometimes the
# Get More Results link stops working on the full list. Haven't had issues
# looking at the lists by session.
for session_type_id, session_type_name in SESSION_TYPES.items():
    for topic_id, topic_name in TOPICS.items():
        url = "https://www.portal.reinvent.awsevents.com/connect/search.ww#" \
               "loadSearch-searchPhrase=" \
               "&searchType=session" \
               "&tc=0" \
               "&sortBy=" \
               f"abbreviationSort&sessionTypeID={session_type_id}" \
               f"&p=&i(19577)={topic_id}"
        DRIVER.get('chrome://settings/clearBrowserData')
        DRIVER.get(url)
        sleep(3)

        print(f"Getting {session_type_name} sessions for topic: {topic_name}")
        more_results = True

        # Click through all of the session results pages for a session.
        while more_results:
            try:
                DRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                get_results_btn = DRIVER.find_element_by_link_text("Get More Results")
                get_results_btn.click()
                sleep(3)
            except NoSuchElementException as e_error:
                more_results = False

        # Once all sessions have been loaded append to a variable for use in BS
        CONTENT_TO_PARSE = DRIVER.page_source

        # Extract high level session info. Note that in some rows there are audio
        # options inside an 'i' tag so we strip them out to make this easier on BS
        soup = BeautifulSoup(CONTENT_TO_PARSE, "html.parser")

        for i in soup.find_all('i'):
            i.extract()

        sessions = soup.find_all("div", class_="sessionRow")

        # For each session, pull out the relevant fields and write them to the sessions.txt file.
        for session in sessions:
            session_soup = BeautifulSoup(str(session), "html.parser")
            session_id = session_soup.find("div", class_="sessionRow")
            session_id = session_id['id']
            session_id = session_id[session_id.find("_")+1:]
            session_number = session_soup.find("span", class_="abbreviation")
            session_number = session_number.string.replace(" - ", "")
            session_title = session_soup.find("span", class_="title")
            session_title = session_title.string.encode('utf-8').rstrip()
            session_title = session_title.decode('utf-8').strip()
            session_type = session_soup.find("small", class_="type").text
            session_interest = session_soup.find("a", class_="interested")
            session_abstract = \
                session_soup.find("span", class_="abstract").text.replace(' View More', '')
            details = session_details(session_id)

            print("Writing", session_number)

            if session_interest is None:
                session_interest = False
            else:
                session_interest = True

            write_contents = \
                str(session_number) + "|" + \
                str(session_title) + "|" + \
                str(session_type) + "|" + \
                topic_name + "|" + \
                str(details['day']) + "|" + \
                str(details['date']) + "|" + \
                str(details['start_time']) + "|" + \
                str(details['end_time']) + "|" + \
                str(details['venue']) + "|" + \
                str(details['room']) + "|" + \
                str(session_interest) + "|" + \
                str(session_abstract)

            with open(OUTPUT_FILE, "a") as myfile:
                myfile.write(str(write_contents.strip()) + "\n")

DRIVER.close()

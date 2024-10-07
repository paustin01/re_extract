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

# Session types and topics were used for filtering prior to the site adding
# venue and day information. Leaving in but commented out in case needed later.

# SESSION_TYPES = {
#     "2624": "Builders Session",
#     "2623": "Chalk Talk",
#     "2": "Session",
#     "2523": "Workshop",
#     "2723": "20-Minute Presentation"
# }

# TOPICS = {
#     "32821": "Alexa",
#     "32822": "Analytics",
#     "32851": "Architecture",
#     "32852": "Artificial Intelligence & Machine Learning",
#     "32853": "Blockchain",
#     "32854": "Compute",
#     "32855": "Containers",
#     "32856": "Databases",
#     "32857": "DevOps",
#     "32859": "End User Computing & Business Apps",
#     "32860": "Enterprise",
#     "32861": "IoT",
#     "32862": "Management Tools & Governance",
#     "32863": "Marketplace",
#     "32864": "Media Solutions",
#     "32865": "Mobile",
#     "32866": "Networking & Content Delivery",
#     "32867": "Open Source",
#     "32868": "Partner",
#     "32870": "Robotics",
#     "32871": "Security, Compliance, and Identity",
#     "32872": "Serverless",
#     "32873": "Storage",
#     "32874": "We Power Tech",
#     "32875": "Windows & .Net"
# }

VENUES = {
    "1714149514282003u0NO": "Mandalay Bay",
    "1714149514282001ui9z": "Caesars Forum",
    "1714149514282004uw2u": "MGM",
    "1714149514282006uDYu": "Venetian",
    "1714149514282007uKju": "Wynn"
}

DAYS = {
    "20241201": "Sunday",
    "20241202": "Monday",
    "20241203": "Tuesday",
    "20241204": "Wednesday",
    "20241205": "Thursday",
    "20241206": "Friday"
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

DRIVER = webdriver.Chrome(options=CHROME_OPTIONS, executable_path=CHROME_DRIVER)

def login(chrome_driver, username, password):
    '''
    Handle user login to the reinvent session catalog.
    Utilizes headless chrome, passing in username and password
    '''
    chrome_driver.get("https://registration.awsevents.com/flow/awsevents/reinvent24/reg/login")
    try:
        print("*** Attempting to Accept Cookie Policy")
        cookie_button = chrome_driver.find_element_by_css_selector("[data-id='awsccc-cb-btn-accept']")
        DRIVER.implicitly_wait(5)
        cookie_button.click()
    except:
        print("*** Assuming Cookie Policy already accepted")

    username_field = chrome_driver.find_element_by_css_selector("[data-test='rf-text-input-node-login-email']")
    username_field.send_keys(username)
    password_field = chrome_driver.find_element_by_css_selector("[data-test='rf-text-input-node-password']")
    password_field.send_keys(password)
    login_button = chrome_driver.find_element_by_css_selector("[data-test='rf-button-button-login']")
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

# Parse interests.txt file to get list we can check against while we navigate site
interests_file = 'interests.txt'
interests_list = {}
try:
    for line in open(interests_file):
        parts = line.rstrip('\n').split(",")
        if len(parts) > 1:
            line = parts[0]
            priority = parts[1]
        else:
            line = parts[0]
            priority = "1"
        interests_list[("".join(line.upper().rstrip('\n').split('-')))] = priority
except:
    print("If you would like to have this script favorite your sessions, please create an interests.txt file.")

# Open a blank text file to write sessions to
OUTPUT_FILE = 'sessions.txt'

# Create a header row for the file. Note the PIPE (|) DELIMITER.
with open(OUTPUT_FILE, "w") as myfile:
    myfile.write("Session ID|Title|Interest|Priority|Topic|Type|Day|Date|Start|End|Venue|Room|Abstract\n")

# Login to the reinvent website
print("*** Logging in")
login(DRIVER, USERNAME, PASSWORD)
sleep(8)

# Getting content by multiple filters in order to get a smaller subset of results
# because the site stops paging a 300 items
total_sessions = 0
for day_id, day_name in DAYS.items():
    # for venue_id, venue_name in VENUES.items():
    # url = f"https://registration.awsevents.com/flow/awsevents/reinvent24/sessioncatalog/page/page?search.day={day_id}&search.venue={venue_id}"
    url = f"https://registration.awsevents.com/flow/awsevents/reinvent24/sessioncatalog/page/page?search.day={day_id}"
    DRIVER.get('chrome://settings/clearBrowserData')
    DRIVER.get(url)
    sleep(8)

    # print(f"*** Getting sessions on {day_name} for {venue_name}")
    print(f"*** Getting sessions on {day_name}")
    more_results = True

    # Click through all of the session results pages for a session.
    while more_results:
        try:
            DRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            get_results_btn = DRIVER.find_element_by_css_selector("[data-test='rf-button-learn-more']")
            print("*** Clicking Show more")
            get_results_btn.click()
            sleep(3)
        except NoSuchElementException as e_error:
            more_results = False

    # Click on all Interest buttons found in interests.txt
    try:
        interest_buttons_on_page = DRIVER.find_elements_by_css_selector("[data-test='rf-icon-interest']")
        for item in interest_buttons_on_page:
            item_session_id = re.search('^Click to favorite (.+?) \||^Click to un-favorite (.+?) \|', item.get_attribute('aria-label'))
            if item_session_id:
                if item_session_id.group(1) is None:
                    item_session_id = item_session_id.group(2)
                else:
                    item_session_id = item_session_id.group(1)

                serssion_id = "".join(item_session_id.upper().rstrip('\n').split('-'))
                if serssion_id in interests_list:
                    # Click if the button is not marked as interested yet
                    is_pressed = item.get_attribute('aria-pressed')
                    if is_pressed == "true":
                        print(f"Found a match in interests.txt for session {item_session_id}, already favorited...")
                    else:
                        print(f"Found a match in interests.txt for session {item_session_id}, clicking to favorite...")
                        DRIVER.execute_script("arguments[0].click();", item)



    except NoSuchElementException as e_error:
        print("*** Didn't find any interest buttons")

    # Once all sessions have been loaded append to a variable for use in BS
    CONTENT_TO_PARSE = DRIVER.page_source

    # Extract high level session info. Note that in some rows there are audio
    # options inside an 'i' tag so we strip them out to make this easier on BS
    soup = BeautifulSoup(CONTENT_TO_PARSE, "html.parser")

    for i in soup.find_all('i'):
        i.extract()

    sessions = soup.find_all("li", {"class": "session-result"})
    print('*** Found Sessions:', len(sessions))
    total_sessions += len(sessions)

    # For each session, pull out the relevant fields and write them to the sessions.txt file.
    for session in sessions:
        session_soup = BeautifulSoup(str(session), "html.parser")

        session_id = session_soup.get("data-session-id")
        parts = session_soup.find("div", class_="title-text").text.rstrip().split(" | ")
        session_number = parts[0] if len(parts) > 0 else "TBD"
        session_title = parts[1] if len(parts) > 1 else "TBD"
        session_abstract = session_soup.find("div", class_="description").text
        session_type = session_soup.find("div", class_="rf-session-types").text

        session_topics = session_soup.find_all("div", class_="badge-attribute-topic")
        session_topics = [item.text for item in session_topics]
        session_topics = ", ".join(session_topics)

        # The filled/not filled Heart Icon depicts whether you have favorited the course
        session_interest = session_soup.find("svg",
                                                 attrs={"data-title": "Heart Icon"})

        session_not_interest = session_soup.find("svg",
                                                 attrs={"data-title": "Heart Open Icon"})

        # TODO: Update session_details function, until then parse main page
        #  details = session_details(session_id)
        details = {
            "day": "TBD",
            "date": "TBD",
            "start_time": "TBD",
            "end_time": "TBD",
            "venue": "TBD",
            "room": "TBD"
        }

        # Example Day: Monday, December 2
        session_day = session_soup.find("span", class_="session-date")
        if session_day is not None:
            session_day = session_day.text
            parts = session_day.split(", ")
            if len(parts) > 0:
                details['day'] = parts[0]
            if len(parts) > 1:
                details['date'] = parts[1]

        # Example Time: 8:00 AM - 10:00 AM PST
        session_time = session_soup.find("span", class_="session-time")
        if session_time is not None:
            session_time = session_time.text
            parts = session_time.split(" - ")
            if len(parts) > 0:
                details['start_time'] = parts[0]
            if len(parts) > 1:
                details['end_time'] = " ".join(parts[1].split(" ")[0:2])  # remove PST

        # Example Location: MGM | Level 1 | Grand 123
        session_location = session_soup.find("span", class_="session-location")
        if session_location is not None:
            session_location = session_location.text

            # Sessions like Dev chats have a trailing "|" we just need to truncate
            if session_location[-1] == "|":
                session_location = session_location[:-1]

            # Sessions like re:Play don't have a venue, just starts with "| "
            if session_location[:1] == "|":
                details['venue'] = "Unknown"
                session_location = session_location[2:]
                parts = session_location.split(" | ")
                if len(parts) > 0:
                    details['room'] = " - ".join(parts)
            else:
                parts = session_location.split(" | ")
                if len(parts) > 0:
                    details['venue'] = parts[0]
                if len(parts) > 1:
                    details['room'] = " - ".join(parts[1:])

        # print("Writing", session_number)
        if session_interest is None:
            session_interest = False
            session_interest_priority = ""
        else:
            session_interest = True
            session_interest_priority = "1"

        write_contents = \
            str(session_number) + "|" + \
            str(session_title) + "|" + \
            str(session_interest) + "|" + \
            str(session_interest_priority) + "|" + \
            str(session_topics) + "|" + \
            str(session_type) + "|" + \
            str(details['day']) + "|" + \
            str(details['date']) + "|" + \
            str(details['start_time']) + "|" + \
            str(details['end_time']) + "|" + \
            str(details['venue']) + "|" + \
            str(details['room']) + "|" + \
            str(session_abstract)

        with open(OUTPUT_FILE, "a") as myfile:
            myfile.write(str(write_contents.strip()) + "\n")

print('*** TOTAL Sessions:', total_sessions)
DRIVER.close()

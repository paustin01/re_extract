# Re:extract
`re_extract.py` is a tool for extracting the AWS re:Invent schedule to a CSV for
easier planning. This project also contains a script called `interests.py` which
can take a list of session IDs you're interested in and mark them in the
resulting `sessions.txt` file output of the extract process. This is useful for
being able to plan out things that you're interested in ahead of time and then
being able to reextract (no pun intended) the catalog multiple times over to get
the freshest content and not lose the things you were interested in.

## Credits
`re_extract.py` is heavily based on the `mda590/reinvent_schedule_extract` repo.
Because that repo hadn't been made to work successfully since re:Invent 2017, I
had enough fixes and usage changes that I felt it warranted more than a fork so
others can discover and help maintain it.

# Extracting
## Usage
1. Use the python version specified in `.python-version` file (recommend using
   pyenv for this)
2. Install requirements via `pip install -r requirements.txt` (recommend using
   venv for this)
3. Download the appropriate version of the Chrome web driver for your Chrome
   browser version into the root of this project directory (Don't worry, it's
   `.gitignore`'d)
   - https://sites.google.com/a/chromium.org/chromedriver/downloads
4. Duplicate the `example.env` file as simply `.env` and update configuration as
   appropriate (see configuration section below)
5. Run the script

The `pyenv` and `venv` patterns ensure this behaves the same way on your system
as it does on mine which is why I showed that model in the example below. If you
choose to use your system python and non vendored packages you may run into
compatibility issues.

### Step-by-step setup
```bash
# Clone this repo and change into the directory
git clone <this repo>
cd re_extract

# The .env file from the example and update per the config section below
cp example.env .env
nano .env

# Use pyenv to auto-install the version of python in the .python-version file
pyenv install

# Setup pip package vendoring
python -m venv venv
source venv/bin/activate

# Install/vendor the packages
pip install -r requirements.txt

# Do the thing
python re_extract.py
```

When done, open the `sessions.txt` file in Excel or spreadsheet app of choice

## Configuration
The `example.env` file in this project must be copied as simply `.env` and
updated per these suggestions:

| Item                      | Notes                                                   |
|---------------------------|---------------------------------------------------------|
| `REINVENT_USERNAME`       | Your username for the re:Invent catalog site            |
| `REINVENT_PASSWORD`       | Your password for the re:Invent catalog site            |
| `VERIFY_SSL_CERTS`        | Set to False to ignore cert warnings                    |
| `CHROMEDRIVER_PATH`       | Path to the chromedriver executable you downloaded      |
| `CHROMEDRIVER_USER_AGENT` | The user-agent to spoof to avoid 403's. See notes below |

### Spoofing the user agent
In 2019 they started adding headless user agent detection and throwing 403's if
detected. Update this value to the appropriate string for the version of chrome
you're using. Since you have to download the version of chromedriver which
matches the version of chrome you have installed anyway, go to this site:
https://www.whatismybrowser.com/detect/what-is-my-user-agent and copy the user
agent string and insert that into the .env file.


# Marking interests
The `interests.py` takes an input file called `interests.txt` which is simply a
line-separated list of session ID's you're interested in and marks them as true
in the Interest column in the sessions.txt file.

## Usage
Once you've run your extract and the `sessions.txt` file exists, and created the
interests.txt file full of ID's you're interested in, just run it.

```bash
python interests.py
```

# Notes on design choices
- As the original credited developer noted, the reinvent session catalog site is
  terrible and just stops paging at some point. To be safe I have it doing much
  smaller chunks at a time (with sleeps to allow for slow loading) by way of
  filtered searches, looping through session types and topics. This was the only
  way I could reliably capture 99% of the catalog contents (some sessions aren't
  categorized at all!)
- I probably could have made it pull session types and topics dynamically but
  just didn't put that time in. Feel free if the spirit moves you and do a PR.
- The `.env` configuration model is a fairly common pattern in many apps.
  Didn't want the user to have to enter creds at the command line or edit source

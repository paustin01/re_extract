# Re:extract
A tool for extracting the AWS re:Invent schedule to a CSV for easier planning

## Credits
The script is heavily based on the `mda590/reinvent_schedule_extract` repo.
Because that repo hadn't been made to work successfully since re:Invent 2017, I
had enough fixes and usage changes that I felt it warranted more than a fork so
others can discover and help maintain it.

# Usage
1. Use the python version specified in `.python-version` file (recommend using
   pyenv for this)
2. Install requirements via `pip install -r requirements.txt` (recommend using
   venv for this)
3. Download the appropriate version of the Chrome web driver for your Chrome
   browser version into the root of this project directory (Don't worry, it's
   `.gitignore`'d)
   - https://sites.google.com/a/chromium.org/chromedriver/downloads
4. Duplicate the `example.env` file as simply `.env` and update configuration as
   appropriate
5. Run the script

The `pyenv` and `venv` patterns ensure this behaves the same way on your system
as it does on mine which is why I showed that model in the example below. If you
choose to use your system python and non vendored packages you may run into
compatibility issues.

## Step-by-step setup
```bash
# Clone this repo and change into the directory
git clone <this repo>
cd re_extract

# Duplicate the example.env file as .env and edit the contents as appropriate
# Note you will probably need to set `VERIFY_SSL_CERTS` to "False" to avoid
# failing on cert issues
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

When done, open the `sessions.txt` file in Excel or spreadsheet app of choise

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

import collections
import csv
import io
import logging
import os
import re
import sys
import time
import urllib.parse
from datetime import datetime

import configparser
import pandas as pd
import pytz
import requests


# Module information.
__author__ = 'Anthony Farina'
__copyright__ = 'Copyright 2021, PRTG Device IP Changer'
__credits__ = ['Anthony Farina']
__license__ = 'MIT'
__version__ = '1.0.1'
__maintainer__ = 'Anthony Farina'
__email__ = 'farinaanthony96@gmail.com'
__status__ = 'Released'


# General global variables.
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

# Global variables from the config file for easy referencing.
CONFIG = configparser.ConfigParser()
CONFIG_PATH = '/../configs/PRTG-Device-IP-Changer-config.ini'
CONFIG.read(SCRIPT_PATH + CONFIG_PATH)
SERVER_URL = CONFIG['PRTG Info']['server-url']
USERNAME = urllib.parse.quote_plus(CONFIG['PRTG Info']['username'])
PASSWORD = urllib.parse.quote_plus(CONFIG['PRTG Info']['password'])
PASSHASH = urllib.parse.quote_plus(CONFIG['PRTG Info']['passhash'])
TIMEZONE = CONFIG['Timezone Info']['timezone']
CSV_FILE = CONFIG['CSV Info']['file-name']


# This method will go through the provided CSV file of devices and their new
# IP addresses. Then it will edit each listed device to their new IP address
# listed in the provided CSV file. It will log everything in a log file.
def prtg_device_ip_changer() -> None:
    # Make a logger that logs what's happening in a log file and the console.
    now_log = datetime.utcnow().replace(tzinfo=pytz.UTC).astimezone(
        pytz.timezone(TIMEZONE))
    logging.basicConfig(filename=SCRIPT_PATH + '/../logs/ip_changer_log-' +
                        now_log.strftime('%Y-%m-%d_%I-%M-%S-%p-%Z') + '.log',
                        level=logging.INFO,
                        format='[%(asctime)s] [%(levelname)s] %(message)s',
                        datefmt='%m-%d-%Y %I:%M:%S %p %Z')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    # Prepare the URL to get all device information from PRTG.
    device_url = SERVER_URL + \
                 '/api/table.xml?content=devices&columns=' \
                 'name,objid,group' \
                 '&output=csvtable&count=50000' \
                 '&username=' + USERNAME
    device_url = add_auth(device_url)

    # Get the device information from PRTG.
    logging.info('Retrieving all devices from PRTG...')
    device_resp = requests.get(url=device_url)
    logging.info('All devices retrieved from PRTG!')

    # Make a clean dataframe object from the device information received from
    # PRTG.
    logging.info('Formatting response from PRTG...')
    device_resp_csv_strio = io.StringIO(device_resp.text)
    device_csv_reader = csv.reader(device_resp_csv_strio,
                                   delimiter=',')

    # Make the device ID dictionary.
    # device[0] is the device's name (the key)
    # device[2] is the device's object ID (the value)
    device_id_dict = collections.defaultdict(str)

    for device in device_csv_reader:
        device_id_dict[device[0]] = device[2]

    # Load provided CSV of devices and their new IP addresses.
    new_ip_csv_reader = csv.reader(open(CSV_FILE))
    next(new_ip_csv_reader)
    logging.info('Response from PRTG has been formatted!')

    # Count the number of successful and unsuccessful edits along with the
    # connection reuse object.
    edits = 0
    errors = 0
    edit_sess = requests.Session()

    # Iterate through all devices and edit specified devices by name.
    for device in new_ip_csv_reader:
        # Log that we are about to make a change to a device.
        logging.info('Editing the IP address of device \"' +
                     device[0] + '\" (ID: ' +
                     device_id_dict[device[0]] + ') from PRTG...')

        # Prepare the edit URL.
        edit_ip_url = SERVER_URL + '/api/setobjectproperty.htm?id=' + \
                      device_id_dict[device[0]] + \
                      '&name=host&value=' + device[1] + \
                      '&username=' + USERNAME
        edit_ip_url = add_auth(edit_ip_url)

        # Send the edit request to PRTG.
        time.sleep(10)
        edit_ip_resp = edit_sess.get(url=edit_ip_url)

        # Check if the IP address edit was successful.
        if edit_ip_resp.status_code != 200:
            logging.error('Error changing the IP address of device \"'
                          + device[0] + '\" (ID: '
                          + device_id_dict[device[0]] + ' in PRTG.')
            logging.error('Caused by: ' + str(edit_ip_resp.status_code))
            logging.error(edit_ip_resp.reason)
            errors += 1
        # The IP address edit was successful.
        else:
            logging.info('Device \"' + device[0] + '\" (ID: ' +
                         device_id_dict[device[0]] +
                         ') IP address successfully changed to ' +
                         device[1] + '!')
            edits += 1

    # Close the connection to PRTG.
    edit_sess.close()

    # Log the results and end the script.
    logging.info('')
    logging.info('===========================================================')
    logging.info('')
    logging.info('Device IP address change job completed.')
    logging.info('Total device IP address edits: ' + str(edits))
    logging.info('Total device IP address edit errors: ' + str(errors))


# Every time table information is called from the PRTG API, the response has
# 'readable' columns and 'raw' columns. Their are subtle differences,
# but the raw columns are not needed. This function removes all the 'raw'
# columns from a dataframe object of the PRTG API response and returns a
# dataframe object with only the non-raw columns.
def remove_raw(raw_df: pd.DataFrame) -> pd.DataFrame:
    # Prepare a list of desired column names.
    col_labels = list()

    # Iterate through the column labels to remove column labels ending with
    # '(RAW)'.
    for col in raw_df.columns:
        # Add only desired column labels to the list.
        if not bool(re.search('\\(RAW\\)$', col)):
            col_labels.append(col)

    # Return the dataframe object that only has desired columns.
    return_df = raw_df[col_labels]
    return return_df


# This function will append the PRTG authentication to the end of the given
# PRTG API call URL. It will append either the password or passhash,
# whichever was provided in the config file. Passhash has priority if both
# fields are filled in.
def add_auth(url: str) -> str:
    # Check if the password or passhash will be used to authenticate the
    # access to the PRTG instance.
    if PASSHASH == '':
        url = url + '&password=' + PASSWORD
    else:
        url = url + '&passhash=' + PASSHASH

    return url


# The main method that runs the script. There are no input arguments.
if __name__ == '__main__':
    # Check to make sure the logs folder exists. If not, create it.
    if not os.path.isdir(SCRIPT_PATH + '/../logs'):
        os.mkdir(SCRIPT_PATH + '/../logs')

    # Run the script.
    prtg_device_ip_changer()

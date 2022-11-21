import configparser
import logging
import os
import sys
import time
from datetime import datetime as dt

import pytz
import requests


# Module information.
__author__ = 'Anthony Farina'
__copyright__ = 'Copyright (C) 2022 Computacenter Digital Innovation'
__credits__ = ['Anthony Farina']
__maintainer__ = 'Anthony Farina'
__email__ = 'farinaanthony96@gmail.com'
__license__ = 'MIT'
__version__ = '1.0.2'
__status__ = 'Released'


# General global variables.
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

# Global variables from the config file for easy referencing.
CONFIG = configparser.ConfigParser()
CONFIG_PATH = '/../configs/PRTG-Device-IP-Changer-config.ini'
CONFIG.read(SCRIPT_PATH + CONFIG_PATH)

# PRTG global variables.
PRTG_INSTANCE_URL = CONFIG['PRTG Info']['server-url']
PRTG_API_TABLE = '/api/table.xml'
PRTG_FETCH_URL = PRTG_INSTANCE_URL + PRTG_API_TABLE
PRTG_API_CHANGE_PROPERTY = '/api/setobjectproperty.htm'
PRTG_CHANGE_PROPERTY_URL = PRTG_INSTANCE_URL + PRTG_API_CHANGE_PROPERTY
PRTG_USERNAME = CONFIG['PRTG Info']['username']
PRTG_PASSWORD = CONFIG['PRTG Info']['password']

# Other global variables from the config file.
TIMEZONE = CONFIG['Timezone Info']['timezone']


# Given a dictionary of devices and their desired IPv4 address
# changes, change those device's IPv4 addresses in PRTG.
def prtg_device_ip_changer(prtg_device_dict: dict) -> None:
    # Make a logger that logs to a file and the console.
    now_dt = dt.utcnow().replace(tzinfo=pytz.UTC).astimezone(
        pytz.timezone(TIMEZONE))
    logging.basicConfig(filename=(
                            SCRIPT_PATH +
                            '/../logs/prtg_device_ip_changer_log_' +
                            now_dt.strftime('%Y-%m-%d_%I-%M-%S-%p-%Z') +
                            '.log'),
                        level=logging.INFO,
                        format='[%(asctime)s] [%(levelname)s] %(message)s',
                        datefmt='%m-%d-%Y %I:%M:%S %p %Z')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    # Get the device information from PRTG and convert it to JSON.
    logging.info('Retrieving devices from PRTG...')
    prtg_devices_resp = requests.get(url=PRTG_FETCH_URL,
                                     params={
                                        'content': 'devices',
                                        'columns': 'group,name,objid,host',
                                        'filter_name': list(
                                            prtg_device_dict.keys()),
                                        'count': '50000',
                                        'output': 'json',
                                        'username': PRTG_USERNAME,
                                        'password': PRTG_PASSWORD
                                     })
    prtg_devices = prtg_devices_resp.json()
    logging.info('Devices retrieved from PRTG!')

    # Count the number of successful and unsuccessful edits along with
    # the connection session object.
    edits = 0
    errors = 0
    edit_sess = requests.Session()

    # Iterate through the devices and edit their IP addresses.
    for prtg_device in prtg_devices['devices']:
        # Log the IP change for this device.
        logging.info('Editing the IP address of device ' +
                     prtg_device['group'] + ' > ' + prtg_device['name'] +
                     ' from + ' + prtg_device['host'] + ' to ' +
                     prtg_device_dict[prtg_device['name']] + '...')

        # Send the edit request to PRTG.
        time.sleep(2)
        edit_ip_resp = edit_sess.get(url=PRTG_CHANGE_PROPERTY_URL,
                                     params={
                                         'id': prtg_device['objid'],
                                         'name': 'host',
                                         'value':
                                             prtg_device_dict[
                                                 prtg_device['name']],
                                         'username': PRTG_USERNAME,
                                         'password': PRTG_PASSWORD
                                     })

        # Check if the edit was unsuccessful.
        if edit_ip_resp.status_code != 200:
            logging.error('Error changing the IP address of device ' +
                          prtg_device['group'] + ' > ' + prtg_device['name'] +
                          ' to ' + prtg_device_dict[prtg_device['name']] +
                          ' in PRTG.')
            logging.error('Caused by: ' + str(edit_ip_resp.status_code))
            logging.error(edit_ip_resp.reason)
            errors += 1
        # The IP address edit was successful.
        else:
            logging.info('Device ' + prtg_device['group'] + ' > ' +
                         prtg_device['name'] +
                         ' IP address successfully changed to ' +
                         prtg_device_dict[prtg_device['name']] + '!')
            edits += 1

    # Close the connection session to PRTG.
    edit_sess.close()

    # Log the results and end the script.
    logging.info('')
    logging.info('===========================================================')
    logging.info('')
    logging.info('Device IP address change job completed.')
    logging.info('Total device IP address edits: ' + str(edits))
    logging.info('Total device IP address edit errors: ' + str(errors))


# The main method that runs the script. There are no input arguments.
if __name__ == '__main__':
    # Check to make sure the "logs" folder exists. If not, create it.
    if not os.path.isdir(SCRIPT_PATH + '/../logs'):
        os.mkdir(SCRIPT_PATH + '/../logs')

    # Test dictionary that will be passed to the script.
    devices = {
        'device1': '192.168.0.1',
        'device2': '192.168.0.2'
    }

    # TODO - Add the functionality of this script to the PRTG-FastAPI
    #        project?
    # Run the script.
    prtg_device_ip_changer(devices)

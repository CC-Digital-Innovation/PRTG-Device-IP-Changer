# PRTG-Device-IP-Changer

## Summary
Given a CSV of device names and IP addresses, edit the devices' IP addresses to match the ones corresponding to the
devices listed in the CSV file.

_Note: If you have any questions or comments you can always use GitHub
discussions, or email me at farinaanthony96@gmail.com._

#### Why
In case there are errors or inconsistencies in the IP addresses of devices
in PRTG, this script will make editing those IP addresses much easier.

## Requirements
- Python >= 3.9.2
- configparser >= 5.0.2
- pandas >= 1.2.2
- pytz >= 2021.1
- requests >= 2.25.1

## Usage
- Add any additional filtering logic to the API URLs to get specific
  devices if desired.
    - _Make sure you configure filtering options accordingly. Available
      options for filtering can be found on the PRTG API:
      https://www.paessler.com/manuals/prtg/live_multiple_object_property_status#advanced_filtering_

- Add additional logic to fine tune exactly which devices should be edited in PRTG.

- Edit the config.ini file with relevant PRTG access information and the
  timezone for the log file naming.

- Simply run the script using Python:
  `python PRTG-Device-IP-Changer.py`

## Compatibility
Should be able to run on any machine with a Python interpreter. This script
was only tested on a Windows machine running Python 3.9.5.

## Disclaimer
The code provided in this project is an open source example and should not
be treated as an officially supported product. Use at your own risk. If you
encounter any problems, please log an
[issue](https://github.com/CC-Digital-Innovation/PRTG-Device-IP-Changer/issues).

## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request ツ

## History
-  version 1.0.2 - 2022/11/21
    - Added LICENSE file
    - Updated requirements.txt and README.md
    - Refactored code
    - Obfuscated config file


-  version 1.0.1 - 2021/06/08
    - Added support for multiple config files
    - Updated README.md


-  version 1.0.0 - 2021/05/19
    - Initial release

## Credits
Anthony Farina <<farinaanthony96@gmail.com>>

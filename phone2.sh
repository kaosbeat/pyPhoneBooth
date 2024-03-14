#!/bin/bash
/usr/bin/screen -s "/bin/bash" -dmS ddd-phone2
/usr/bin/screen  -S ddd-phone2 -X stuff "cd /home/pi/DataDrivenDreams/python/pyPhoneBooth\n"
/usr/bin/screen  -S ddd-phone2 -X stuff "pyenv activate ddd-phone\n"
/usr/bin/screen  -S ddd-phone2 -X stuff "python phone.py phone2 option1 option2\n"

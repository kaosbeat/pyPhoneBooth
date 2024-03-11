#!/bin/bash
/usr/bin/screen -s "/bin/bash" -dmS ddd-phone1 
/usr/bin/screen  -S ddd-phone1 -X stuff "cd /home/pi/DataDrivenDreams/python/pyPhoneBooth\n"
/usr/bin/screen  -S ddd-phone1 -X stuff "pyenv activate ddd-phone\n"
/usr/bin/screen  -S ddd-phone1 -X stuff "python phone.py phone1 option1 option2\n"

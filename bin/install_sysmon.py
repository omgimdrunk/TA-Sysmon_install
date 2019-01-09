#!/bin/env python
import os
import requests
from datetime import datetime

os.environ["hour"] =%time:~0,2%
os.environ["minute"]=%time:~3,2%
installPath = "C:\\ProgramData\\sysmon"
access_rights = 0o755
sysMonURL = "https://live.sysinternals.com/Sysmon64.exe"
sysMonConfigURL = "https://raw.githubusercontent.com/f8al/TA-Sysmon_install/master/etc/sysmonconfig-export.xml"
sysMonUpdaterURL = "https://raw.githubusercontent.com/f8al/TA-Sysmon_install/master/Auto_Update.bat"
time = datetime.now()
taskTime = time + datetime.timedelta(minutes = 2)
datetime.strptime(tasktime, '%H:%M')

try:  
    os.mkdir(installPath, access_rights)
except OSError:  
    print ("Creation of the directory %s failed" % path)
else:  
    print ("Successfully created the directory %s " % path)

os.chdir(installPath)


rsysmon=requests.get(sysMonURL, allow_redirects=True, show_warnings=False)
open (installPath+'sysmon64.exe', 'wb').write(rsysmon.content)
print ('[+] Downloading Sysmon...')

rsysmonconfig=requests.get(sysMonConfigURL, allow_redirects=True, show_warnings=False)
open (installPath+'\\sysmonconfig-export.xml', 'wb').write(rsysmonconfig.content)
print ('[+] Downloading Sysmon config...')

rsymonupdate=requests.get(sysMonUpdaterURL, allow_redirects=True, show_warnings=False)
open (installPath+'\\Auto_Update.bat', 'wb').write(rsysmonconfig.content)
print ('[+] Downloading Sysmon config...')

os.system(installPath + 'sysmon64.exe -accepteula -i sysmonconfig-export.xml')
os.system('sc failure Sysmon actions= restart/10000/restart/10000// reset= 120')
print('[+] Sysmon Successfully Installed!')
print('[+] Creating Auto Update Task set to Hourly..')
os.system('SchTasks /Create /RU SYSTEM /RL HIGHEST /SC HOURLY /TN Update_Sysmon_Rules /TR '+installPath+'Auto_Update.bat /F /ST ' + taskTime)
os.sleep(10)
exit()

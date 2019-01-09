#!/bin/env python
import os
import requests
import sys

from datetime import timedelta, datetime
import time
from subprocess import Popen, PIPE
from hashlib import sha256
'''

λ sha256sum.exe "Sysmon64.exe"

e39520fb0bb6b1ae408bf4b7b1471d32753ef8b31191d4efe4ca4ae14efc3726 *Sysmon64.exe



open (installPath+'\\', 'wb').write(rsysmon.content)
print ('[+] Downloading Sysmon...')

rsysmonconfig=requests.get(sysMonConfigURL, allow_redirects=True, show_warnings=False)
open (installPath+'\\', 'wb').write(rsysmonconfig.content)
print ('[+] Downloading Sysmon config...')

rsymonupdate=requests.get(sysMonUpdaterURL, allow_redirects=True, show_warnings=False)
open (installPath+'\\', 'wb').write(rsysmonconfig.content)
print ('[+] Downloading Sysmon config...')

'''



class SYSMON:
    url = "https://live.sysinternals.com/Sysmon64.exe"
    saveas = 'sysmon64.exe'
    shasum = 'e39520fb0bb6b1ae408bf4b7b1471d32753ef8b31191d4efe4ca4ae14efc3726'

class SYSMONCONFIG:
    url = "https://raw.githubusercontent.com/f8al/TA-Sysmon_install/master/etc/sysmonconfig-export.xml"
    saveas = 'sysmonconfig-export.xml'


class SYSMONUPDATER:
    url = "https://raw.githubusercontent.com/f8al/TA-Sysmon_install/master/Auto_Update.bat"
    saveas = 'Auto_Update.bat'


class SysmonHNDL:
    def __init__(self):

        self.install_root = 'C:'
        self.install_path = os.path.join(self.install_root, 'ProgramData', 'sysmon')
        self.access_rights = 0o755

        self._time = self._t_now()
        self._chk_path()

    def _chk_path(self):

        try:
            os.mkdir(self.install_path, self.access_rights)
        except Exception as E:
            pass

        return 0

    def _t_now(self):
        _t = datetime.now()
        _t = _t + timedelta(minutes=2)
        print(_t)
        #datetime.strptime(_t, '%H:%M')
        return _t

    @staticmethod
    def chk_hash(data, comp_hash):
        _hsh = sha256()
        _hsh.update(data)
        hsh = _hsh.hexdigest()
        if hsh == comp_hash:
            return [0]
        else:
            raise KeyError('Hash missmatch {}, {}'.format(hsh, comp_hash))

    @staticmethod
    def exec(*cmds):
        _sp = Popen(cmds, stdout=PIPE, stdin=PIPE, stderr=PIPE)

        while _sp.poll() is None:
            time.sleep(.5)
        stat, err = _sp.communicate()
        if err:
            raise Exception(err)
        else:
            return stat

    def _mod_file(self, _fname, _fdata):
        with open (os.path.join(self.install_path, _fname), 'wb') as sysmon:
            try:
                sysmon.write(_fdata.content)
            except Exception as E:
                sys.stdout.write(str(E))
                raise E
            else:
                sys.stdout.write('[+] Downloading {}\n'.format(_fname))

    def pull_url(self, sys_obj):
        rsysmon = requests.get(sys_obj.url, allow_redirects=True)

        try:
            shasum = sys_obj.shasum
        except:
            pass
        else:
            hshchk =  self.chk_hash(rsysmon.content, shasum)
            if hshchk[0] != 0:
                sys.stdout.write(str(hshchk))
                sys.stdout.flush()
                sys.exit()

        try:
            self._mod_file(os.path.join(self.install_path, sys_obj.saveas), rsysmon)
        except Exception as E:
            raise E
        else:
            return 0







my_sysmon = SysmonHNDL()

for runit in [SYSMON, SYSMONCONFIG, SYSMONUPDATER]:

    try:
        my_sysmon.pull_url(runit)
    except Exception as E:
        print(E)
    else:
        sys.stdout.write('Completed {}\n'.format(runit.saveas))


stat = my_sysmon.exec([os.path.join(my_sysmon.install_path, 'sysmon64.exe'), '-accepteula', '-i', 'sysmonconfig-export.xml'])
if type(stat) == Exception:
    sys.stdout.write('FAIL')
    sys.exit()
else:

# os.system('sc failure Sysmon actions= restart/10000/restart/10000// reset= 120')
# print('[+] Sysmon Successfully Installed!')
# print('[+] Creating Auto Update Task set to Hourly..')
# os.system('SchTasks /Create /RU SYSTEM /RL HIGHEST /SC HOURLY /TN Update_Sysmon_Rules /TR '+installPath+'Auto_Update.bat /F /ST ' + taskTime)

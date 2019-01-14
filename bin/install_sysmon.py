#!/bin/env python
import os
import requests
import sys

from datetime import timedelta, datetime
import time
from subprocess import Popen, PIPE
from hashlib import sha256


class SYSMON:
    url = "https://live.sysinternals.com/Sysmon64.exe"
    saveas = 'sysmon64.exe'
    saveto = os.path.join('C:\\', 'ProgramData', 'sysmon')
    shasum = 'e39520fb0bb6b1ae408bf4b7b1471d32753ef8b31191d4efe4ca4ae14efc3726'
    CMD = [
        "{FILE} -accepteula -i sysmonconfig-export.xml",
        "sc failure Sysmon actions= restart/10000/restart/10000// reset= 120"
        ]


class SYSMONCONFIG:
    url = "https://raw.githubusercontent.com/f8al/TA-Sysmon_install/master/etc/sysmonconfig-export.xml"
    saveas = 'sysmonconfig-export.xml'
    saveto = os.path.join('C:\\', 'ProgramData', 'sysmon')
    print(saveto)

class SYSMONUPDATER:
    url = "https://raw.githubusercontent.com/f8al/TA-Sysmon_install/master/Auto_Update.bat"
    saveas = 'Auto_Update.bat'
    saveto = os.path.join('C:\\', 'ProgramData', 'sysmon')
    CMD = [
        "SchTasks /Create /RU SYSTEM /RL HIGHEST /SC HOURLY" +
        "/TN Update_Sysmon_Rules /TR \"{FILE}\" /F /ST {TIME}"
        ]


class SysmonHNDL:
    def __init__(self):
        self.access_rights = 0o755

    def _chk_path(self, _path):
        print('making {}'.format(_path))
        try:
            os.mkdir(_path. self.access_rights)
        except:
            pass

    @staticmethod
    def chk_hash(data, comp_hash):
        _hsh = sha256()
        _hsh.update(data)
        hsh = _hsh.hexdigest()
        if hsh == comp_hash:
            return [0]
        else:
            raise KeyError('Hash missmatch {}, {}'.format(hsh, comp_hash))

    def _mod_file(self, _fname, _fpath, _fdata):
            self._chk_path(_fpath)

            if not os.path.exists(_fpath):
                raise NotADirectoryError(_fpath)

            with open (os.path.join(_fpath, _fname), 'wb') as sysmon:
                print(os.path.join(_fpath, _fname))
                try:
                    sysmon.write(_fdata.content)
                except Exception as E:
                    sys.stdout.write(str(E))
                    raise E
                else:
                    sys.stdout.write('[+] Downloading {}\n'.format(_fname))
                    return

    def pull_url(self, sys_obj):
        rsysmon = requests.get(sys_obj.url, allow_redirects=True)

        try:
            shasum = sys_obj.shasum
        except:
            pass
        else:
            hshchk = self.chk_hash(rsysmon.content, shasum)
            if hshchk[0] != 0:
                sys.stdout.write(str(hshchk))
                sys.stdout.flush()
                sys.exit()

        try:
            self._mod_file(sys_obj.saveas, sys_obj.saveto, rsysmon)
        except Exception as E:
            raise E
        else:
            return 0




class SchTasksHNDL:
    def __init__(self,  sysobj, add_seconds: int=0):

        self.add_time = add_seconds
        self.sysobj = sysobj
        self.task_time = self._t_now()

        self.tags = {
                    '{TIME}' : { 'TIME' : self.task_time },
                    '{FILE}' : { 'FILE' : os.path.join(self.sysobj.saveto, self.sysobj.saveas) }
                    }

    def _t_now(self):
        _t = datetime.now()
        _later = _t + timedelta(seconds=self.add_time)
        return _later.strftime('%H:%M')

    def _parse_cmd(self):
        try:
            for cmd in self.sysobj.CMD:
                _mods = dict()
                for key in self.tags.keys():
                    if key in cmd:
                        _mods.update(self.tags[key])

                yield cmd.format(**_mods)
        except:
            raise

    def exec(self):

        for cmd in self._parse_cmd():
            _call = cmd.split(' ')
            print(_call)
            _sp = Popen(_call, stdout=PIPE, stdin=PIPE, stderr=PIPE)

            while _sp.poll() is None:
                time.sleep(.5)
            stat, err = _sp.communicate()
            if err:
                sys.stderr.write(str(err))
                raise Exception(err)
            else:
                return stat


if __name__ == "__main__":

    sysmon_wget = SysmonHNDL()

    for runit in [SYSMON, SYSMONCONFIG, SYSMONUPDATER]:
        try:
            sysmon_wget.pull_url(runit)
        except Exception as E:
            sys.stderr.write(str(E))
            raise E
        else:
            sys.stdout.write('Completed {}\n'.format(runit.saveas))


    exec_sysmon = SchTasksHNDL(SYSMON)
    try:
        exec_sysmon.exec()
    except Exception as E:
        sys.stderr.write(str(E))
        raise E

    exec_sysmonupdate = SchTasksHNDL(SYSMONUPDATER, add_seconds=120)
    try:
        exec_sysmonupdate.exec()
    except Exception as E:
        sys.stderr.write(str(E))
        raise E



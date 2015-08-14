#!/usr/bin/env python
#encoding: utf-8

import os
import logging
import subprocess

_logger = logging.getLogger('root.utils.cmdutils')

def exec_cmd(args, async=False, cwd=None):
   return _async_exec_cmd(args, cwd) if async else _sync_exec_cmd(args, cwd)


def _async_exec_cmd(args, cwd=None):
    _cmd = []

    if cwd is not None:
        _cmd.append('cd /D "%s"' % cwd) if os.name == 'nt' else _cmd.append('cd "%s"' % cwd)
        _cmd.append('&&')

    (os.name == 'nt') and _cmd.append('start')
    

    _cmd += args if isinstance(args, list) else [args]
   
    (os.name == 'nt') or _cmd.append('&')
    
    _returncode = os.system(' '.join(_cmd))

    _returncode = 0
    _output = ''
    _pid = -1

    _logger.debug('async exec cmd: %s, returncode, %d, output:%s, pid:%d', _cmd, _returncode, _output, _pid)
    return [_returncode, _output, _pid]


def _sync_exec_cmd(args, cwd=None):
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    _process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
    _stdout, _stderr = _process.communicate()
    _returncode = _process.returncode
    _pid = _process.pid
    _output = ''
    try:
        _output = str(_stdout)
    except BaseException:
        pass
    _logger.debug('sync exec cmd: %s, returncode, %d, output:%s, pid:%d', args, _returncode, _output, _pid)
    return [_returncode, _output, _pid]

def process_id_exists(pid):
    _args = 'tasklist /FI "PID eq %d"' % pid if os.name == 'nt' else "ps -aux | awk '{print $2}' | grep -e %d" % pid
    _code, _output, _pid = exec_cmd(_args)
    return _output.find(str(pid)) != -1

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)s %(levelname)s:%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
#     print exec_cmd(['python', 'test.py'], True, cwd=r"d:\\")
#     print exec_cmd(['ping ', 'www.360.cn', '-n 100'], True)
#     print exec_cmd(['ping ', 'www.360.cn'])
    print process_exists(2152)
    
#!/usr/bin/env python
#encoding: utf-8

import os
import logging
import traceback
import time
import datetime
import threading
import copy
import re

try:
    import gconf
except BaseException:
    import sys
    sys.path.insert(0, '..')
    import gconf

from cmdutils import exec_cmd
from fmonitor import folder_monitor
from fileutils import get_all_files

INTERVAL_CALLBACK = 60

_logger = logging.getLogger('root.utils.crontab')

_lock = threading.Lock()
_script_path_dir = os.path.join(gconf.PROCESS_PATH, 'scripts')

_commands = []

def _execute_cmd(cmd, cwd):
    return exec_cmd(cmd, True, cwd=cwd)[0]

def _validate_time_sequence(time_sequence):
    for _seq in time_sequence:
        if re.match("^([*]|[\d]{1,2}([,-][\d]{1,2})*|[*][/][\d]{1,2})$", _seq) is None:
            return False
    return True

def _read_configs():
    global _commands

    _cmds = []
    _paths = get_all_files(_script_path_dir, filter=lambda x:os.path.basename(x)=='crontab')

    for _path in _paths:
        _cwd = os.path.dirname(_path)
        with open(_path, 'rb') as _handler:
            for _line in _handler:
                _line = _line.strip()
                if _line == '' or _line.startswith('#'):
                    continue
                
                _sp = _line.split()
                
                if len(_sp) < 6:
                    _logger.error('crontab file config error, path:%s, line:%s', _path, _line)
                    continue
                
                if not _validate_time_sequence(_sp[:5]):
                    _logger.error('crontab file config error, path:%s, line:%s', _path, _line)
                    continue

                _cmds.append({'time_sequence': _sp[:5], 'cmd': _sp[5:], 'cwd': _cwd})
    
    if _lock.acquire():
        try:
            _commands = _cmds
        finally:
            _lock.release()

    return _cmds


def _judge_time(current_time_sequence, time_sequence):
    for _i in xrange(5):
        if time_sequence[_i] == '*':
            continue
        elif str(time_sequence[_i]).startswith('*/'):
            if int(current_time_sequence[_i]) % int(str(time_sequence[_i])[2:]) != 0:
                return False
        else:
            _nodes = str(time_sequence[_i]).split(',')
            _rt = False
            for _node in _nodes:
                if _node.find('-') != -1:
                    _min, _max = _node.split('-')[:2]
                    if int(current_time_sequence[_i]) >= int(_min) and int(current_time_sequence[_i]) <= int(_max):
                        _rt = True
                        break
                else:
                    if int(_node) == int(current_time_sequence[_i]):
                        _rt = True
                        break
            if not _rt:
                return False
            
    return True


def _judge_execute_commands(current_time, commands):
    _current_datetime = datetime.datetime.fromtimestamp(current_time)
    _current_time_sequence = [_current_datetime.minute, _current_datetime.hour, _current_datetime.day, _current_datetime.month, (_current_datetime.weekday()) + 1 % 7]
    for _command in commands:
        _time_sequence = _command.get('time_sequence')
        if _judge_time(_current_time_sequence, _time_sequence):
            _cmd = _command.get('cmd')
            _cwd = _command.get('cwd')
            _code = _execute_cmd(_cmd, _cwd)
            _logger.debug('execute cmd: %s at dir:%s, result:%s', _cmd, _cwd, _code)


def run():
    _logger.debug('judge exec commands')

    _execute_commands = []
    if _lock.acquire():
        try:
            _execute_commands = copy.deepcopy(_commands)
        finally:
            _lock.release()
    
    _judge_execute_commands(time.time(), _execute_commands)
        

folder_monitor(_script_path_dir, _read_configs, sleeptime=5, content=True, filter=lambda x:os.path.basename(x)=='crontab')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s %(levelname)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        )
    from runserver import Callback, run_as_server
    run_as_server(Callback(callback=run, interval=INTERVAL_CALLBACK))

#!/usr/bin/env python
#encoding: utf-8
import os
import sys
import time
import logging

import gconf

from utils.fileutils import read_file, write_file
from utils.cmdutils import process_id_exists
from utils.crontab import run, INTERVAL_CALLBACK
from utils.runserver import Callback, run_as_server
from utils.logwatcher import LogWatcher
    
LogWatcher(os.path.join(gconf.PROCESS_PATH, 'logging.cfg')).start()
_logger = logging.getLogger('root')

_pid_path = os.path.join(gconf.PROCESS_PATH, 'pid')

def write_pid():
    _pid = os.getpid()
    _history_pid = read_file(_pid_path)
    if _history_pid and process_id_exists(int(_history_pid)):
        _logger.info('Another crontab process is running, the process is going to die')
        sys.exit(-1)
    
    write_file(_pid_path, _pid)
    return _pid

def run_server():
    _logger.info('process crontab is running, process id:%s', write_pid())
    run_as_server(Callback(callback=run, interval=INTERVAL_CALLBACK))

if __name__ == '__main__':
    run_server()
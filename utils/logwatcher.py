#!/usr/bin/env python
# encoding:utf-8

import os
import threading
import logging
import logging.config
import traceback
import time

root_logger = logging.getLogger()

class LogWatcher(threading.Thread):

    def __init__(self, config):
        super(LogWatcher, self).__init__()
        self.setDaemon(True)
        self._config = config
        self._modify_time = 0
        self._check()
    
    def run(self):
        while 1:
            self._check()
            time.sleep(2)
    
    def _check(self):
        _mtime = int(os.path.getmtime(self._config))
        if _mtime > self._modify_time:
            try:
                self._modify_time = _mtime
                logging.config.fileConfig(self._config)
            except BaseException, e:
                root_logger.exception('error:%s', str(e))
                root_logger.exception(traceback.format_exc())



if __name__ == '__main__':
    LogWatcher('logging.cfg').start()
    logger = logging.getLogger('root')

    idx = 0
    while 1:
        logger.error('%s:error' % idx)
        logger.info('%s:info' % idx)
        logger.debug('%s:debug' % idx)
        idx += 1
        time.sleep(1)

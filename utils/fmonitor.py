#!/usr/bin/env python
#encoding: utf-8

import os
import threading
import logging
import time

from crypt import file_md5
from fileutils import get_all_files

_logger = logging.getLogger('root.utils.fmonitor')

def file_monitor(path, callback, sleeptime=10, content=True, *args, **kwargs):
    _key = {'key': 0}

    def _check():
        _current_key = 0
        if os.path.exists(path):
            _current_key = file_md5(path) if content else int(os.path.getmtime(path))
                
        if _key['key'] != _current_key:
            _logger.debug('file is change, path: %s', path)
            _key['key'] = _current_key
            callback(*args, **kwargs)

    def _run():
        while 1:
            _check()   
            time.sleep(sleeptime)
    
    _check()

    th = threading.Thread(target=_run)
    th.setName('file_monitor_%s' % os.path.basename(path))
    th.setDaemon(True)
    th.start()

def folder_monitor(path, callback, sleeptime=20, content=True, filter=None, *args, **kwargs):
    _file_list = {}

    def _check():
        _has_changed = False
        _files = get_all_files(path, filter)
        _delete_files = []
        
        for _file in _files:
            _key = _file_list.get(_file, 0)
            _current_key = file_md5(_file) if content else int(os.path.getmtime(_file))
            if _key != _current_key:
                _file_list[_file] = _current_key
                _has_changed = True
            
            
        for _file in _file_list:
            if _file not in _files:
                _has_changed = True 
                _delete_files.append(_file)
                
        for _file in _delete_files:
            del _file_list[_file]
        
        if _has_changed:
            _logger.debug(_file_list)
            callback(*args, **kwargs)
    
    def _run():
        while 1:
            _check()
            time.sleep(sleeptime)
    
    _check()

    th = threading.Thread(target=_run)
    th.setName('folder_monitor_%s' % os.path.basename(path))
    th.setDaemon(True)
    th.start()


if __name__ == '__main__':
    import time
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(name)s %(levelname)s:%(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')
        
    def callback(*args, **kwargs):
        print args[0]

    file_monitor("d:/file.txt", callback, 5, False, 'file changed')
    folder_monitor("d:/folder", callback, 20, False, lambda path:path.endswith('.monitor'), 'folder changed')
    while 1:
        time.sleep(5)
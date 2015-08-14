#!/usr/bin/env python
#encoding: utf-8

import os
import hashlib

def md5(s):
    _md5 = hashlib.md5()
    _md5.update(str(s))
    return _md5.hexdigest()

def file_md5(path):
    _md5 = hashlib.md5()
    if os.path.exists(path):
        _handler = None
        try:
            _handler = open(path, 'rb')
            while 1:
                _cxt = _handler.read(1024)
                if not _cxt:
                    break
                _md5.update(str(_cxt))
        except BaseException:
            pass
        finally:
            if _handler is not None:
                _handler.close()
                    
    return _md5.hexdigest()

if __name__ == '__main__':
    print md5('a')
    print md5({'a':1})
    print md5([1, 2])
    print md5([1, '2'])
    print md5_file("e:/t.txt")


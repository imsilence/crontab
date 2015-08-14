#!/usr/bin/env python
#encoding: utf-8

import os
import shutil

def write_file(path, cxt, retry=3):
    _handler = None
    
    for _i in xrange(retry):
        try:
            _handler = open(path, 'wb')
            _handler.write(str(cxt))
            break
        except BaseException, e:
            print e
            pass
        
    if _handler is not None:
        _handler.close()

def read_file(path):
    _handler = None
    _cxt = ''
    try:
        if os.path.exists(path):
            _handler = open(path, 'rb')
            _cxt = _handler.read()
    except BaseException, e:
        print e
        pass
    finally:
        if _handler is not None:
            _handler.close()
        return _cxt
    
def delete_file(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.unlink(path)
            

def get_all_files(path, filter=None):
    _list = []
    if os.path.exists(path):
        if os.path.isdir(path):
            try:
                for _filename in os.listdir(path):
                    if _filename in ['.', '..']:
                        continue
                    _cpath = os.path.join(path, _filename)
                    _list += get_all_files(_cpath, filter)
            except BaseException:
                pass
        else:
            if filter is None or filter(path):
                _list.append(os.path.normpath(path))
                
    return _list
    
if __name__ == '__main__':
    write_file('f:/t.txt', 'silence')
    write_file('e:/t.txt', 'silence')
    print read_file('e:/t.txt')
    print read_file('e:/t.txt')
    delete_file('e:/tttt')
    delete_file('e:/t.txt')
    print get_all_files("E:\\code\\tests", lambda path: path.endswith('.project'))

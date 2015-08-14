#!/usr/bin/env python
#encoding: utf-8

if __name__ == '__main__':
    import time, os
    with open('t.txt', 'ab') as h:
        h.write('%s%s' % (str(time.time()), os.linesep))

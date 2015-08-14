#!/usr/bin/env ptyhon
#encoding: utf-8
import logging
import traceback
import threading
import time

_logger = logging.getLogger('root.utils.runserver')

_RUNNING = True

NIL = lambda *args, **kwargs: None

class SelfException(Exception):
    pass

class Callback(object):
    
    def __init__(self, **kwargs):
        self.init = kwargs.get('init', NIL)
        self.callback = kwargs.get('callback', NIL)
        self.dispose = kwargs.get('dispose', NIL)
        self.interval = float(kwargs.get('interval', 1))
        self.timesleep = float(kwargs.get('timesleep', 0.5))
    

class DaemonThread(threading.Thread):
    
    def __init__(self, callback, interval=1, timesleep=0.5):
        super(DaemonThread, self).__init__()
        self.setName('thread_daemon')
        self.setDaemon(True)
        self._callback = callback
        self._interval = interval
        self._timesleep = timesleep
        
    def run(self):
        _callback = self._callback
        _interval = self._interval
        _next_time = 0
        while 1:
            try:
                _current_time = time.time()
                if _current_time > _next_time:
                    _next_time = _current_time + _interval
                    _callback()
            except BaseException:
                _logger.exception(traceback.format_exc())
            finally:
                time.sleep(self._timesleep)

def run_as_server(callbacks, timesleep=0.5):
    if not isinstance(callbacks, list):
        callbacks = [callbacks]
        
    _disponse_funcs = []
    try:
        for _callback in callbacks:
            if not isinstance(_callback, Callback):
                raise SelfException('Parameters must be inherited from type object Callback')
        
            _init_func = getattr(_callback, 'init')
            _callback_func = getattr(_callback, 'callback')
            _dispose_func = getattr(_callback, 'dispose')
            _interval = getattr(_callback, 'interval')
            _timesleep = getattr(_callback, 'timesleep')
            
            _init_func()
            DaemonThread(_callback_func, _interval, _timesleep).start()
            
            _disponse_funcs.append(_dispose_func)
            
        while _RUNNING:
            time.sleep(1)
    except BaseException:
        _logger.exception(traceback.format_exc())
    finally:
        for _dispose_func in _disponse_funcs:
            _dispose_func()
            
def stop_server():
    global _RUNNING
    _RUNNING = False

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)s %(levelname)s:%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
    def callback1():
        print 'callback1:', time.time()
        
    def callback2():
        pass
        
    def stop():
        time.sleep(1000)
        stop_server()
        
    threading.Thread(target=stop).start()
    run_as_server([Callback(callback=callback1, interval=5),Callback(callback=callback2)])

import collections
import inspect
import time
import weakref

_EVENTS = {}

_QUEUE = collections.deque()

ANY, QUIT, TICK = range(3)

_EVENTS[ANY] = weakref.WeakSet()


def register(event, func):
    if not callable(func):
        # XXX could raise an exception
        return
    if event not in _EVENTS:
        _EVENTS[event] = weakref.WeakSet()
    _EVENTS[event].add(func)


def unregister(event, func=None):
    if event not in _EVENTS:
        # XXX may raise an exception
        return
    if func is None and event is not ANY:
        del _EVENTS[event]
        return
    if func in _EVENTS[event]:
        _EVENTS[event].remove(func)
    if not len(_EVENTS[event]) and event is not ANY:
        del _EVENTS[event]


def post(event, **kargs):
    if event not in _EVENTS:
        return
    _QUEUE.append((event, kargs)) 


def _consume_event_queue():
    stop = False
    while _QUEUE:
        event, ekargs = _QUEUE.popleft()
        handlers = _EVENTS[event] | _EVENTS[ANY]
        for handler in handlers:
            hargs, _, hkeywords, _ = inspect.getargspec(handler)
            kargs = dict(ekargs)
            # Add a special attribute with the type of the event
            kargs['__event__'] = event
            if not hkeywords:
                for key in kargs:
                    if key not in hargs:
                        del kargs[key]
            handler(**kargs)
        if event == QUIT:
            stop = True 
            break
    return stop


def run():
    ''' Sample main loop of yaranullin '''
    stop = False
    while not stop:
        time.sleep(0.01)
        post(TICK)
        stop = _consume_event_queue()

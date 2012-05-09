import collections
import inspect
import time

EVENTS = {}

QUEUE = collections.deque()

ANY, QUIT = range(1)

EVENTS[ANY] = set()


def register(event, func):
    if not callable(func):
        # XXX could raise an exception
        return
    if event not in EVENTS:
        EVENTS[event] = set()
    EVENTS[event].add(func)


def unregister(event, func=None):
    if event not in EVENTS:
        # XXX may raise an exception
        return
    if func is None and event is not ANY:
        del EVENTS[event]
        return
    if func in EVENTS[event]:
        EVENTS[event].remove(func)


def post(event, **kargs):
    if event not in EVENTS:
        return
    QUEUE.append((event, kargs)) 


def _consume_event_queue():
    stop = False
    while QUEUE:
        event, ekargs = QUEUE.popleft()
        if event == QUIT:
            stop = True 
        handlers = EVENTS[event] | EVENTS[ANY]
        for handler in handlers:
            hargs, _, hkeywords, _ = inspect.getargspec(handler)
            kargs = dict(ekargs)
            if not hkeywords:
                for key in kargs:
                    if key not in hargs:
                        del kargs[key]
            handler(**kargs)
    return stop


def run():
    ''' Sample main loop of yaranullin '''
    stop = False
    while not stop:
        time.sleep(0.01)
        stop = _consume_event_queue()

import collections
import inspect
import time
import weakref


_EVENTS = {}

_QUEUE = collections.deque()

ANY, QUIT, TICK = range(3)

_EVENTS[ANY] = weakref.WeakValueDictionary()


def register(event, func):
    if inspect.isfunction(func):
        func = {func: func}
    elif inspect.ismethod(func):
        func = {func.im_func: func.im_self}
    else:
        return
    if event not in _EVENTS:
        _EVENTS[event] = weakref.WeakValueDictionary()
    _EVENTS[event].update(func)


def unregister(event, func=None):
    if event not in _EVENTS:
        # XXX may raise an exception
        return
    if func is None and event is not ANY:
        del _EVENTS[event]
        return
    if inspect.ismethod(func):
        del _EVENTS[event][func.im_func]
    else:
        del _EVENTS[event][func]
    if not _EVENTS[event] and event is not ANY:
        del _EVENTS[event]


def post(event, **kargs):
    if event not in _EVENTS:
        return
    _QUEUE.append((event, kargs)) 


def _consume_event_queue():
    stop = False
    while _QUEUE:
        event, ekargs = _QUEUE.popleft()
        handlers = {}
        handlers.update(_EVENTS[event])
        handlers.update(_EVENTS[ANY])
        for handler, instance in handlers.iteritems():
            hargs, _, hkeywords, _ = inspect.getargspec(handler)
            kargs = dict(ekargs)
            # Add a special attribute with the type of the event
            kargs['__event__'] = event
            kargs['self'] = instance
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


class Pipe(object):

    ''' Used for communication between two processes.
    
    To allow sending and receiving events from two different processes,
    create an instance of Pipe for each one of them. The in_queue of the
    first Pipe must be the out_queue of the second and viceversa.

    The default implementation allows all events through the queues.
    
    '''

    def __init__(self, in_queue, out_queue):
        self.in_queue = in_queue
        self.out_queue = out_queue
        register(ANY, self.handle)

    def handle(self, **kargs):
        if kargs['__event__'] == TICK:
            return
        self.out_queue.put(kargs)

    def tick(self):
        while not self.in_queue.empty():
            event = self.in_queue.get()
            post(**event)

import inspect
import time
import multiprocessing

EVENTS = {}

OUT_QUEUE = multiprocessing.Queue()
IN_QUEUE = OUT_QUEUE

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
    OUT_QUEUE.put((event, kargs)) 


def _consume_event_queue():
    stop = False
    while True:
        if IN_QUEUE.empty():
            break
        event, ekargs = IN_QUEUE.get()
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


class SubEventManager(multiprocessing.Process):

    sleep_time = 0.01

    def __init__(self, in_queue, out_queue):
        multiprocessing.Process.__init__(self)
        global IN_QUEUE, OUT_QUEUE
        IN_QUEUE = in_queue
        OUT_QUEUE = out_queue

    def _prerun(self):
        ''' Called just before entering the main loop '''

    def _postrun(self):
        ''' Called just after leaving the main loop '''

    def run(self):
        self._prerun()
        stop = False
        while not stop:
            time.sleep(self.sleep_time)
            stop = _consume_event_queue()
        self._postrun()


class EventManager(object):

    sleep_time = 0.01
    subs = set()

    def _flush_out_queues(self):
        for event in IN_QUEUE:
            for _, _, out_queue in self.subs:
                out_queue.put(event)

    def _flush_in_queues(self):
        for _, in_queue, _ in self.subs:
            if not in_queue.empty():
                event = in_queue.get()
                IN_QUEUE.put(event)

    def run(self):
        stop = False
        while not stop:
            time.sleep(self.sleep_time)
            self._flush_out_queues()
            stop = _consume_event_queue()
            self._flush_in_queues()

    def add_process(self, sub_class):
        in_q = multiprocessing.Queue()
        out_q = multiprocessing.Queue()
        # The queues are swapped from the parent point of view
        sub = sub_class(out_q, in_q)
        self.subs.add((sub, in_q, out_q))

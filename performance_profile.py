import time

global_start_at = time.time()

_tm_stack = []


def get_global_epoch_time():
    return time.time() - global_start_at


def get_time_header():
    global_epoch = get_global_epoch_time()
    return f'[TIME:T+{global_epoch:04.3f}s]'


class TimeMeasureSession:
    def __init__(self, mult, is_avg):
        self._start_at = None
        self._stop_at = None
        self._average_list = []
        self._counter = 0
        self.multiplier = mult
        self.is_avg = is_avg

    def start(self):
        self._stop_at = None
        self._start_at = time.time()

    def stop(self):
        self._stop_at = time.time()
        time_taken_secs = self._stop_at - self._start_at
        self._average_list.append(time_taken_secs * self.multiplier)
        self._average_list = self._average_list[:100]
        self._counter += 1

    def print_time(self, message):
        time_taken_secs = 0
        if len(self._average_list) > 0:
            time_taken_secs = self._average_list[-1]
        this_start_at_globally = self._start_at - global_start_at
        this_stop_at_globally = self._stop_at - global_start_at
        print(get_time_header() + f'[{this_start_at_globally :#.3f}-{this_stop_at_globally:#.3f}s:{time_taken_secs:#.5f}s]{message}', flush=True)

    def print_avg(self, message):
        print(get_time_header() + f'[avg:{self.average * 1000.0:08.3f}ms]{message}', flush=True)

    def reset(self):
        self._average_list = []

    @property
    def average(self):
        len_average = len(self._average_list)
        if len_average == 0:
            return 0
        return sum(self._average_list) / len_average

    @property
    def counter(self):
        return self._counter


def time_measure(message, stack=True, avg=True):
    def f(g):
        def wrapper(*args, **kwargs):
            with TimeMeasure(message, stack=stack, avg=avg):
                return g(*args, **kwargs)

        return wrapper

    return f


class TimeMeasure:
    enabled = True
    sessions = dict()
    force_print = False

    def __init__(self, message: str = '', stack=False, avg=True, mult=1.0):
        self._message = message
        self._stack = stack
        self._is_avg = avg
        self._mult = mult

    def __enter__(self):
        self.session.start()
        if self._stack:
            _tm_stack.append(self._message)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if self._stack:
            _tm_stack.pop()
        self.session.stop()

        session = self.session
        if not self.enabled:
            return
        if not self._is_avg or self.force_print:
            session.print_time(self.message)

    @property
    def session(self):
        key = self.message
        if key not in self.sessions:
            self.sessions[key] = TimeMeasureSession(self._mult, self._is_avg)
        return self.sessions[key]

    @property
    def message(self):
        message = '->'.join(_tm_stack + [self._message])
        return message

    def print_avg(self):
        self.sessions[self.message].print_avg()

    @classmethod
    def reset_all_avg(cls):
        for mes, v in cls.sessions.items():
            if v.is_avg:
                v.reset()

    @classmethod
    def print_all_avg(cls):
        avg_sum = 0
        for mes, v in cls.sessions.items():
            if v.is_avg:
                v.print_avg(mes)
                avg_sum += v.average


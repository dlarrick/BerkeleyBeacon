import time
from threading import Thread, Event

from bridge import BRIDGE
from conf import BEACON, Color, COLORVALS

def turn_on_with_color(color, beacon=BEACON):
    xy = COLORVALS.get(color, [0,0])
    BRIDGE.lights(beacon, 'state', bri=255, sat=255, on=True,
                  xy=xy)

def turn_off(beacon=BEACON):
    BRIDGE.lights(beacon, 'state', on=False)


# StoppableThread is from user Dolphin,
# from http://stackoverflow.com/questions/5849484/how-to-exit-a-multithreaded-program
class StoppableThread(Thread):

    def __init__(self, beacon):
        Thread.__init__(self)
        self.stop_event = Event()
        self._beacon = beacon

    def stop(self, do_turn_off=False):
        if do_turn_off:
            turn_off(self._beacon)
        if self.is_alive():
            # set event to signal thread to terminate
            self.stop_event.set()
            # block calling thread until thread really has terminated
            self.join()

class IntervalTimer(StoppableThread):

    def __init__(self, interval, worker_func, beacon):
        StoppableThread.__init__(self, beacon)
        self._interval = interval
        self._worker_func = worker_func

    def run(self):
        while not self.stop_event.is_set():
            self._worker_func(self)
            time.sleep(self._interval)

class ColorSequencer(IntervalTimer):

    def __init__(self, interval, init_sequence=None, debug=False, beacon=BEACON):
        self._interval = interval
        IntervalTimer.__init__(
            self, self._interval, ColorSequencer.sequencer, beacon)
        self._sequence = init_sequence
        self._counter = 0
        self._last_color = None
        self._debug = debug
        light = BRIDGE.lights[self._beacon]()
        if debug:
            print(f"At start: {light}")

    def sequencer(self):
        if not self._sequence:
            if self._debug:
                print("No sequence")
            return
        color = self._sequence[self._counter]
        if self._debug:
            print(f"Current color: {color}")
        if color == self._last_color:
            if self._debug:
                print("Color has not changed")
            return
        if color == Color.BLACK:
            if self._debug:
                print("Turn off (black)")
            turn_off(beacon=self._beacon)
        else:
            if self._debug:
                print(f"Turn on, {color}")
            turn_on_with_color(color, beacon=self._beacon)
        self._last_color = color
        self._counter += 1
        if self._counter >= len(self._sequence):
            self._counter = 0

    def set_sequence(self, sequence):
        running = self.is_alive()
        if running:
            print("Error: can't set sequence after running")
        self._counter = 0
        self._sequence = sequence
        self._last_color = None

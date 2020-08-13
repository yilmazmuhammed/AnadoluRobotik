from queue import Queue
from threading import Thread
from time import sleep


class Motor:
    def __init__(self, pin):
        self.throttle = 0
        self.pin = pin
        self.queue = Queue()
        self.thread = Thread(target=self.motor_thread, args=(self.queue,))
        self.thread.start()

    def motor_thread(self, queue):
        prev_power = 0
        throttle = 0
        slp = 0.00
        pin = self.pin
        while True:
            throttle = queue.get()
            if prev_power == throttle:
                continue
            elif prev_power < throttle:
                for i in range(prev_power + 1, throttle + 1):
                    print("Thread %s:" % pin, i / 100)
                    sleep(slp)
            else:
                for i in range(prev_power - 1, throttle - 1, -1):
                    print("Thread %s:" % pin, i / 100)
                    sleep(slp)
            prev_power = throttle


class Rov:
    def __init__(self):
        self.l = []
        for i in range(4):
            self.l.append(Motor(i))

    def change_throttle(self, t):
        for m in self.l:
            m.queue.put(t)
            # m.throttle = t


if __name__ == '__main__':
    r = Rov()
    for i in range(1000):
        r.change_throttle(i)
        # sleep(0.01)

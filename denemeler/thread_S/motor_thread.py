from datetime import datetime
from queue import Queue
from threading import Thread, Lock
from time import sleep

class Motor:
    def __init__(self, pin):
        self.throttle = 0
        self.pin = pin
        self.queue = Queue()
        self.lock = Lock()
        self.running = True
        self.thread = Thread(target=self.motor_thread, args=(self.queue,))
        self.thread.start()

    def motor_thread(self, queue):
        prev_power = 0
        throttle = 0
        slp = 0.00
        pin = self.pin
        while self.running:
            # sleep(0.01)
            # throttle = queue.get()
            # with self.lock:
            self.lock.acquire()
            throttle = self.throttle
            if prev_power == throttle:
                continue
            elif prev_power < throttle:
                for i in range(prev_power + 1, throttle + 1):
                    # print("Thread %s:" % pin, i / 100)
                    sleep(slp)
            else:
                for i in range(prev_power - 1, throttle - 1, -1):
                    # print("Thread %s:" % pin, i / 100)
                    sleep(slp)
            prev_power = throttle


class Rov:
    def __init__(self):
        self.l = []
        for i in range(8):
            self.l.append(Motor(i))

    def change_throttle(self, t):
        for m in self.l:
            print("\t\t", datetime.now())
            # m.queue.put(t)
            m.throttle = t
            m.lock.release()


if __name__ == '__main__':
    r = Rov()
    for i in range(100):
        print(datetime.now())
        r.change_throttle(i)
        sleep(0.01)

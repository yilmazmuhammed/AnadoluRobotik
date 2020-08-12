#!/usr/bin/python

import threading
import time

exitFlag = 0


class myThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + self.name)
        print_time(self.name, 0, self.counter)
        print("Exiting " + self.name)


def print_time(threadName, delay, counter):
    while counter:
        if exitFlag:
            threadName.exit()
        time.sleep(delay)
        print("%s: %s" % (threadName, time.ctime(time.time())))
        counter -= 1


if __name__ == '__main__':
    # Create new threads
    thread1 = myThread(1, "Thread-1", 100)
    thread2 = myThread(2, "Thread-2", 100)

    # Start new Threads
    thread2.start()
    thread1.start()

    print("Exiting Main Thread")

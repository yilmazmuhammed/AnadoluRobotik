# -*- coding: utf-8 -*
import threading
from queue import Queue

import serial
import time
import os


class Lidar:
    def __init__(self, tty_port):
        self.tty_port = tty_port
        self.serial_port = None
        self.distance = None
        self.strength = None
        self.read_thread = None
        self.read_lock = threading.Lock()
        self.running = False

    def _open(self):
        try:
            self.serial_port = serial.Serial(self.tty_port, 115200)
            print(self.tty_port, "Açıldı")
            if not self.serial_port.is_open:
                self.serial_port.open()
            self.distance, self.strength = self._get_data()
        except Exception as e:
            raise e

    def start(self):
        if self.running:
            print('Lidar is already running')
            return None
        if self.running is False:
            self._open()
            self.running = True
            self.read_thread = threading.Thread(target=self.update_values)
            self.read_thread.start()
        return self

    def update_values(self):
        while self.running:
            try:
                count = self.serial_port.in_waiting
                if count > 8:
                    recv = self.serial_port.read(9)
                    self.serial_port.reset_input_buffer()
                    if recv[0] == 0x59 and recv[1] == 0x59:
                        distance = recv[2] + recv[3] * 256
                        strength = recv[4] + recv[5] * 256
                        with self.read_lock:
                            self.distance = distance
                            self.strength = strength
            except RuntimeError:
                print("Could not read values from lidar")
                # FIX ME - stop and cleanup thread
                # Something bad happened

    def _get_data(self):
        count = self.serial_port.in_waiting
        if count > 8:
            recv = self.serial_port.read(9)
            self.serial_port.reset_input_buffer()
            # if recv[0] == 0x59 and recv[1] == 0x59:
            print(recv)
            if recv[0] == 0x59 and recv[1] == 0x59:
                distance = recv[2] + recv[3] * 256
                strength = recv[4] + recv[5] * 256

                return distance, strength
        return None, None

    def get_data(self):
        with self.read_lock:
            distance = self.distance
            strength = self.strength
        return distance, strength

    def stop(self):
        if self.running:
            self.running = False
            self.serial_port.close()
            self.read_thread.join()


def lidar_control(lock, values, ports):
    sudoPassword = "att"
    lidars = {}
    for key in ports:
        os.system('echo %s|sudo -S chmod 777 %s' % (sudoPassword, ports[key]))
        lidars[key] = Lidar(ports[key])

    for i in lidars:
        lidars[i].start()
    while True:
        # print(running)
        with lock:
            for key in lidars:
                values[key] = lidars[key].get_data()

    for i in lidars:
        lidars[i].stop()


if __name__ == '__main__':
    tl = threading.Lock()
    tv = {}
    ports = {
        "front": "/dev/ttyUSB0",
        "left": "/dev/ttyUSB1",
        "right": "/dev/ttyUSB2",
        "bottom": "/dev/ttyTHS1"
    }
    th = threading.Thread(target=lidar_control, args=(tl, tv, ports))
    th.start()
    try:
        while True:
            with tl:
                #pass
                print(tv)
    except KeyboardInterrupt:  # Ctrl+C
        th.join()

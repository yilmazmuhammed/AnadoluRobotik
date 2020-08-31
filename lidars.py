# -*- coding: utf-8 -*
from datetime import datetime
from pathlib import Path
from threading import Thread, Lock
from time import sleep

import serial
import os


class Lidar:
    def __init__(self, tty_port):
        self.tty_port = tty_port
        self.serial_port = None
        self.distance = None
        self.strength = None
        self.read_thread = None
        self.read_lock = Lock()
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
            self.read_thread = Thread(target=self.update_values)
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
                    else:
                        distance = None
                        strength = None
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
            print(self.tty_port, "kapatılıyor...")
            self.running = False
            self.read_thread.join()
            self.serial_port.close()
            print(self.tty_port, "kapatıldı...")


class RovLidars:
    def __init__(self, ports, sudo_password='att', output_file=""):
        self._lidars = {}
        self._values = {}
        self._read_thread = None
        self._read_lock = Lock()
        self._create_lidars(ports, sudo_password)
        self._running = False
        self.output = None
        if output_file != "":
            Path("logs").mkdir(parents=True, exist_ok=True)
            output_file = "logs/" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + "_lidars_" + output_file
            self.output = open(output_file, "a")

    def _create_lidars(self, ports, sudo_password):
        for key in ports:
            os.system('echo %s|sudo -S chmod 777 %s' % (sudo_password, ports[key]))
            self._lidars[key] = Lidar(ports[key])
            self._lidars[key].start()
            self._values[key] = self._lidars[key].get_data()

    def start(self):
        if self._running:
            print('Lidars is already running')
            return None

        self._running = True
        self._read_thread = Thread(target=self._update_values)
        self._read_thread.start()
        return self

    def stop(self):
        if self._running:
            print("- RovLidars is shutting down...")
            self._running = False
            for key in self._lidars:
                print("-", key, "lidar is shutting down...")
                self._lidars[key].stop()
                print("+", key, "lidar is shut down.")
            self._read_thread.join()
            if self.output:
                self.output.close()
            print("+ RovLidars is shut down.")
        else:
            print("? RovLidars is already shut down...")

    def _update_values(self):
        values = {}
        while self._running:
            for key in self._lidars:
                values[key] = self._lidars[key].get_data()
            with self._read_lock:
                self._values.update(values)
            if self.output:
                self.output.write(str(datetime.now()) + ": " + str(values))
            sleep(0.1)

    def get_values(self):
        with self._read_lock:
            values = self._values.copy()
        return values


if __name__ == '__main__':
    ports = {
        "front": "/dev/ttyUSB0",
        # "left": "/dev/ttyUSB1",
        # "right": "/dev/ttyUSB2",
        # "bottom": "/dev/ttyTHS1"
    }
    rov_lidars = RovLidars(ports=ports, sudo_password='2003')
    rov_lidars.start()
    try:
        while True:
            print(rov_lidars.get_values())
            sleep(0.1)
    except KeyboardInterrupt:
        rov_lidars.stop()

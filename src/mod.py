# main.py
import time
from machine import Pin
import ujson as json
from bluetooth import BLE


def start_example():
    in_one = Pin(13, Pin.OUT)
    in_onv = Pin(12, Pin.OUT)
    in_onv.value(1)
    for _ in range(5):
        in_one.value(not in_one.value())
        time.sleep(1)
        print("in_one: ", in_one.value())

    in_onv.value(0)

def start_prog():
    car = CarState()
    ble = BLE("REDESP", car)
    while True:
        if not ble.is_connected:
            print("Waiting for connection...")
        time.sleep(2)
        ble.send(car.car_data(as_string=True))


class CarState:
    acc: int = 0
    on_ready: int = 0
    ignite: int = 0
    engine: int = 0

    def car_data(self, as_string: bool = False) -> dict:
        data = dict(
            acc=self.acc, ignite=self.ignite, engine=self.engine, ready=self.on_ready
        )
        if as_string:
            return json.dumps(data)
        return data

    def toggle_acc(self):
        if not self.engine and not self.ignite:
            self.acc = 0 if self.acc else 1
            stat = "ON" if self.acc else "OFF"
        print("toggle_acc: ", stat)

    def toggle_ready(self):
        if not self.acc:
            print("acc is off")
            print("turning on acc")
            self.acc = 1
        time.sleep(1)
        self.on_ready = 1 if self.acc else 0
        time.sleep(2)

    def set_ignite(self):
        if not self.on_ready:
            self.toggle_ready()

        if self.on_ready and not self.engine:
            self.ignite = 1
            print("engine ignited")
            time.sleep(1)
            self.ignite = 0
            print("release ignition")

        else:
            print("engine is on, skip ignition")

    def set_off(self):
        self.acc = 0
        time.sleep(2)
        self.on_ready = 0
        time.sleep(2)
        self.engine = 0

    def start_stop_engine(self):
        if not self.engine:
            self.set_ignite()
            self.engine = 1

        else:
            self.set_off()

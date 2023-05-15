from machine import Pin, Timer
from time import sleep_ms
import ubluetooth


class BLE:
    def __init__(self, name, car_mod):
        self.name = name
        self.car_mod = car_mod
        self.ble = ubluetooth.BLE()
        self.ble.active(True)

        self.led = Pin(2, Pin.OUT)
        self.timer1 = Timer(0)
        self.timer2 = Timer(1)

        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()
        self.is_connected = False

    def connected(self):
        self.timer1.deinit()
        self.timer2.deinit()
        self.is_connected = True

    def disconnected(self):
        self.timer1.init(
            period=1000, mode=Timer.PERIODIC, callback=lambda t: self.led(1)
        )
        sleep_ms(200)
        self.timer2.init(
            period=1000, mode=Timer.PERIODIC, callback=lambda t: self.led(0)
        )
        self.is_connected = False

    def ble_irq(self, event, data):
        handler = {
            "start": self.car_mod.start_stop_engine,
            "acc": self.car_mod.toggle_acc,
            "ignite": self.car_mod.set_ignite,
            "stop": self.car_mod.set_off,
            "ready": self.car_mod.toggle_ready,
        }
        if event == 1:
            self.connected()
            self.led(1)

        elif event == 2:
            self.advertiser()
            self.disconnected()

        elif event == 3:
            buffer = self.ble.gatts_read(self.rx)
            message = buffer.decode("UTF-8").strip()
            func = handler.get(message)
            if func:
                func()
            print(message)

    def register(self):
        # Nordic UART Service (NUS)
        NUS_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
        RX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
        TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY)

        BLE_UART = (
            BLE_NUS,
            (
                BLE_TX,
                BLE_RX,
            ),
        )
        SERVICES = (BLE_UART,)
        (
            (
                self.tx,
                self.rx,
            ),
        ) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        if self.is_connected:
            self.ble.gatts_notify(0, self.tx, data + "\n")

    def advertiser(self):
        name = bytes(self.name, "UTF-8")
        self.ble.gap_advertise(
            100,
            bytearray("\x02\x01\x02", "UTF-8")
            + bytearray((len(name) + 1, 0x09))
            + name,
        )

from tango import AttrWriteType
from PyTango import DevState, DevFailed
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command, pipe
from qtpy import QtCore, QtWidgets
from qtpy.QtCore import Signal, Slot, QObject
import time
from threading import Thread
from pyrpl import Pyrpl
import queue

pyrpl_instance = None
APP = None
voltageQueue = queue.Queue()


class PyrplPlusTango(Device, metaclass=DeviceMeta):
    HOST = '131.246.145.106'
    PORT = 54545
    time.sleep(3)
    APP = None

    def init_device(self):
        Device.init_device(self)
        self.set_state(DevState.ON)

    voltage1 = attribute(label="voltage 1", dtype=float,
                         access=AttrWriteType.READ,
                         unit="V",
                         doc="Voltage on fast analog IN1 on LV Jumper setting")

    def read_voltage1(self):
        do_voltage.volt.emit("a1")
        while voltageQueue.empty():
            pass
        if voltageQueue.qsize() != 1:
            print("WARNING: voltage queue length not 1!!!")
        voltage = voltageQueue.get()
        voltageQueue.task_done()
        return voltage

    voltage2 = attribute(label="voltage 2", dtype=float,
                         access=AttrWriteType.READ,
                         unit="V",
                         doc="Voltage on fast analog IN2 on LV Jumper setting")

    def read_voltage2(self):
        do_voltage.volt.emit("a2")
        while voltageQueue.empty():
            pass
        if voltageQueue.qsize() != 1:
            print("WARNING: voltage queue length not 1!!!")
        voltage = voltageQueue.get()
        voltageQueue.task_done()
        return voltage


if __name__ == "__main__":
    APP = QtWidgets.QApplication.instance()
    if APP is None:
        APP = QtWidgets.QApplication()

    class ask_for_voltage(QObject):
        volt = Signal(str)

    @Slot(str)
    def read_voltage(stringa):
        if stringa == "a1":
            voltageQueue.put(pyrpl_instance.rp.scope.voltage_in1)
        if stringa == "a2":
            voltageQueue.put(pyrpl_instance.rp.scope.voltage_in2)

    do_voltage = ask_for_voltage()
    do_voltage.volt.connect(read_voltage)

    pyrpl_instance = Pyrpl(config='test19_05_03')
    pyrpl_instance.lockbox.classname = "AG_Lockbox"

    tango_thread = Thread(target=lambda: run([PyrplPlusTango]))
    tango_thread.start()
    APP.exec()

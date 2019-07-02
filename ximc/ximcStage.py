from ctypes import *
import time
import os
import sys
import tempfile
import re
import Stage
import math
import inspect

if sys.version_info >= (3, 0):
    import urllib.parse
try:
    from pyximc import *
except ImportError as err:
    print(
        "Can't import pyximc module. The most probable reason is that you haven't copied pyximc.py to the working "
        "directory. See developers' documentation for details.")
    exit()
except OSError as err:
    print(
        "Can't load libximc library. Please add all shared libraries to the appropriate places (next to pyximc.py on "
        "Windows). It is decribed in detail in developers' documentation. On Linux make sure you installed "
        "libximc-dev package.")
    exit()


class StandaStage(Stage.Stage):
    def __init__(self):
        """Aus Stage"""
        self.position = {
            "position_current_Steps": 0,
            "position_current_uSteps": 0,
            "position_new_Steps": 0,
            "position_new_uSteps": 0,
        }
        """Aus Instrument"""
        self.connection_type = 'XIMC'
        self.configuration = {}
        self.load_configurution()
        self.position_zero = 0
        self.TerraFaktor = 1
        self.MicrostepMode = 1
        self.StepsPerRev = 1
        self.Laser = 633 * 10 ** -9  # should be 633*10^-9
        self.LichtinLuft = 299705518
        self.velocity = 10
        self.device_id = None
        self.lib = lib


    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    """Aus Instrument"""

    def connect(self):
        if self.device_id is not None:
            print('Device already connected')
            return True
        else:
            self.device_id = self._Standa_Connect_
            if self.device_id <= 0:
                print('kein Verbundenes Gerät...exiting')
                return False
            else:
                """rufe hier ximcStage_functionCalls get engine settings auf"""
                self.Standa_get_engine_settings()
                print('Verbundenes Gerät' + str(self.device_id))
                return True

    def disconnect(self):
        print('\ndisconnect aufgerufen!')
        if self.device_id is not None:
            self._Standa_Close_()
            self.device_id = None
            print('Connection has been closed')
            return True

    def read(self):
        print("Direct Read not possible through ximc")

    def write(self):
        print("Direct write not possible through ximc")

    def save_configurution(self):
        print("Not implemented")

    def load_configurution(self):
        print("Not implemented")

    def set_configurution(self):
        print("Not implemented")

    def get_configurution(self):
        print("Not implemented")

    def in_case_terra_sends_SDN(self):
        time.sleep(.100)

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    """Standa Stage Befehle"""

    def position_get(self):
        positionHandler = self.Standa_get_position()
        self.position["position_current_Steps"] = positionHandler.Position
        self.position["position_current_uSteps"] = positionHandler.uPosition

    def set_zero_position(self):
        self.lib.command_zero(self.device_id)  # "does this work?"

    def move_absolute_in_as(self, new_position_in_as):
        print('\nMove Ab in as aufgerufen!')
        print('neue Position in as: ' + repr(new_position_in_as))
        self.position_as_to_steps(new_position_in_as)
        pos = self.position["position_new_Steps"]
        upos = self.position["position_new_uSteps"]
        print('neue Position in Steps: ' + str(pos) + ', uSteps: ' + str(upos))
        self.lib.command_move(self.device_id, pos, upos)

        if self.statusHandler():
            print('Move Ab in as has arrived!')
        else:
            print('Move Ab in as something went wrong!')

    def move_absolute_in_steps(self, new_position_fullSteps, new_position_uSteps):#TODO: falls uSteps größer als 256, dann wird fahrergebnis negativ gewertet....
        print('\nMove Ab in steps aufgerufen!')
        self.position["position_new_Steps"] = new_position_fullSteps
        self.position["position_new_uSteps"] = new_position_uSteps
        print('neue Position in steps: ' + repr(self.position["position_new_Steps"]) + ', uSteps: ' + repr(
            self.position["position_new_uSteps"]))
        result=self.lib.command_move(self.device_id, self.position["position_new_Steps"], self.position["position_new_uSteps"])
        if result == Result.Ok:
            print('Move Ab in steps result ok!')
        else:
            print('Move Ab in steps result bad!')
            print('because we might still moving!')
        if self.statusHandler():
            print('Move Ab in steps has arrived!')
        else:
            print('Move Ab in steps something went wrong!')

    def move_relative_in_as(self, Shift_in_as):
        print('\nmove_relative_in_as aufgerufen!')
        print('shift Position in as um: ' + repr(Shift_in_as))
        self.position_as_to_steps(Shift_in_as)
        print('position_new enthält jetzt die Shift Werte!')
        self.lib.command_movr(self.device_id, self.position["position_new_Steps"], self.position["position_new_uSteps"])

        if self.statusHandler():
            print('move_relative_in_as has arrived!')
        else:
            print('move_relative_in_as something went wrong!')

    def move_relative_in_steps(self, new_position_fullSteps, new_position_uSteps):
        print('\nmove_relative_in_steps aufgerufen!')
        self.position["position_new_Steps"] = new_position_fullSteps
        self.position["position_new_uSteps"] = new_position_uSteps

        self.lib.command_movr(self.device_id, self.position["position_new_Steps"], self.position["position_new_uSteps"])
        if self.statusHandler():
            print('move_relative_in_as has arrived!')
        else:
            print('move_relative_in_as something went wrong!')

    def go_home(self):

        print('\ngo_home aufgerufen!')
        self.get_home()
        self.position["position_new_Steps"] = 0
        self.position["position_new_uSteps"] = 0
        result = self.lib.command_home(self.device_id)
        result = self.lib.command_home(self.device_id)
        if result == Result.Ok:
            print('go_home result ok')
        if self.statusHandler():
            print('go_home has arrived!')
            return True
        else:
            print('go_home something went wrong!')
            print('this usually never works so lets')
            print('set home by move to zero position!')
            step = -1*self.position["position_current_Steps"]
            ustep = -1*self.position["position_current_uSteps"]
            self.move_relative_in_steps(step, ustep)
            print('go_home has arrived!')
            return True



    def get_home(self):
        print('\nget_home aufgerufen!')
        x_home = home_settings_t()
        result = self.lib.get_home_settings(self.device_id, byref(x_home))
        if result == Result.Ok:
            print('\n Home Settings are:')
            for key in dir(x_home):
                if key[:1] == "_":
                    pass
                    # do nothing
                else:
                    print(key, '->', getattr(x_home, key))
        return x_home


    def set_zero_position(self):
        print('\nset_zero_position aufgerufen!')
        self.position["position_new_Steps"] = 0
        self.position["position_new_uSteps"] = 0
        self.lib.command_zero(self.device_id)
        self.position_get()
        # statusHandler() Unnecessary here
        """if self.statusHandler():
            print('set_zero_position has arrived!')
        else:
            print('set_zero_position went wrong!')"""

    def move_left(self):
        print('\nmove_left aufgerufen!')
        self.lib.command_left(self.device_id)

    def move_right(self):
        print('\nmove_right aufgerufen!')
        self.lib.command_right(self.device_id)

    def stop_move(self):
        print('\nstop_move aufgerufen!')
        self.lib.command_sstp(self.device_id)
        time.sleep(.500)

    def fast_stop(self):
        print('\nfast_stop aufgerufen!')
        string = 'dont use me!!\n its hurting!'
        print(string)
        self.lib.command_stop(self.device_id)
        time.sleep(.500)
        return string
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    """Stuff notwendig für Stage Befehle"""

    def Umrechnungsfaktor(self):
        return (self.Laser / self.LichtinLuft) / (
                (self.StepsPerRev * 3 / 2) * self.MicrostepValue()) * 10 ** +18  # Umrechungsfaktor in uSteps/as

    def position_current_in_as(self):
        if self.position["position_new_uSteps"] >= self.MicrostepValue():
            self.position["position_new_Steps"] += 1
            self.position["position_new_uSteps"] -= self.MicrostepValue()
            print('position korrigiert:')
            print('position_new Steps' + repr(self.position["position_new_Steps"]) + ',position_new uSteps' + repr(
                self.position["position_new_uSteps"]))
        return self.roundTraditional(
            (self.position["position_current_Steps"] * self.MicrostepValue() +
             self.position["position_current_uSteps"]) * self.Umrechnungsfaktor() * self.TerraFaktor, 0)

    def position_as_to_steps(self, new_position_in_as):
        var_value = new_position_in_as / self.TerraFaktor / self.Umrechnungsfaktor()
        self.position["position_new_Steps"] = math.floor(var_value / self.MicrostepValue())
        self.position["position_new_uSteps"] = int(
            self.roundTraditional(var_value - self.MicrostepValue() * self.position["position_new_Steps"], 0))
        print('\nposition angepasst:')
        for key, val in self.position.items():
            print(key, "=>", val)

    def MicrostepValue(self):  # works
        return 2 ** self.MicrostepMode / 2

    def statusHandler(self):
        gohomeflag = False
        if self.position["position_new_Steps"] == 0 & self.position["position_current_Steps"] == 0:
            gohomeflag = True

        while True:
            time.sleep(.500)
            statushand = self.Standa_Status()
            self.position["position_current_Steps"] = statushand.CurPosition
            self.position["position_current_uSteps"] = statushand.uCurPosition
            print('Now at: Steps ' + repr(self.position["position_current_Steps"]) + ', uSteps ' + repr(
                self.position["position_current_uSteps"]))
            if getattr(statushand, 'MoveSts') == 0:  # if move Flag is on w8
                break
            else:
                print('Moving...')

        if not gohomeflag:
            if self.position["position_current_uSteps"] < 0:
                print('uSteps negativ. Corrigiere')
                self.position["position_current_Steps"] = self.position["position_current_Steps"]-1
                self.position["position_current_uSteps"] = float(self.position["position_current_uSteps"])+self.MicrostepValue()

            if self.position["position_current_uSteps"] >= self.MicrostepValue():
                print('uSteps zu groß. Corrigiere')
                self.position["position_current_Steps"] = self.position["position_current_Steps"] + 1
                self.position["position_current_uSteps"] = float(
                    self.position["position_current_uSteps"]) - self.MicrostepValue()

        if self.position["position_current_Steps"] == self.position["position_new_Steps"]:
            print('Steps angekommen')
        if self.position["position_current_uSteps"] == self.position["position_new_uSteps"]:
            print('uSteps angekommen')
            return True
        else:
            print('Staus handler: something went wrong')
            return False

    @property
    def POS(self):
        self.position_get()
        print('pos in steps: ' + str(self.position["position_current_Steps"]) + ' uSteps: ' +
              str(self.position["position_current_uSteps"]))
        pos = self.position_current_in_as()
        return pos

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    """Little helper Stuff"""

    def roundTraditional(self, val, digits):  # Runden
        return round(val + 10 ** (-len(str(val)) - 1), digits)

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    """Standa Stuff"""

    @property
    def _Standa_Connect_(self):
        # variable 'lib' points to a loaded library
        # note that ximc uses stdcall on win
        print("Library loaded")

        sbuf = create_string_buffer(64)
        self.lib.ximc_version(sbuf)
        print("Library version: " + sbuf.raw.decode())

        # This is device search and enumeration with probing. It gives more information about devices.
        devenum = self.lib.enumerate_devices(EnumerateFlags.ENUMERATE_PROBE, None)
        print("Device enum handle: " + repr(devenum))
        print("Device enum handle type: " + repr(type(devenum)))

        dev_count = self.lib.get_device_count(devenum)
        print("Device count: " + repr(dev_count))

        controller_name = controller_name_t()
        for dev_ind in range(0, dev_count):
            enum_name = self.lib.get_device_name(devenum, dev_ind)
            result = self.lib.get_enumerate_device_controller_name(devenum, dev_ind, byref(controller_name))
            if result == Result.Ok:
                print("Enumerated device #{} name (port name): ".format(dev_ind) + repr(
                    enum_name) + ". Friendly name: " + repr(controller_name.ControllerName) + ".")

        open_name = None
        if len(sys.argv) > 1:
            open_name = sys.argv[1]
        elif dev_count > 0:
            open_name = self.lib.get_device_name(devenum, 0)
        elif sys.version_info >= (3, 0):
            # use URI for virtual device when there is new urllib python3 API
            tempdir = tempfile.gettempdir() + "/testdevice.bin"
            if os.altsep:
                tempdir = tempdir.replace(os.sep, os.altsep)
            # urlparse build wrong path if scheme is not file
            uri = urllib.parse.urlunparse(urllib.parse.ParseResult(scheme="file", \
                                                                   netloc=None, path=tempdir, params=None, query=None,
                                                                   fragment=None))
            open_name = re.sub(r'^file', 'xi-emu', uri).encode()

        if not open_name:
            exit(1)

        if type(open_name) is str:
            open_name = open_name.encode()

        print("\nOpen device " + repr(open_name))
        device_id = self.lib.open_device(open_name)
        print("Device id: " + repr(device_id))
        self.lib.free_enumerate_devices(devenum)
        self.device_id = device_id
        self.connect()
        return device_id

    def _Standa_Close_(self):
        # self.lib.close_device(self.device_id)
        self.lib.close_device(byref(cast(self.device_id, POINTER(c_int))))  # aus testpython

    def Standa_get_engine_settings(self):
        engine_settings = engine_settings_t()
        result = self.lib.get_engine_settings(self.device_id, byref(engine_settings))
        if result == Result.Ok:
            print('\n Engine Settings are:')
            for key in dir(engine_settings):
                if key[:1] == "_":
                    pass
                    # do nothing
                else:
                    print(key, '->', getattr(engine_settings, key))

            self.MicrostepMode = engine_settings.MicrostepMode
            self.StepsPerRev = engine_settings.StepsPerRev
            if not self.StepsPerRev == 200:
                print('StepsPerRev entsprechen nicht 200!\n Betrieb nicht konform!\nUmrechnungen Fehlerhaft!')
                self.disconnect()
                sys.exit()
            return result
        else:
            print('something went wrong!')

    def Standa_get_position(self):
        print("\nRead position")
        x_pos = get_position_t()
        result = self.lib.get_position(self.device_id, byref(x_pos))
        if result == Result.Ok:
            print("Position: " + repr(x_pos.Position))
            print("uPosition: " + repr(x_pos.uPosition))
            # pos_dict = dict(x_pos._fields_)
        else:
            print('something went wrong!')
        return x_pos

    def Standa_Status(self):
        """ possible status_mode should be:
            MoveSts         Flags of move state
    		MvCmdSts        Move command state
    	    PWRSts          Flags of power state of stepper motor
    		EncSts          Encoder state
    		WindSts         Winding state
    		CurPosition     Current position
    		uCurPosition    Step motor shaft position in 1/256 microsteps
    		EncPosition     Cureent encoder position
    		CurSpeed        Motor shaft speed
    		uCurSpeed       Part of motor shaft speed in 1/2256 microsteps
    		Ipwr            Engine current
    		Upwr            Power supply voltage
    		Iusb            USB current consumption
    		Uusb            USB voltage
    		CurT            Temperature in thnths od degress C
    		Flags           Status flags
    		GPIOFlags       Status flags
    		CmdBufFreeSpace This field shows the amount of free cells buffer synchronizazion chain
    	"""
        print("\nStanda_Status")
        x_status = status_t()
        result = self.lib.get_status(self.device_id, byref(x_status))
        print("Result: " + repr(result))
        if result == Result.Ok:
            print("Status.MoveSts: " + repr(x_status.MoveSts))
            print("Status.CurPosition : " + repr(x_status.CurPosition))
            print("Status.uCurPosition: " + repr(x_status.uCurPosition))
            print("Status.Flags: " + repr(hex(x_status.Flags)))
        else:
            print('something went wrong!')

        # status_dict = self.obj_to_dict(x_status)
        return x_status

    def Standa_get_motor_settings(self):
        """	_fields_ = [
		("Speed", c_uint),
		("uSpeed", c_uint),
		("Accel", c_uint),
		("Decel", c_uint),
		("AntiplaySpeed", c_uint),
		("uAntiplaySpeed", c_uint),
	]"""
        print("\nStanda_get_motor_settings")
        y_status = move_settings_t()
        result = self.lib.get_move_settings(self.device_id, byref(y_status))
        if result == Result.Ok:
            for key in dir(y_status):
                if key[:1] == "_":
                    pass
                    # do nothing
                else:
                    print(key, '->', getattr(y_status, key))
        else:
            print('something went wrong!')
        return y_status

    def _Standa_set_motor_settings_(self):
        print("Called set motor settings")
        print("dont do this!")
        q = input("You really want this?(Y/N)")
        if q == "N" or q == "n":
            return False
        elif q == "Y" or q == "y":
            y_status = move_settings_t()
            result = self.lib.get_move_settings(self.device_id, byref(y_status))
            if result == Result.Ok:
                print('\n Move Settings are:')
                for key in dir(y_status):
                    if key[:1] == "_":
                        pass
                        # do nothing
                    else:
                        print(key, '->', getattr(y_status, key))
                print("\nmodifing move settings!")
                q2 = input("You really want this?(Y/N)")
                if q2 == "N" or q2 == "n":
                    return False
                elif q2 == "Y" or q2 == "y":
                    y_status.Speed = 1000
                    y_status.uSpeed = 256
                    y_status.Accel = 2000
                    result = self.lib.set_move_settings(self.device_id, byref(y_status))
                    if result == Result.Ok:
                        for key in dir(y_status):
                            if key[:1] == "_":
                                pass
                                # do nothing
                            else:
                                print(key, '->', getattr(y_status, key))
                    else:
                        print('something went wrong!')
                else:
                    print('something went wrong!')
                    return y_status
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # control gui stuff


if __name__ == "__main__":
    stage = StandaStage()
    stage.connect()
    stage.Standa_Status()
    stage.position_get()
    stage.Standa_get_position()
    stage.set_zero_position()
    stage.move_absolute_in_as(153600)#TODO: Umrechnungen alle Richtig? vonwegen Terra und Gui to server_tcp to ximcStage
    # stage.Umrechnungsfaktor()
    # stage.set_zero_position()
    # stage.Standa_get_position()
    #
    # stage.in_case_terra_sends_SDN()
    # stage.POS
    #
    # stage.move_left()
    # time.sleep(2)
    # stage.fast_stop()#dont use me, its hurting
    # stage.stop_move()
    # stage.move_right()
    # time.sleep(1)
    # stage.stop_move()
    # value = stage.position_current_in_as()
    # #stage.fast_stop()
    #
    # stage.read()
    # stage.write()
    # stage.move_relative_in_as(-105)
    # stage.move_absolute_in_as(7000)
    # stage.Standa_get_motor_settings()
    # # stage._Standa_set_motor_settings_()
    # #stage.Standa_get_motor_settings()
    # stage.Standa_get_engine_settings()
    #
    # stage.set_zero_position()
    # stage.move_relative_in_as(105)
    # stage.POS
    # stage.go_home()

    # TODO debuggen~~~~~~~~
    #^^^^^^^debuggen^^^^^^^^^^^^^^

    stage.disconnect()


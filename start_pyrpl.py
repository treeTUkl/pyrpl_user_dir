from pyrpl import pyrpl
import sys

class pyrpl_p(object):
    def __init__(self):
        self.pyrpl_Connected = False
        self.pyrpl_p = None
        self.pyrpl_voltage = 0
        self.start()

    def start(self):
        try:
            if self.pyrpl_p is None:
                self.pyrpl_p = pyrpl.Pyrpl(config='test19_05_03')
                self.pyrpl_p.lockbox.classname = "AG_Lockbox"
        except (RuntimeError, TypeError, NameError):
            self.windowprintqueue.put(['printme', 'Something went wrong with pyrpl'])
            self.pyrpl_p=None
        finally:
            if not self.pyrpl_p is None:
                self.pyrpl_Connected = True
            else:
                self.pyrpl_Connected = False

            return self.pyrpl_Connected

    def stop_pyrpl(self):
        # TODO OSError: Socket is closed dont know how to handle
        if self.pyrpl_Connected:
            try:
                self.pyrpl_p._clear()
            except Exception as error:
                for each in error:
                    print('Stop_prypl error catched "%s' % data)
                    pass
                #self.print_list.addItem(str(error))
                #QMessageBox.about(self, "closing error",
                #                  "This is an expected error. Please close the pyrpl window via ""x""")
            finally:
                self.pyrpl_Connected = False
                #sys.exit()
                self.pyrpl_p = None

    def get_voltage(self, channel):
        try:
            if channel == "a1":
                voltage= self.pyrpl_p.rp.scope.voltage_in1
                return float(voltage)
            elif channel == "a2":
                voltage =self.pyrpl_p.rp.scope.voltage_in2
                return float(voltage)
            else:
                return 0
        except Exception as error:
                #for each in error:
                print('get_voltage error catched "%s' % data)

                return False


if __name__ == "__main__":
    print("start this")
    pyrpl_p = pyrpl_p()
    result =pyrpl_p.start()
    print(result)
    result=pyrpl_p.get_voltage("a1")
    print("Voltage1: " + str(result))
    result=pyrpl_p.get_voltage("a2")
    print("Voltage2: " + str(result))
    #pyrpl_p.stop_pyrpl()
    print("done")
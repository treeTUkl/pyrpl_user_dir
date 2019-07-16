from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import *  # QAction, QApplication, QFileDialog, QMessageBox, QWidget,
from PyQt5.QtCore import *
import random
import numpy
import sys
import time
import socket
from pyrpl import pyrpl
from pyrpl import sshshell
import threading
import queue


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


class Window(QtWidgets.QMainWindow):
    def _init_(self):
        super(Window, self).__init__()
        self.ui = uic.loadUi("standa_pyrpl_gui.ui", self)
        self.ac_messung = False
        self.run_messung = False
        self.Standa_Connected = False
        self.standa_live_control = False
        self.pyrpl_Connected = False
        self.pyrpl_p = None
        self.pyrpl_voltage = 0
        self.windowprintqueue = queue.Queue()
        self.messung_pos=0
        self.standa_moving = False
        self.home()

    def home(self):
        extractAction = QAction('&Get to the choppah', self)
        extractAction.setShortcut('Ctrl+Q')
        extractAction.setStatusTip('leave the app')
        extractAction.triggered.connect(self.close_application)

        self.print_list.setAutoScroll(True)
        self.step_list.setAutoScroll(True)
        self.progressBar.setValue(0)
        self.statusBar()

        self.Add_to_list_Button.clicked.connect(self.add_to_list)

        self.buttonBox.accepted.connect(self.start_messung)
        self.buttonBox.rejected.connect(self.stop_messung)
        self.ac_checkBox.stateChanged.connect(self.ac_check)

        self.Clear_list_Button.clicked.connect(self.clear_list)
        self.Load_list_Button.clicked.connect(self.ListFilePicker)
        self.Save_list_Button.clicked.connect(self.ListFileSaver)
        self.select_file_Button.clicked.connect(self.Ac_File_Picker)
        self.Sort_list_Button.clicked.connect(self.sort_list)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&Test')
        fileMenu.addAction(extractAction)
        # self.actionFile.triggered.connect(extractAction)

        # lets do standa stuff blow here
        self.Standa_Connect_Button.clicked.connect(self.Standa_Connect_to_Server)
        self.Standa_Close_Button.clicked.connect(self.Standa_Close_Connection_to_Server)
        self.standaclient = False
        self.standa_live_control_ButtonBox.accepted.connect(self.standa_live_control_start)
        self.standa_live_control_ButtonBox.rejected.connect(self.standa_live_control_stop)
        self.Go_right_Button.clicked.connect(self.standa_right)
        self.Stop_Button.clicked.connect(self.standa_stop)
        self.Go_left_Button.clicked.connect(self.standa_left)
        self.move_to_Button.clicked.connect(self.standa_move_to)
        self.Go_Home_Button.clicked.connect(self.standa_go_home)
        self.SetHome_Button.clicked.connect(self.standa_set_home)
        self.Pyrpl_Start_Button.clicked.connect(self.pyrpl_start)
        self.Pyrpl_Get_Voltage.clicked.connect(self.pyrpl_prozess_fn)
        self.Pyrpl_Close_Button.clicked.connect(self.clean_pyrpl)
        self.get_standa_settings_Button.clicked.connect(self.standa_get_settings)
        self.Set_Motor_Settings_Button.clicked.connect(self.standa_set_settings)
        self.Microstep_mode_choos_spinBox.valueChanged.connect(self.Microstep_changed)
        self.StandaWidget.currentChanged.connect(self.standa_handling)
        self.reverse_List_checkBox.stateChanged.connect(self.sort_list)
        self.move_relative_Button_2.clicked.connect(self.standa_move_relative)  # TODO
        self.readQueuebool=True
        self.show()
        self.readQueue()

    def sort_list(self):
        state = self.reverse_List_checkBox.isChecked()
        numbers = []
        for x in range(self.step_list.count()):
            numbers.append(float(self.step_list.item(x).text()))
        numbers.sort(reverse=state)
        self.step_list.clear()
        for x in numbers:
            self.step_list.addItem(str(x))

    def ListFilePicker(self):
        name, _ = QFileDialog.getOpenFileName(self, 'Open File', options=QFileDialog.DontUseNativeDialog)
        if not name == "":
            file = open(name, 'r')
            with file:
                text = file.read()
                for x in text.splitlines():
                    if isfloat(x):
                        self.step_list.addItem(str(x))
            return True
        return False

    def Ac_File_Picker(self):
        name, _ = QFileDialog.getSaveFileName(self, 'Save File', options=QFileDialog.DontUseNativeDialog)
        if name == "":
            return False
        else:
            if not name[len(name) - 3:] == 'xml':
                name = name + str('.xml')
            self.filePath_Edit.setText(str(name))
            return True

    def ListFileSaver(self):
        name, _ = QFileDialog.getSaveFileName(self, 'Save File', options=QFileDialog.DontUseNativeDialog)
        if not name == "":
            if not name[len(name) - 3:] == 'txt':
                name = name + str('.txt')
            file = open(name, 'w')
            text = ""
            for x in range(self.step_list.count()):
                string = self.step_list.item(x).text()
                text = text + string + str('\n')
            file.write(text)
            file.close()

    def ac_check(self):
        state = self.ac_checkBox.isChecked()
        if state:
            if self.filePath_Edit.text() == '':
                result = self.Ac_File_Picker()
                self.ac_messung = True
                if not result:
                    self.ac_messung = False
            else:
                self.ac_messung = True
        else:
            self.ac_messung = False

    def start_messung(self):
        self.run_messung = True
        self.messung()

    def standa_moving_Check(self, bool=None):
        if bool is None:
            return self.standa_moving
        elif bool is True:
            self.standa_moving_Check_radioButton.animateClick()
            self.standa_moving = True
        elif bool is False:
            self.standa_moving = False

    def messung(self):
        name = self.filePath_Edit.text()
        if name == "":
            pass
        else:
            file = open(name, 'a')
            text = 'Postition in as' + str('\t') + str('\t') + 'Voltage' + str('\n')
            file.write(text)

        self.ac_messung = self.ac_checkBox.isChecked()
        self.completed = 0
        self.complete = 1 / self.step_list.count() * 100
        input = self.pyrpl_input_choice()
        if not self.standaclient == False & self.Standa_Connected == True:
            if self.pyrpl_p is not None:
                if self.pyrpl_Connected_check():
                    for self.x in range(self.step_list.count()):
                        if self.run_messung:
                            xitem = self.step_list.item(self.x).text()
                            step = 'MOV' + xitem
                            client.clientsendqueue.put(['send', str(step)])  # TODO  bisher gibts kein send queue
                            self.standa_moving = True
                            while self.standa_moving:
                                time.sleep(200)
                                client.clientsendqueue.put(['send', 'STATE'])
                                QApplication.processEvents()
                                time.sleep(200)
                                client.clientsendqueue.put(['send', 'POSS'])
                                QApplication.processEvents()

                                if self.standa_moving_Check() == False:
                                    client.clientsendqueue.put(['send', 'POS'])
                                    break

                            standa_result = self.messung_pos  # TODO ist der Rückgabewert in as Korrekt?

                            self.standa_moving = False
                            self.completed += self.complete
                            self.progressBar.setValue(self.completed)
                            self.windowprintqueue.put(['printme', 'POS' + standa_result])
                            QApplication.processEvents()
                            if self.ac_messung:
                                if input == 1:
                                    self.pyrpl_voltage = self.pyrpl_p.rp.scope.voltage_in1
                                elif input == 2:
                                    self.pyrpl_voltage = self.pyrpl_p.rp.scope.voltage_in2
                                else:
                                    self.pyrpl_result = random.random()
                                    self.windowprintqueue.put(['printme', 'No pyrpl input generating randoms'])
                                pyrpl_result = self.pyrpl_voltage
                                text = str(standa_result) + str('\t') + str('\t') + str(pyrpl_result)
                                text = text + str('\n')
                                if not name == "":
                                    file.write(text)

                            if self.x == self.step_list.count() - 1:
                                if not self.messung_finished():
                                    self.progressBar.setValue(100)
                                    text = str('\n') + 'Messung finished\n'
                                    self.standa_live_control = False
                                    if not name == "":
                                        file.write(text)

                        else:
                            self.windowprintqueue.put(['printme', 'Messung Canceled'])
                            self.progressBar.setValue(0)
                            text = str('\n') + 'Messung Canceled\n'
                            self.standa_live_control = False
                            if not name == "":
                                file.write(text)
                            break
            else:
                QMessageBox.about(self, "No active Pyrpl", "Connect to Pyrpl first!")
                self.progressBar.setValue(0)
                self.windowprintqueue.put(
                    ['printme', 'Connect to Standa first\nStanda_Connected is ' + str(self.Standa_Connected)])

        else:
            QMessageBox.about(self, "No Standa Server", "Connect to Standa first!")
            self.progressBar.setValue(0)
            self.windowprintqueue.put(
                ['printme', 'Connect to Standa first\nStanda_Connected is ' + str(self.Standa_Connected)])

        if not name == "":
            file.close()

    def messung_finished(self):
        self.print_list.addItem(str('Messung Done'))
        self.print_list.scrollToBottom()

    def stop_messung(self):
        self.run_messung = False
        return False

    def add_to_list(self):
        start = self.Start_SpinBox.value()
        end = self.End_SpinBox.value()
        stepsize = self.Stepsize_SpinBox.value()
        if stepsize == 0.0:
            pass
        else:
            if end < start:
                x = start
                start = end
                end = x
            for x in numpy.arange(start, end + stepsize, stepsize):
                value = str(x)
                self.step_list.addItem(value)

    def clear_list(self):
        self.step_list.clear()

    def close_application(self):
        print("whooaaaa so custom!!!")
        self.Standa_Close_Connection_to_Server()
        self.readQueuebool=False
        sys.exit()

    def readQueue(self):
        while self.readQueuebool:
            if client.clientprintqueue.empty() == False:
                clientstatus = client.clientprintqueue.get()
                client.clientprintqueue.task_done()
                if clientstatus[0] == "printme":
                    string = str(clientstatus[1])
                    self.print_list.addItem(string)
                    self.print_list.scrollToBottom()
                elif clientstatus[0] == "Standa_Connected_check":
                    mybool = bool(clientstatus[1])
                    self.Standa_Connected_check(mybool)
                elif clientstatus[0] == "MOV":
                    self.print_list.addItem('Moving via MOV')
                    self.print_list.scrollToBottom()
                    self.standa_moving_Check(True)

                    while self.standa_moving_Check():
                        time.sleep(200)
                        client.clientsendqueue.put(['send', 'STATE'])
                        QApplication.processEvents()
                        time.sleep(200)
                        client.clientsendqueue.put(['send', 'POSS'])
                        QApplication.processEvents()
                        if self.standa_moving_Check() == False:
                            client.clientsendqueue.put(['send', 'POSS'])
                            break
                elif clientstatus[0] == "MOVV":
                    self.print_list.addItem('Moving via MOVV')
                    self.print_list.scrollToBottom()
                    self.standa_moving = True
                    while self.standa_moving:
                        time.sleep(200)
                        client.clientsendqueue.put(['send', 'STATE'])
                        QApplication.processEvents()
                        time.sleep(200)
                        client.clientsendqueue.put(['send', 'POSS'])
                        QApplication.processEvents()

                        if self.standa_moving_Check() == False:
                            client.clientsendqueue.put(['send', 'POSS'])
                            break

                elif clientstatus[0] == "LMOVE":
                    self.print_list.addItem('Moving via LMOVE')
                    self.print_list.scrollToBottom()
                    self.standa_moving_Check(True)
                elif clientstatus[0] == "RMOVE":
                    self.print_list.addItem('Moving via RMOVE')
                    self.print_list.scrollToBottom()
                    self.standa_moving_Check(True)
                elif clientstatus[0] == "SDN":
                    self.print_list.addItem('Got SDN')
                    self.print_list.scrollToBottom()
                elif clientstatus[0] == "DEH":
                    self.print_list.addItem('Got DEH')
                    self.print_list.scrollToBottom()
                    client.clientsendqueue.put(['send', 'POSS'])
                elif clientstatus[0] == "MVR":
                    self.print_list.addItem('Moving via MVR')
                    self.print_list.scrollToBottom()
                    self.standa_moving = True

                    while self.standa_moving:
                        time.sleep(200)
                        client.clientsendqueue.put(['send', 'STATE'])
                        QApplication.processEvents()
                        time.sleep(200)
                        client.clientsendqueue.put(['send', 'POSS'])
                        QApplication.processEvents()
                        if self.standa_moving_Check() == False:
                            client.clientsendqueue.put(['send', 'POSS'])
                            break

                elif clientstatus[0] == "MVRR":
                    self.print_list.addItem('Moving via MVRR')
                    self.print_list.scrollToBottom()
                    self.standa_moving_Check(True)
                    while self.standa_moving_Check():
                        time.sleep(200)
                        client.clientsendqueue.put(['send', 'STATE'])
                        QApplication.processEvents()
                        time.sleep(200)
                        client.clientsendqueue.put(['send', 'POSS'])
                        QApplication.processEvents()

                        if self.standa_moving_Check() == False:
                            client.clientsendqueue.put(['send', 'POSS'])
                            break

                elif clientstatus[0] == "STOPMOVE":
                    while self.standa_moving_Check():
                        client.clientsendqueue.put(['send', 'STATE'])
                        if self.standa_moving_Check() == False:
                            break
                    self.print_list.addItem('STATE: ' + clientstatus[1])
                    self.print_list.scrollToBottom()


                elif clientstatus[0] == "STATE":
                    states = clientstatus[1].split(", ")
                    MoveSts = states[1].split("-> ")
                    MoveSts = MoveSts[1]
                    CurSpeed = states[2].split("-> ")
                    CurSpeed = CurSpeed[1]
                    uCurSpeed = states[3].split("-> ")
                    uCurSpeed = uCurSpeed[3]
                    if CurSpeed != "0" or uCurSpeed != "0" or MoveSts != "0":
                        self.standa_moving_Check(False)
                    else:
                        self.standa_moving_Check(True)
                    self.print_list.addItem('STATE: ' + clientstatus[1])
                    self.print_list.scrollToBottom()
                elif clientstatus[0] == "POS":
                    result = clientstatus[1]
                    self.messung_pos = result
                elif clientstatus[0] == "POSS":
                    result = clientstatus[1].split(', ')
                    self.Pos_Number.display(result[0])
                    self.uPos_Number.display(result[1])
                elif clientstatus[0] == "close":
                    self.print_list.addItem('this is odd\nserver sended "close"\nso... closing socket')
                    self.print_list.scrollToBottom()
                elif clientstatus[0] == "received":
                    self.print_list.addItem('received: ' + clientstatus[1])
                    self.print_list.scrollToBottom()
                elif clientstatus[0] == "MGET":
                    result = clientstatus[1].split(", ")
                    self.get_standa_settings_listWidget.clear()
                    for each in result:
                        self.get_standa_settings_listWidget.addItem(str(each) + "\n")
                    MicrosetpValue = result[3]
                    MicrosetpValue = MicrosetpValue[len(MicrosetpValue) - 1:len(MicrosetpValue)]
                    self.Microstep_mode_choos_spinBox.setValue(int(MicrosetpValue))
                    self.print_list.scrollToBottom()
                elif clientstatus[0] == "MSET":
                    if clientstatus[1] == "Standa_set_settings worked":
                        self.print_list.addItem(str(clientstatus[1]))
                        self.print_list.scrollToBottom()
                        self.standa_get_settings()
                    else:
                        self.get_standa_settings_listWidget.clear()
                        self.get_standa_settings_listWidget.addItem("Set Settings went wrong!")

            if self.windowprintqueue.empty() == False:
                windowstatus = self.windowprintqueue.get()
                self.windowprintqueue.task_done()
                if windowstatus[0] == "printme":
                    string = str(windowstatus[1])
                    self.print_list.addItem(string)
                    self.print_list.scrollToBottom()
            QApplication.processEvents()



    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # aus standa&pyrpl_client.py
    #    pyrplclient = client('localhost', 54545)  # pyrpl_server läuft local auf dem selben rechner.
    # diodenmessung(pyrplclient, 'bnc1')
    # diodenmessung(pyrplclient, 'bnc2')
    # pyrplclient.close()
    #   standaclient= client('127.127.127.2', 22222)#standa_server über ssh auf redpitaya
    def Standa_Connect_to_Server(self):
        if self.standaclient == False:
            standa_ip = self.standa_connection_ip.text()
            standa_port = self.standa_connection_port.text()  # TODO str!
            if standa_ip == "":
                QMessageBox.about(self, "Connect where to?", "Standa IP is missing. Trying to connect to localhost")
                standa_ip = '127.0.0.1'
                standa_port = 54545
            if standa_port == "":
                QMessageBox.about(self, "Connect where to?", "Standa Port is missing")
                self.Standa_Connected_check(False)
                return False
            else:
                self.windowprintqueue.put(['printme', "Connect to Standa_Server via:\n" + str(standa_ip) + ", " + str(standa_port)])#TODO

                self.standaclient = client(standa_ip, standa_port, GUI=self)
                self.standaclient.start()  # TODO
           # if self.standaclient.sock._closed == False:
           #     self.Standa_Connected_check(True)
           # elif self.standaclient.sock._closed == True:
           #     self.Standa_Close_Connection_to_Server()

    def Standa_Connected_check(self, bool=None):
        if bool is None:
            return self.Standa_Connected
        elif bool is True:
            self.Standa_Connected = True
            self.Standa_Connected_label.setAutoFillBackground(True)
            self.Standa_Connected_label.setStyleSheet("background-color:#10ff00;")
        elif bool is False:
            self.Standa_Connected = False
            self.Standa_Connected_label.setStyleSheet("background-color:#ff0000;")
            self.Standa_Connected_label.setAutoFillBackground(False)
            self.standa_live_control = False


    def Standa_Close_Connection_to_Server(self):
        if not self.standaclient == False:
            self.standa_live_control_stop()
            self.standaclient.close()
            self.standaclient = False
            self.standa_live_control = False
            self.Standa_Connected_check(False)
        elif self.Standa_Connected == True:
            self.Standa_Connected_check(True)


    def standa_check(self):
        if self.Standa_Connected_check():
            if not self.standaclient == False:
                return True
            else:
                return False
        else:
            return False


    def standa_live_control_start(self):  # TODO the live control should be running in an thread
        if self.standa_check():
            self.standa_live_control = True
            self.Standa_live_control_widget.hide()
        if self.StandaWidget.currentIndex() == 0:
            self.standa_handling()


    def standa_handling(self):
        while self.standa_live_control & self.StandaWidget.currentIndex() == 0:
            QApplication.processEvents()
            self.standa_pos()
            QApplication.processEvents()
            if self.standa_live_control == False:
                self.standa_live_control_stop()
                break
            if self.StandaWidget.currentIndex() == 1:
                client.clientsendqueue.put(['STOPMOVE', ''])
                break


    def standa_move_relative(self):
        if self.standa_check():
            client.clientsendqueue.put(['MVRR', str(self.Pos_spinBox.value()) + ', ' + str(self.uPos_spinBox.value())])


    def standa_live_control_stop(self):
        if self.standa_check():
            client.clientsendqueue.put(['STOPMOVE', ''])
            self.Standa_live_control_widget.show()
            self.Pos_Number.display('NaN')
            self.uPos_Number.display('NaN')
            self.standa_live_control = False


    def standa_pos(self):
        if self.standa_check():
            client.clientsendqueue.put(['POSS', ''])
        else:
            self.Pos_Number.display('NaN')
            self.uPos_Number.display('NaN')


    def standa_right(self):
        if self.standa_check() & self.standa_live_control:
            client.clientsendqueue.put(['RMOVE', ''])


    def standa_left(self):
        if self.standa_check() & self.standa_live_control:
            client.clientsendqueue.put(['LMOVE', ''])


    def standa_stop(self):
        if self.standa_check() & self.standa_live_control:
            client.clientsendqueue.put(['STOPMOVE', ''])


    def standa_move_to(self):
        if self.standa_check() & self.standa_live_control:
            client.clientsendqueue.put(['MOV', str(self.Pos_spinBox.value()) + ', ' + str(self.uPos_spinBox.value())])


    def standa_go_home(self):
        if self.standa_check() & self.standa_live_control:
            client.clientsendqueue.put(['MOV', "0" + ', ' + "0"])


    def standa_set_home(self):
        if self.standa_check() & self.standa_live_control:
            client.clientsendqueue.put(['DEH', ''])


    def standa_get_settings(self):
        if self.standa_check() & self.standa_live_control:
            self.standa_stop()
            client.clientsendqueue.put(['MGET', ''])


    def standa_set_settings(self):
        if self.standa_check() & self.standa_live_control:
            self.standa_stop()
            send = "MSET"
            send = send + ", " + str(self.Motor_Speed_spinBox.value())
            send = send + ", " + str(self.Acceleration_spinBox.value())
            send = send + ", " + str(self.Deceleration_spinBox.value())
            send = send + ", " + str(self.Microstep_mode_choos_spinBox.value())
            client.clientsendqueue.put(['MSET', send])
            self.standa_get_settings()


    def Microstep_changed(self):
        MicrosetpValue = (2 ** self.Microstep_mode_choos_spinBox.value()) / 2
        self.Microstep_mode_choos_LineEdit.setText(str(int(MicrosetpValue)))


    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # aus pyrpl start.py

    def pyrpl_prozess_fn(self):
        if self.pyrpl_Connected:
            self.windowprintqueue.put(['printme', 'pyrpl Voltage'])
            self.pyrpl_voltage = self.pyrpl_p.rp.scope.voltage_in1
            self.windowprintqueue.put(['printme', 'pyrpl Voltage1: ' + str(self.pyrpl_voltage)])
            self.Volt1.display(self.pyrpl_voltage)
            self.pyrpl_voltage = self.pyrpl_p.rp.scope.voltage_in2
            self.windowprintqueue.put(['printme', 'pyrpl Voltage2: ' + str(self.pyrpl_voltage)])
            self.Volt2.display(self.pyrpl_voltage)
            if not self.pyrpl_p is None:
                self.pyrpl_Connected = True
            else:
                self.pyrpl_Connected = False


    def pyrpl_Connected_check(self, bool=None):
        if bool is None:
            return self.pyrpl_Connected
        elif bool is True:
            self.pyrpl_Connected = True
            self.Pyrpl_Started_label.setAutoFillBackground(True)
            self.Pyrpl_Started_label.setStyleSheet("background-color:#10ff00;")
        elif bool is False:
            self.pyrpl_Connected = False
            self.Pyrpl_Started_label.setStyleSheet("background-color:#ff0000;")
            self.Pyrpl_Started_label.setAutoFillBackground(False)
            self.standa_live_control = False


    def clean_pyrpl(self):
        if self.pyrpl_Connected:
            self.windowprintqueue.put(['printme', 'clean Pyrpl'])
            self.stop_pyrpl_prozess()
            self.pyrpl_p = None
            self.pyrpl_Connected_check(False)
            self.print_list.scrollToBottom()


    def stop_pyrpl_prozess(self):
        # TODO OSError: Socket is closed dont know how to handle
        if self.pyrpl_Connected:
            self.windowprintqueue.put(['printme', 'Stoping Pyrpl'])
            try:
                self.pyrpl_p._clear()
            except OSError as error:
                self.print_list.addItem(str(error))
                QMessageBox.about(self, "closing error",
                                  "This is an expected error. Please close the pyrpl window via ""x""")


    def pyrpl_input_choice(self):
        if self.pyrpl_input1.isChecked():
            return 1
        if self.pyrpl_input2.isChecked():
            return 2


    def pyrpl_start(self):  # TODO: Info aus Console in Textbox übertragen
        self.windowprintqueue.put(['printme', 'Starting Pyrpl\nThis might take a while (up to 1min)'])
        QApplication.processEvents()
        try:
            if self.pyrpl_p is None:
                self.pyrpl_p = pyrpl.Pyrpl(config='test19_05_03')
                self.pyrpl_p.lockbox.classname = "AG_Lockbox"
            else:
                self.windowprintqueue.put(['printme', 'Pyrpl already started'])

        except (RuntimeError, TypeError, NameError):
            self.windowprintqueue.put(['printme', 'Something went wrong with pyrpl'])
        finally:
            if not self.pyrpl_p is None:
                self.pyrpl_Connected_check(True)
            else:
                self.pyrpl_Connected_check(False)
            self.print_list.scrollToBottom()


class client(threading.Thread):
    clientsendqueue = queue.Queue()
    clientprintqueue = queue.Queue()

    def __init__(self, host, port, GUI):
        threading.Thread.__init__(self)
        self.sock = 0
        self.HOST = host
        self.PORT = int(port)
        self.GUI = GUI
        self.connect()

    def connect(self):
        if self.sock == 0 or self.sock._closed == True:
            # HOST = 'localhost'
            # PORT = 54545
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.sock.connect((self.HOST, self.PORT))
                client.clientprintqueue.put(['printme', 'connected to server'])#ToDO befor that the queue should be empty
                client.clientprintqueue.put(['Standa_Connected_check', True])

                threading.Thread(target=self.recv).start()
                client.clientsendqueue.put(["POS", ""])
                self.handleClientQueue()

            except ConnectionRefusedError:
                client.clientprintqueue.put(['printme', 'Connection Refused! Server might not ready'])
                msg = QtWidgets.QMessageBox()
                msg.setWindowTitle('Connection Refused!')
                msg.setText("Do you want to try again?")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                buttonReply = msg.exec_()
                if buttonReply == QMessageBox.Yes:
                    client.clientprintqueue.put(['printme', 'then, keep runnig.'])
                    self.sock = 0
                    self.connect()
                else:
                    client.clientprintqueue.put(['printme', 'stopping....'])
                    self.sock.close()
                    self.GUI.standaclient = False
                    self.GUI.Standa_Close_Connection_to_Server()

            except OSError:
                client.clientprintqueue.put(['printme', 'Connection Refused! Server might not ready'])
                QMessageBox.about(self, "Connect where to?", "Standa IP is seems invalid!")
                client.clientprintqueue.put(['printme', 'stopping....'])
                self.sock.close()


    def handleClientQueue(self):#TODO when will i arrive here?
        while True:
            if client.clientsendqueue.empty() == False:
                clientsend = client.clientsendqueue.get()
                client.clientsendqueue.task_done()
                string=str(clientsend[0]+clientsend[1])
                if clientsend[0]=="close":
                    self.send(string)
                    break
                self.send(string)
                time.sleep(200)
            else:
                QApplication.processEvents()

    def recv(self):
        while True:
            try:
                data = self.sock.recv(100)
                data = data.decode()
                if not data:
                    client.clientprintqueue.put(
                        ['printme', 'nothing received.\nseems to be an error on server\nnothing '
                                    'received.\nseems to be an error on server\nmight need to call'
                                    ' close socket here?'])
                    self.sock.close()
                    break
                if data[:4] == "POSS":
                    client.clientprintqueue.put(['POSS', data[6:]])
                elif data[:3] == "POS":
                    client.clientprintqueue.put(['POS', data[5:]])
                elif data[:4] == "MOVV":
                    client.clientprintqueue.put(['MOVV', ''])
                elif data[:3] == "MOV":
                    client.clientprintqueue.put(['MOV', ''])
                elif data[:5] == "STATE":
                    client.clientprintqueue.put(['STATE', data[7:]])
                elif data[:4] == "MVRR":
                    client.clientprintqueue.put(['MVRR', ''])
                elif data[:3] == "MVR":
                    client.clientprintqueue.put(['MVR', ''])
                elif data[:3] == "DEH":
                    client.clientprintqueue.put(['DEH', ''])
                elif data[:3] == "SDN":
                    client.clientprintqueue.put(['SDN', ''])
                elif data[:] == "close":
                    client.clientprintqueue.put(['close', 'server client called close!'])
                    self.sock.close()
                elif data[:] == "LMOVE":
                    client.clientprintqueue.put(['LMOVE', ''])
                elif data[:] == "RMOVE":
                    client.clientprintqueue.put(['RMOVE', ''])
                elif data == "STOPMOVE":
                    client.clientprintqueue.put(['STOPMOVE', ''])
                elif data[:4] == "MGET":
                    client.clientprintqueue.put(['MGET', data[6:]])
                elif data[:4] == "MSET":
                    client.clientprintqueue.put(['MSET', data[6:]])
                else:
                    client.clientprintqueue.put(['printme', data])
            except socket.error:
                client.clientprintqueue.put(['printme', 'Error Occured.->closing socket'])
                self.sock.close()
                break

    def send(self, message):
        if self.sock == 0 or self.sock._closed == True:
            client.clientprintqueue.put(['printme', 'no socked, try connect first..'])
        else:
            # Send data
            client.clientprintqueue.put(['printme', 'sending:' + message])
            try:
                if message == "close":
                    client.clientprintqueue.put(['printme', 'closing socket'])
                    message = message.encode()
                    self.sock.sendall(message)
                    self.sock.close()
                else:
                    message = message.encode()
                    self.sock.sendall(message)  # TODO  add case for timeout from server??

            except (ConnectionAbortedError, EOFError):
                client.clientprintqueue.put(
                    ['printme', 'Sending Error: seems to be an error on server->closing socket'])
                self.sock.close()

    def close(self):
        client.clientprintqueue.put(['printme', 'closing socket'])
        self.send("close")


def run():
    # sshshell.paramiko.util.log_to_file("paramikologsall.log")
    app = QApplication(sys.argv)
    GUI = Window()
    GUI._init_()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()

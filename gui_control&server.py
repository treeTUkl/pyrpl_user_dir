from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import *  # QAction, QApplication, QFileDialog, QMessageBox, QWidget,
from PyQt5.QtCore import *
import random
import numpy
import sys
import time
import datetime

from multiprocessing import Process
#from pyrpl import pyrpl
#from pyrpl import sshshell
import start_pyrpl
import threading
import queue
import start_standaclient

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
class readQueue(threading.Thread):
    def __init__(self, GUI):
        threading.Thread.__init__(self)
        timerstart=time.time()
        while GUI.readQueuebool:
            #if isinstance(GUI.standaclient,(Object)):
            if not GUI.standaclient is None:
                if GUI.Standa_Connected==True:

                    if GUI.standaclient.clientprintqueue.empty() == False:
                        clientstatus = GUI.standaclient.clientprintqueue.get()
                        if clientstatus[0] == "printme":
                            string = str(clientstatus[1])
                            GUI.windowprintqueue.put(['printme', string])

                        elif clientstatus[0] == "Standa_Connected_check":
                            mybool = bool(clientstatus[1])
                            GUI.Standa_Connected_check(mybool)
                        elif clientstatus[0] == "MOV":
                            GUI.windowprintqueue.put(['printme', 'Moving via MOV'])

                            GUI.standa_moving_Check(True)
                            #time.sleep(0.5)
                            #client.clientsendqueue.put(['STATE', ""])
                        elif clientstatus[0] == "MOVV":
                            GUI.windowprintqueue.put(['printme', 'Moving via MOVV'])

                            #time.sleep(0.5)
                            GUI.standa_moving = True
                            #client.clientsendqueue.put(['STATE', ""])
                        elif clientstatus[0] == "LMOVE":
                            GUI.windowprintqueue.put(['printme', 'Moving via LMOVE'])
                            GUI.standa_moving_Check(True)
                            #time.sleep(0.5)
                            #client.clientsendqueue.put(['STATE', ""])
                        elif clientstatus[0] == "RMOVE":
                            GUI.windowprintqueue.put(['printme', 'Moving via RMOVE'])

                            GUI.standa_moving_Check(True)
                            #time.sleep(0.5)
                            #client.clientsendqueue.put(['STATE', ""])
                        elif clientstatus[0] == "SDN":
                            GUI.windowprintqueue.put(['printme', 'Got SDN'])

                        elif clientstatus[0] == "DEH":
                            GUI.windowprintqueue.put(['printme', 'Got DEH'])
                            #GUI.standaclient.clientsendqueue.put(['POSS',""])
                            GUI.standaclient.clientsendqueue.put(['STATE',""])

                        elif clientstatus[0] == "MVR":
                            GUI.windowprintqueue.put(['printme', 'Moving via MVR'])

                            GUI.standa_moving_Check(True)
                            #time.sleep(0.5)
                        elif clientstatus[0]== "Mess":
                            GUI.standa_moving_Check(True)
                            GUI.windowprintqueue.put(['printme', 'Moving via AC Messung'])

                            # GUI.Messung_Messpoint(clientstatus[1])
                            # GUI.print_list.addItem('Messpoint Reached!')
                            # GUI.print_list.scrollToBottom()
                        elif clientstatus[0] == "MVRR":
                            GUI.windowprintqueue.put(['printme', 'Moving via MVRR'])

                            GUI.standa_moving_Check(True)
                            #time.sleep(0.5)
                            #client.clientsendqueue.put(['STATE', ""])
                        elif clientstatus[0] == "STOPMOVE":
                            #time.sleep(0.5)
                            #GUI.standa_moving_Check(False)
                            #client.clientsendqueue.put(['STATE', ""])
                            #QApplication.processEvents()
                            #GUI.print_list.addItem('STATE: ' + clientstatus[1])
                            GUI.windowprintqueue.put(['printme', 'Stopmove'])
                            #GUI.print_list.scrollToBottom()
                        elif clientstatus[0] == "STATE":
                            #GUI.windowprintqueue.put(['printme', 'got STATE! '])
                            states = clientstatus[1].split(", ")
                            MoveSts = states[0].split("-> ")
                            MoveSts = MoveSts[1]
                            CurSpeed = states[1].split("-> ")
                            CurSpeed = CurSpeed[1]
                            uCurSpeed = states[2].split("-> ")
                            uCurSpeed = uCurSpeed[1]
                            CurPostiotion=states[3].split("-> ")
                            if not isfloat(CurPostiotion[1]):
                                #SOMETHING WENT WRONG
                                pass
                            CurPostiotion= CurPostiotion[1]
                            uCurPosition= states[4].split("-> ")
                            uCurPosition = uCurPosition[1]
                            asPosition = states[5].split("-> ")
                            asPosition=asPosition[1]
                            while not isfloat(uCurPosition):
                                uCurPosition=uCurPosition[:-1]
                            GUI.Pos_Number.display(CurPostiotion)
                            GUI.uPos_Number.display(uCurPosition)
                            if CurSpeed != "0" or uCurSpeed != "0" or MoveSts != "0":
                                GUI.standa_moving_Check(True)
                                if GUI.run_messung==True:
                                    if GUI.hold_messung == False: #TODO debugg this
                                            GUI.windowprintqueue.put(['printme', 'Still moving to Messpoint'])
                                            GUI.windowprintqueue.put(['printme', 'Now at: ' + str(asPosition)])
                                    elif GUI.hold_messung == True:
                                        GUI.windowprintqueue.put(['printme', "Messung is paused"])
                                        GUI.windowprintqueue.put(['printme', "But Standa is still moving to next Messpoint and will w8 there"])
                                    #GUI.windowprintqueue.put(['printme', "Pos: " + CurPostiotion + '\n'+'uPos: ' + uCurPosition])
                                    #TODO
                            else:
                                result=GUI.standa_moving_Check(False)
                                if result is False:
                                    GUI.windowprintqueue.put(['printme', 'No more Movement!'])

                                else:
                                    time.sleep(0.01)
                                    self.standa_moving = False
                                if GUI.run_messung==True:
                                    if GUI.messung_pos == asPosition:#50000.0

                                        GUI.windowprintqueue.put(['printme', 'Messpoint Reached!'])
                                        GUI.Messung_Messpoint(asPosition)
                                    else:
                                        if GUI.standa_moving_Check() is False:
                                            if GUI.hold_messung is False:
                                                GUI.windowprintqueue.put(['printme', 'Messpoint Missed! Trying again'])
                                                GUI.windowprintqueue.put(['printme', 'Now at: ' + str(asPosition)])
                                                GUI.standaclient.clientsendqueue.put(['Mess', str(GUI.messung_pos)])
                                                GUI.standa_moving_Check(True)

                        #            GUI.windowprintqueue.put(['printme', "couse of State i check POS"])
                        #            GUI.standaclient.clientsendqueue.put(['POS', ""])
                            #GUI.print_list.addItem('STATE: ' + clientstatus[1])
                        # elif clientstatus[0] == "POS":
                        #     if GUI.run_messung == True:
                        #         if GUI.hold_messung ==False:
                        #             if GUI.messung_pos == clientstatus[1]:
                        #                 GUI.windowprintqueue.put(['printme', 'Messpoint Reached!'])
                        #                 GUI.Messung_Messpoint(clientstatus[1])
                        #             else:
                        #                 if GUI.standa_moving_Check()==False:#
                        #                     GUI.windowprintqueue.put(['printme', 'Messpoint Missed! Trying again'])
                        #                     GUI.standaclient.clientsendqueue.put(['Mess', str(GUI.messung_pos)])
                        #                     GUI.standa_moving_Check(True)
                        #                 GUI.windowprintqueue.put(['printme', 'Still moving to Messpoint'])
                        #                 GUI.windowprintqueue.put(['printme', 'Now at: ' + clientstatus[1]])
                        #         elif GUI.hold_messung == True:
                        #             pass
                        #     elif GUI.run_messung == False:
                        #         GUI.standa_moving_Check(False)
                        #         GUI.windowprintqueue.put(['printme', 'Messung stopped!'])
                        #
                        # elif clientstatus[0] == "POSS":
                        #     result = clientstatus[1].split(', ')
                        #     GUI.Pos_Number.display(result[0])
                        #     GUI.uPos_Number.display(result[1])
                        elif clientstatus[0] == "close":
                            GUI.windowprintqueue.put(['printme','this is odd\nserver sended "close" so... closing socket'])
                        elif clientstatus[0] == "received":
                            GUI.windowprintqueue.put(['received: ' + clientstatus[1]])
                        elif clientstatus[0] == "MGET":
                            result = clientstatus[1].split(", ")
                            GUI.get_standa_settings_listWidget.clear()
                            for each in result:
                                GUI.get_standa_settings_listWidget.addItem(str(each) + "\n")
                            MicrosetpValue = result[3]
                            MicrosetpValue = MicrosetpValue[len(MicrosetpValue) - 1:len(MicrosetpValue)]
                            GUI.Microstep_mode_choos_spinBox.setValue(int(MicrosetpValue))
                            GUI.print_list.scrollToBottom()
                        elif clientstatus[0] == "MSET":
                            if clientstatus[1] == "Standa_set_settings worked":
                                GUI.windowprintqueue.put(['printme', str(clientstatus[1])])
                                GUI.standa_get_settings()
                            else:
                                GUI.get_standa_settings_listWidget.clear()
                                GUI.get_standa_settings_listWidget.addItem("Set Settings went wrong!")

                    if GUI.standaclient.clientsendqueue.empty():
                        if GUI.standaclient.clientsendqueue.empty():
                            now = time.time()
                            #if GUI.standa_moving_Check():
                            delta = now - timerstart
                            if GUI.standa_live_control== True:
                                w8time = 3
                            elif GUI.run_messung== True:
                                w8time = 8
                            else:
                                w8time = 10
                                # if GUI.run_messung == True:
                                #     if delta > 3:
                                #         if GUI.hold_messung== False:
                                #             GUI.windowprintqueue.put(['printme', "checking pos"])
                                #             GUI.standaclient.clientsendqueue.put(['POS', ""])
                                #             timerstart = time.time()
                                #         elif GUI.hold_messung == True:
                                #             GUI.windowprintqueue.put(['printme', "Messung is paused"])
                                # else:
                            if delta > w8time:
                                if GUI.hold_messung == False:
                                    #GUI.windowprintqueue.put(['printme',"sendet state0"])
                                    GUI.standaclient.clientsendqueue.put(['STATE', ""])

                                elif GUI.hold_messung == True:
                                    GUI.windowprintqueue.put(['printme', "Messung is paused"])
                                timerstart = time.time()

            if GUI.windowprintqueue.empty() == False:
                while not GUI.windowprintqueue.empty():
                    windowstatus = GUI.windowprintqueue.get()
                    if windowstatus[0] == "printme":
                        string = str(windowstatus[1])
                        GUI.print_list.addItem(string)
                        GUI.print_list.scrollToBottom()

                    GUI.windowprintqueue.task_done()
            if GUI.Standa_Connected == False:
                GUI.Standa_Connected_check(False)

            if GUI.readQueuebool== False:
                break
            QApplication.processEvents()
        print("ReadQueue of GUI died")

class Window(QtWidgets.QMainWindow):
    def _init_(self):
        super(Window, self).__init__()
        self.ui = uic.loadUi("standa_pyrpl_gui.ui", self)
        self.setWindowTitle("PhasenStabi Control")
        self.setWindowIcon(QtGui.QIcon('pulse.png'))
        self.ac_messung = False
        self.run_messung = False
        self.hold_messung = False
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

        self.holdMessung_pushButton.clicked.connect(self.hold_Messung)#TODO
        self.nextStep_pushButton.clicked.connect(self.skip_Messpoint)#TODO
        self.Clear_list_Button.clicked.connect(self.clear_list)
        self.Load_list_Button.clicked.connect(self.ListFilePicker)
        self.Save_list_Button.clicked.connect(self.ListFileSaver)
        self.select_file_Button.clicked.connect(self.Ac_File_Picker)
        self.Sort_list_Button.clicked.connect(self.sort_list)
        self.reverse_List_checkBox.clicked.connect(self.sort_list)

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


        self.move_relative_Button_2.clicked.connect(self.standa_move_relative)
        self.standa_moving_Check_radioButton.setAutoExclusive(False)
        self.readQueuebool=True
        self.show()

        readQueue(self).start()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Nachricht', "Soll die Anwendung geschlossen werden?",QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
            self.close_application()
        else:
            event.ignore()


    def sort_list(self):
        if not self.run_messung:

            state = self.reverse_List_checkBox.isChecked()
            if state==True: state=False
            else: state=True
            numbers = []
            for x in range(self.step_list.count()):
                numbers.append(float(self.step_list.item(x).text()))
            numbers.sort(reverse=state)
            self.step_list.clear()
            for x in numbers:
                self.step_list.addItem(str(x))
        else:
            self.windowprintqueue.put(['printme', 'Cant mod List while running measurement'])

    def ListFilePicker(self):
        if not self.run_messung:
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
        else:
            self.windowprintqueue.put(['printme', 'Cant mod List while running measurement'])

    def Ac_File_Picker(self):
        if not self.run_messung:
            name, _ = QFileDialog.getSaveFileName(self, 'Save File', options=QFileDialog.DontUseNativeDialog)
            if name == "":
                return False
            else:
                if not name[len(name) - 4:] == '.xml':
                    name = name + str('.xml')
                self.filePath_Edit.setText(str(name))
                return True
        else:
            self.windowprintqueue.put(['printme', 'Cant mod ACFile while running measurement'])

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
        name = self.filePath_Edit.text()
        if name == "":
            QMessageBox.about(self, "Select Ac_File", "Ac_File is missing. Choose or create File first")
            self.ac_checkBox.setChecked(True)
        else:
            self.windowprintqueue.put(['printme', 'AC Messung Started'])
            self.run_messung = True
            self.hide_messung_controls_widget.hide()
            self.completed=0
            self.standa_live_control_stop()
            time.sleep(0.1)
            self.messung(None)
    def skip_Messpoint(self):
        self.windowprintqueue.put(['printme', 'Messpoint skipped'])
        self.messung(True)

    def hold_Messung(self):
        if self.hold_messung is False:
            self.hold_messung= True
            self.holdMessung_pushButton.setText("continue")
            self.windowprintqueue.put(['printme', 'pausing Messung'])
            self.standaclient.clientsendqueue.put(['STOPMOVE', ''])
        elif self.hold_messung is True:
            self.hold_messung=False
            self.holdMessung_pushButton.setText("Pause")
            self.windowprintqueue.put(['printme', 'continue Messung'])

    def Messung_Messpoint(self, aspos):
        self.completed += self.complete
        self.progressBar.setValue(self.completed)
        if self.run_messung is True:
            if self.ac_messung:
                input = self.pyrpl_input_choice()
                self.pyrpl_voltage=0
                for i in range(20):
                    if input == 1:

                        voltage = self.pyrpl_p.get_voltage("a1")
                    elif input == 2:
                        voltage = self.pyrpl_p.get_voltage("a2")
                    else:
                        voltage = random.random()
                        self.windowprintqueue.put(['printme', 'No pyrpl input generating randoms'])
                    self.pyrpl_voltage=self.pyrpl_voltage + voltage

                self.pyrpl_voltage=self.pyrpl_voltage/20#TODO WARUM /20 ?
                print_voltage= "{:10.8f}".format(self.pyrpl_voltage)#TODO debugg its only 1 value!!!!
                self.windowprintqueue.put(['printme', 'Pyrpl Voltage: '+ str(print_voltage)])
                text = str(aspos) + str('\t') + str('\t') + print_voltage + str('\t') + str('\t') + str(time.asctime()) + str('\n')
                if self.file.closed is False:
                    self.file.write(text)
            if self.Stabitest_checkBox.isChecked() is True:
                self.messung(None)
            else:
                self.messung(True)


    def messung(self, state =None):
        if self.run_messung is False:
            state = False

        if state is  None:
            name = self.filePath_Edit.text()
            if name == "":
                QMessageBox.about(self, "Select Ac_File", "Ac_File is missing. Something went wrong please cancel manualy")
            else:
                self.file = open(name, 'a')
                text = 'Postition in as' + str('\t') + str('\t') + 'Voltage' + str('\t') + str('\t') + 'Time' +str('\n')
                self.file.write(text)

            self.ac_messung = self.ac_checkBox.isChecked()
            self.completed = 0
            self.complete = 1 / self.step_list.count() * 100


            #if not self.standaclient == False & self.Standa_Connected == True:
            if self.Standa_Connected is True:
                if self.pyrpl_p is not None:
                    if self.pyrpl_Connected_check():
                        self.curstep=0
                        if self.run_messung:
                            xitem = self.step_list.item(self.curstep).text()

                            self.windowprintqueue.put(['printme', 'Putting in First Step: '+ str(xitem)])
                            self.standaclient.clientsendqueue.put(['Mess', str(xitem)])
                            #time.sleep(0.2)
                            self.messung_pos=xitem
                            self.standa_moving_Check(True)
                    else:
                        QMessageBox.about(self, "No active Pyrpl", "Connect to Pyrpl first!")
                        self.run_messung=False
                        self.windowprintqueue.put(['printme', 'Connect to pyrpl first\n'])
                else:
                    QMessageBox.about(self, "No active connection to Pyrpl", "Connect to Pyrpl first!")
                    self.run_messung=False
                    self.windowprintqueue.put(
                        ['printme', 'Connect to pyrpl first\n'])
            else:
                QMessageBox.about(self, "No Standa Server", "Connect to Standa first!")
                self.progressBar.setValue(0)
                self.windowprintqueue.put(
                    ['printme', 'Connect to Standa first\nStanda_Connected is ' + str(self.Standa_Connected)])
                self.run_messung = False

        elif state is False:
            self.windowprintqueue.put(['printme', 'Messung Canceled'])
            self.progressBar.setValue(0)
            text = str('\n') + 'Messung Canceled\n' +str(time.asctime())
            if self.file.closed is False:
                self.file.write(text)
                self.file.close()

        elif state is True:
            self.curstep=self.curstep+1
            if self.Standa_Connected is True:
                if self.pyrpl_p is not None:
                    if self.pyrpl_Connected_check():
                        if self.run_messung:
                            if self.curstep== self.step_list.count():
                                self.print_list.addItem(str('Messung Done'))
                                self.print_list.scrollToBottom()
                                self.progressBar.setValue(100)
                                text = str('\n') + 'Messung finished\n' + str(time.asctime())
                                self.standa_live_control = False
                                if self.file.closed is False:
                                    self.file.write(text)
                                    self.file.close()
                                self.run_messung = False

                            else:
                                xitem = self.step_list.item(self.curstep).text()

                                self.windowprintqueue.put(['printme', 'Putting in next Step: ' + str(xitem)])
                                self.standaclient.clientsendqueue.put(['Mess', str(xitem)])
                                self.standa_moving_Check(True)
                                self.messung_pos = xitem

                else:
                    QMessageBox.about(self, "No active Pyrpl", "Connect to Pyrpl first!")
                    self.progressBar.setValue(0)
                    self.run_messung=False
            else:
                QMessageBox.about(self, "No Standa Server", "Connect to Standa first!")
                self.progressBar.setValue(0)
                self.windowprintqueue.put(
                    ['printme', 'Connect to Standa first\nStanda_Connected is ' + str(self.Standa_Connected)])
                self.run_messung=False

    def stop_messung(self):
        self.hold_messung = False
        self.run_messung = False
        self.progressBar.setValue(0)
        if self.Standa_Connected is True:
            self.standaclient.clientsendqueue.put(['STOPMOVE', ''])
            self.standaclient.clientsendqueue.put(['ClearList', ''])
        self.hide_messung_controls_widget.show()
        self.messung(False)
        self.messung_pos = False

    def add_to_list(self):#TODO von 10 to 0 in schirtten hinzufügen nicht möglich!
        if not self.run_messung:
            start = self.Start_SpinBox.value()
            end = self.End_SpinBox.value()
            stepsize = self.Stepsize_SpinBox.value()
            if stepsize == 0.0:
                pass
            else:
                #if end < start:
                 #   x = start
                  #  start = end
                   # end = x
                for x in numpy.arange(start, end + stepsize, stepsize):
                    value = str(x)
                    self.step_list.addItem(value)
        else:
            self.windowprintqueue.put(['printme', 'Cant mod List while running measurement'])

    def clear_list(self):
        if self.run_messung:
            self.windowprintqueue.put(['printme', 'Cant mod List while running measurement'])
        else:
            self.step_list.clear()

    def close_application(self):
        print("whooaaaa so custom!!!")
        self.Standa_Close_Connection_to_Server()
        self.readQueuebool = False
        QApplication.processEvents()
        sys.exit()

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # aus standa&pyrpl_client.py
    #    pyrplclient = client('localhost', 54545)  # pyrpl_server läuft local auf dem selben rechner.
    # diodenmessung(pyrplclient, 'bnc1')
    # diodenmessung(pyrplclient, 'bnc2')
    # pyrplclient.close()
    #   standaclient= client('127.127.127.2', 22222)#standa_server über ssh auf redpitaya
    def Standa_Connect_to_Server(self):
        if self.standaclient is False:
            standa_ip = self.standa_connection_ip.text()
            standa_port = self.standa_connection_port.text()
            if standa_ip == "":
                QMessageBox.about(self, "Connect where to?", "Standa IP is missing. Trying to connect to localhost")
                standa_ip = '127.0.0.1'
                standa_port = 54545
            if standa_port == "":
                QMessageBox.about(self, "Connect where to?", "Standa Port is missing")
                self.Standa_Connected_check(False)
                return False
            else:
                #while self.Standa_Connected== False:
                    self.windowprintqueue.put(['printme', "Connect to Standa_Server via:\n" + str(standa_ip) + ", " + str(standa_port)])
                    self.standaclient = start_standaclient.client(standa_ip, standa_port, GUI=self)
                    if self.Standa_Connected is True:
                        pass#break
                    else:
                        self.standa_live_control_stop()
                        self.standaclient = False
                        self.standa_live_control = False
                        self.Standa_Connected_check(False)
                        self.windowprintqueue.put(['printme', 'Connection failed!'])
                        self.Standa_Close_Connection_to_Server()

    def Standa_Connected_check(self, state=None):
        if state is None:
            return self.Standa_Connected
        elif state is True:
            self.Standa_Connected = True
            self.Standa_Connected_label.setAutoFillBackground(True)
            self.Standa_Connected_label.setStyleSheet("background-color:#10ff00;")
        elif state is False:
            self.Standa_Connected = False
            self.Standa_Connected_label.setStyleSheet("background-color:#ff0000;")
            self.Standa_Connected_label.setAutoFillBackground(False)
            self.standa_live_control = False

    def Standa_Close_Connection_to_Server(self):
        self.windowprintqueue.put(['printme', 'Closing Standa Socked & connection\n'])
        if not self.standaclient is False:
            self.standa_live_control_stop()
            self.standaclient.close()
            self.standaclient = False
            #self.standa_live_control = False
            self.Standa_Connected_check(False)
        elif self.Standa_Connected is True:
            self.Standa_Connected_check(True)

    def standa_check(self):
        if self.Standa_Connected_check():
            if not self.standaclient is False:
                return True
            else:
                return False
        else:
            return False

    def standa_live_control_start(self):  # TODO the live control should be running in an thread
        if self.standa_check():
            self.standa_live_control = True
            self.Standa_live_control_widget.hide()
            self.standa_pos()
        if self.StandaWidget.currentIndex() == 0:
            #self.standa_handling()
            pass

    def standa_handling(self):#TODO this not needed? cause readQuee will handle
        # if self.standa_live_control == False:
        #     self.standa_live_control_stop()
        # if self.StandaWidget.currentIndex() == 1:
        #     self.standaclient.clientsendqueue.put(['STOPMOVE', ''])
        pass

    def standa_move_relative(self):
        if self.standa_check():
            self.standaclient.clientsendqueue.put(['MVRR', str(self.Pos_spinBox.value()) + ', ' + str(self.uPos_spinBox.value())])
            time.sleep(0.3)

    def standa_live_control_stop(self):

        if self.standa_check():
            self.standaclient.clientsendqueue.put(['STOPMOVE', ''])
            self.Standa_live_control_widget.show()
            self.Pos_Number.display('NaN')
            self.uPos_Number.display('NaN')
            self.standa_live_control = False

    def standa_pos(self):
        if self.standa_check():
            #self.standaclient.clientsendqueue.put(['POSS', ''])
            self.standaclient.clientsendqueue.put(['STATE', ''])
        else:
            self.Pos_Number.display('NaN')
            self.uPos_Number.display('NaN')

    def standa_right(self):
        if self.standa_check() & self.standa_live_control:
            self.standaclient.clientsendqueue.put(['RMOVE', ''])
            time.sleep(0.3)

    def standa_left(self):
        if self.standa_check() & self.standa_live_control:
            self.standaclient.clientsendqueue.put(['LMOVE', ''])
            time.sleep(0.3)

    def standa_stop(self):
        if self.standa_check() & self.standa_live_control:
            self.standaclient.clientsendqueue.put(['STOPMOVE', ''])

    def standa_move_to(self):
        if self.standa_check() & self.standa_live_control:
            self.standaclient.clientsendqueue.put(['MOVV', str(self.Pos_spinBox.value()) + ', ' + str(self.uPos_spinBox.value())])
            time.sleep(0.3)

    def standa_go_home(self):
        if self.standa_check() & self.standa_live_control:
            self.standaclient.clientsendqueue.put(['MOVV', "0" + ', ' + "0"])
            time.sleep(0.3)

    def standa_set_home(self):
        if self.standa_check() & self.standa_live_control:
            self.standaclient.clientsendqueue.put(['DEH', ''])
            time.sleep(0.3)

    def standa_get_settings(self):
        if self.standa_check() & self.standa_live_control:
            self.standa_stop()
            time.sleep(0.3)
            self.standaclient.clientsendqueue.put(['MGET', ''])

    def standa_set_settings(self):
        if self.standa_check() & self.standa_live_control:
            self.standa_stop()
            time.sleep(0.03)
            send = str(self.Motor_Speed_spinBox.value())
            send = send + ", " + str(self.Acceleration_spinBox.value())
            send = send + ", " + str(self.Deceleration_spinBox.value())
            send = send + ", " + str(self.Microstep_mode_choos_spinBox.value())
            self.standaclient.clientsendqueue.put(['MSET', send])
            time.sleep(0.03)
            self.standa_get_settings()

    def standa_moving_Check(self, state=None):
        if state is None:
            if self.standa_moving:
                state = True
            else:
                state = False
        if state is True:
            self.standa_moving_Check_radioButton.setAutoRepeat(True)
            self.standa_moving_Check_radioButton.setAutoFillBackground(True)
            self.standa_moving_Check_radioButton.setStyleSheet("QRadioButton::indicator {background-color:#32CC99;border: 2px solid white;}")
            self.standa_moving = True
        elif state is False:
            self.standa_moving = False
            self.standa_moving_Check_radioButton.setAutoRepeat(False)
            self.standa_moving_Check_radioButton.setAutoFillBackground(True)
            self.standa_moving_Check_radioButton.setStyleSheet("QRadioButton::indicator {background-color:white; border:2px solid white;}")
        return self.standa_moving

    def Microstep_changed(self):
        MicrosetpValue = (2 ** self.Microstep_mode_choos_spinBox.value()) / 2
        self.Microstep_mode_choos_LineEdit.setText(str(int(MicrosetpValue)))

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # aus pyrpl start.py

    def pyrpl_prozess_fn(self):
        if self.pyrpl_Connected:
            self.windowprintqueue.put(['printme', 'pyrpl Voltage'])
            self.pyrpl_voltage = self.pyrpl_p.get_voltage("a1")
            self.windowprintqueue.put(['printme', 'pyrpl Voltage1: ' + str(self.pyrpl_voltage)])
            self.Volt1.display(self.pyrpl_voltage)
            self.pyrpl_voltage = self.pyrpl_p.get_voltage("a2")
            self.windowprintqueue.put(['printme', 'pyrpl Voltage2: ' + str(self.pyrpl_voltage)])
            self.Volt2.display(self.pyrpl_voltage)

    def pyrpl_Connected_check(self, state=None):
        if state is None:
            return self.pyrpl_Connected
        elif state is True:
            self.pyrpl_Connected = True
            self.Pyrpl_Started_label.setAutoFillBackground(True)
            self.Pyrpl_Started_label.setStyleSheet("background-color:#10ff00;")
        elif state is False:
            self.pyrpl_Connected = False
            self.Pyrpl_Started_label.setStyleSheet("background-color:#ff0000;")
            self.Pyrpl_Started_label.setAutoFillBackground(False)
            self.standa_live_control = False

    def clean_pyrpl(self):
        if self.pyrpl_Connected:
            self.windowprintqueue.put(['printme', 'close Pyrpl'])
            self.pyrpl_p.stop_pyrpl()
            self.pyrpl_p = None
            self.pyrpl_Connected_check(False)
            self.print_list.scrollToBottom()

    def pyrpl_input_choice(self):
        if self.pyrpl_input1.isChecked():
            return 1
        if self.pyrpl_input2.isChecked():
            return 2

    def pyrpl_start(self):# TODO: Info aus Console in Textbox übertragen
        QMessageBox.about(self, "Pyrpl Info",
                          "Starting Pyrpl\nThis might take a while (up to 1min)")

        self.windowprintqueue.put(['printme', 'Starting Pyrpl\nThis might take a while (up to 1min)'])
        QApplication.processEvents()
       #pyrplThread= threading.Thread(target=start_pyrpl.pyrpl_p)
       # pyrplProcess= Process(target=start_pyrpl.pyrpl_p)
        self.pyrpl_p = start_pyrpl.pyrpl_p()
        result = self.pyrpl_p.start()
        #result=pyrplThread.run()
        #result=pyrplProcess.run()

        self.pyrpl_Connected_check(result)
        if result is True:
            self.windowprintqueue.put(['printme', 'Pyrpl started !\n'])
        else:
            self.windowprintqueue.put(['printme', 'Something went wrong with pyrpl'])

def run():
    app = QApplication(sys.argv)
    GUI = Window()
    GUI._init_()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()

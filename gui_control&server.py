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
class readQueue(threading.Thread):
    def __init__(self, GUI):
        threading.Thread.__init__(self)
        timerstart=time.time()
        while GUI.readQueuebool:
            if isinstance(GUI.standaclient,(client)):

                if GUI.Standa_Connected==True:

                    if client.clientprintqueue.empty() == False:
                        clientstatus = client.clientprintqueue.get()
                        if clientstatus[0] == "printme":
                            string = str(clientstatus[1])
                            GUI.print_list.addItem(string)
                            GUI.print_list.scrollToBottom()
                        elif clientstatus[0] == "Standa_Connected_check":
                            mybool = bool(clientstatus[1])
                            GUI.Standa_Connected_check(mybool)
                        elif clientstatus[0] == "MOV":
                            GUI.print_list.addItem('Moving via MOV')
                            GUI.print_list.scrollToBottom()
                            GUI.standa_moving_Check(True)
                            #time.sleep(0.5)
                            #client.clientsendqueue.put(['STATE', ""])
                        elif clientstatus[0] == "MOVV":
                            GUI.print_list.addItem('Moving via MOVV')
                            GUI.print_list.scrollToBottom()
                            #time.sleep(0.5)
                            GUI.standa_moving = True
                            #client.clientsendqueue.put(['STATE', ""])
                        elif clientstatus[0] == "LMOVE":
                            GUI.print_list.addItem('Moving via LMOVE')
                            GUI.print_list.scrollToBottom()
                            GUI.standa_moving_Check(True)
                            #time.sleep(0.5)
                            #client.clientsendqueue.put(['STATE', ""])
                        elif clientstatus[0] == "RMOVE":
                            GUI.print_list.addItem('Moving via RMOVE')
                            GUI.print_list.scrollToBottom()
                            GUI.standa_moving_Check(True)
                            #time.sleep(0.5)
                            #client.clientsendqueue.put(['STATE', ""])
                        elif clientstatus[0] == "SDN":
                            GUI.print_list.addItem('Got SDN')
                            GUI.print_list.scrollToBottom()
                        elif clientstatus[0] == "DEH":
                            GUI.print_list.addItem('Got DEH')
                            GUI.print_list.scrollToBottom()
                            client.clientsendqueue.put(['POSS',""])
                        elif clientstatus[0] == "MVR":
                            GUI.print_list.addItem('Moving via MVR')
                            GUI.print_list.scrollToBottom()
                            GUI.standa_moving_Check(True)
                            #time.sleep(0.5)
                        elif clientstatus[0]== "Mess":
                            GUI.standa_moving_Check(True)
                            GUI.print_list.addItem('Moving via AC Messung')
                            GUI.print_list.scrollToBottom()
                            # GUI.Messung_Messpoint(clientstatus[1])
                            # GUI.print_list.addItem('Messpoint Reached!')
                            # GUI.print_list.scrollToBottom()
                        elif clientstatus[0] == "MVRR":
                            GUI.print_list.addItem('Moving via MVRR')
                            GUI.print_list.scrollToBottom()
                            GUI.standa_moving_Check(True)
                            #time.sleep(0.5)
                            #client.clientsendqueue.put(['STATE', ""])
                        elif clientstatus[0] == "STOPMOVE":
                            #time.sleep(0.5)
                            #GUI.standa_moving_Check(False)
                            #client.clientsendqueue.put(['STATE', ""])
                            #QApplication.processEvents()
                            #GUI.print_list.addItem('STATE: ' + clientstatus[1])
                            GUI.print_list.addItem('Stopmove')
                            #GUI.print_list.scrollToBottom()
                        elif clientstatus[0] == "STATE":

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
                            while not isfloat(uCurPosition):
                                uCurPosition=uCurPosition[:-1]
                            GUI.Pos_Number.display(CurPostiotion)
                            GUI.uPos_Number.display(uCurPosition)
                            if CurSpeed != "0" or uCurSpeed != "0" or MoveSts != "0":
                                GUI.standa_moving_Check(True)
                                if GUI.run_messung==True:
                                    GUI.print_list.addItem("Pos: " + CurPostiotion + '\n'+'uPos: ' + uCurPosition)
                            else:
                                GUI.standa_moving_Check(False)
                                if GUI.run_messung==True:
                                    client.clientsendqueue.put(['POS', ""])
                            #GUI.print_list.addItem('STATE: ' + clientstatus[1])
                            GUI.print_list.addItem('STATE: ')
                            GUI.print_list.scrollToBottom()
                        elif clientstatus[0] == "POS":
                            if GUI.run_messung == True:
                                if GUI.messung_pos == clientstatus[1]:
                                    GUI.print_list.addItem('Messpoint Reached!')
                                    GUI.print_list.scrollToBottom()
                                    GUI.Messung_Messpoint(clientstatus[1])
                                else:
                                    GUI.print_list.addItem('Messpoint Missed! Trying again')
                                    client.clientsendqueue.put(['Mess', str(GUI.messung_pos)])
                                    GUI.standa_moving_Check(True)
                        elif clientstatus[0] == "POSS":
                            result = clientstatus[1].split(', ')
                            GUI.Pos_Number.display(result[0])
                            GUI.uPos_Number.display(result[1])
                        elif clientstatus[0] == "close":
                            GUI.print_list.addItem('this is odd\nserver sended "close"\nso... closing socket')
                            GUI.print_list.scrollToBottom()
                        elif clientstatus[0] == "received":
                            GUI.print_list.addItem('received: ' + clientstatus[1])
                            GUI.print_list.scrollToBottom()
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
                                GUI.print_list.addItem(str(clientstatus[1]))
                                GUI.print_list.scrollToBottom()
                                GUI.standa_get_settings()
                            else:
                                GUI.get_standa_settings_listWidget.clear()
                                GUI.get_standa_settings_listWidget.addItem("Set Settings went wrong!")

                    if client.clientsendqueue.empty():
                        if GUI.standa_moving_Check():
                            now = time.time()
                            delta = now - timerstart
                            if delta >5:
                                if GUI.run_messung == True:
                                    client.clientsendqueue.put(['POS', ""])
                                else:
                                    client.clientsendqueue.put(['STATE', ""])
                                timerstart=time.time()


            if GUI.windowprintqueue.empty() == False:
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


        self.move_relative_Button_2.clicked.connect(self.standa_move_relative)  # TODO
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
                if not name[len(name) - 3:] == 'xml':
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
            self.messung(None)

    def standa_moving_Check(self, bool=None):
        if bool is None:
            if self.standa_moving:
                bool=True
            else:
                bool =False
        if bool is True:
            self.standa_moving_Check_radioButton.setAutoRepeat(True)
            self.standa_moving_Check_radioButton.setAutoFillBackground(True)
            self.standa_moving_Check_radioButton.setStyleSheet("QRadioButton::indicator {background-color:#32CC99;border: 2px solid white;}")
            self.standa_moving = True
        elif bool is False:
            self.standa_moving = False
            self.standa_moving_Check_radioButton.setAutoRepeat(False)
            self.standa_moving_Check_radioButton.setAutoFillBackground(True)
            self.standa_moving_Check_radioButton.setStyleSheet("QRadioButton::indicator {background-color:white; border:2px solid white;}")
        return self.standa_moving

    def Messung_Messpoint(self, aspos):
        self.completed += self.complete
        self.progressBar.setValue(self.completed)
        if self.run_messung==True:
            if self.ac_messung:
                input = self.pyrpl_input_choice()
                self.pyrpl_voltage=0
                for i in range(20):
                    if input == 1:
                        voltage = self.pyrpl_p.rp.scope.voltage_in1
                    elif input == 2:
                        voltage = self.pyrpl_p.rp.scope.voltage_in2
                    else:
                        voltage = random.random()
                        self.windowprintqueue.put(['printme', 'No pyrpl input generating randoms'])
                    self.pyrpl_voltage=self.pyrpl_voltage + voltage

                self.pyrpl_voltage=self.pyrpl_voltage/20
                text = str(aspos) + str('\t') + str('\t') + str(self.pyrpl_voltage) + str('\n')
                if self.file.closed == False:
                    self.file.write(text)
            self.messung(True)

    def messung(self, bool =None):#TODO needs to be rewritten to be able to get MOV pos reached -> now take voltage
        if self.run_messung==False:
            bool=False

        if bool == None:
            name = self.filePath_Edit.text()
            if name == "":
                QMessageBox.about(self, "Select Ac_File", "Ac_File is missing. Something went wrong please cancel manualy")
            else:
                self.file = open(name, 'a')
                text = 'Postition in as' + str('\t') + str('\t') + 'Voltage' + str('\n')
                self.file.write(text)

            self.ac_messung = self.ac_checkBox.isChecked()
            self.completed = 0
            self.complete = 1 / self.step_list.count() * 100

            #if not self.standaclient == False & self.Standa_Connected == True:
            if self.Standa_Connected == True:
                if self.pyrpl_p is not None:
                    if self.pyrpl_Connected_check():
                        self.curstep=0
                        if self.run_messung:
                            xitem = self.step_list.item(self.curstep).text()
                            self.windowprintqueue.put(['printme', 'Putting in First Step: '+ str(xitem)])
                            client.clientsendqueue.put(['Mess', str(xitem)])
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

        elif bool == False:#TODO the new state "Mess" in ximcServer" could get messy if canceled in between debugg this
            self.windowprintqueue.put(['printme', 'Messung Canceled'])
            self.progressBar.setValue(0)
            text = str('\n') + 'Messung Canceled\n'
            if self.file.closed == False:
                self.file.write(text)
                self.file.close()

        elif bool == True:
            self.curstep=self.curstep+1
            if self.Standa_Connected == True:
                if self.pyrpl_p is not None:
                    if self.pyrpl_Connected_check():
                        if self.run_messung:
                            if self.curstep== self.step_list.count():
                                self.print_list.addItem(str('Messung Done'))
                                self.print_list.scrollToBottom()
                                self.progressBar.setValue(100)
                                text = str('\n') + 'Messung finished\n'
                                self.standa_live_control = False
                                if self.file.closed==False:
                                    self.file.write(text)
                                    self.file.close()
                                self.run_messung = False

                            else:
                                xitem = self.step_list.item(self.curstep).text()
                                client.clientsendqueue.put(['Mess', str(xitem)])  # TODO  bisher gibts kein send queue
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
        self.run_messung = False
        self.progressBar.setValue(0)


        #self.messung(False)#TODO ? might needed?

    def add_to_list(self):
        if not self.run_messung:
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
        self.readQueuebool=False
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
                #while self.Standa_Connected== False:
                    self.windowprintqueue.put(['printme', "Connect to Standa_Server via:\n" + str(standa_ip) + ", " + str(standa_port)])
                    self.standaclient = client(standa_ip, standa_port, GUI=self)
                    #self.standaclient.start()#TODO needed here?
                    if self.Standa_Connected== True:
                        pass#break
                    else:
                        self.standa_live_control_stop()
                        self.standaclient = False
                        self.standa_live_control = False
                        self.Standa_Connected_check(False)
                        self.windowprintqueue.put(['printme', 'Connection failed!'])
                        # msg = QtWidgets.QMessageBox()
                        # msg.setWindowTitle('Connection Refused!')
                        # msg.setText("Do you want to try again?")
                        # msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                        # buttonReply = msg.exec_()
                        # if buttonReply == QMessageBox.Yes:
                        #     self.windowprintqueue.put(['printme', 'then, keep runnig.'])
                        #     self.standaclient = client(standa_ip, standa_port, GUI=self)
                        #     self.standaclient.start()  # TODO
                        # else:
                        #     self.windowprintqueue.put(['printme', 'stopping....'])
                        #     self.Standa_Connected == False
                        #     break


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


    def Standa_Close_Connection_to_Server(self):#TODO how is works?
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
            #self.standa_handling()
            pass


    def standa_handling(self):#TODO this not needed? cause readQuee will handle
        if self.standa_live_control == False:
            self.standa_live_control_stop()
        if self.StandaWidget.currentIndex() == 1:
            client.clientsendqueue.put(['STOPMOVE', ''])


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
            client.clientsendqueue.put(['MOVV', str(self.Pos_spinBox.value()) + ', ' + str(self.uPos_spinBox.value())])

    def standa_go_home(self):
        if self.standa_check() & self.standa_live_control:
            client.clientsendqueue.put(['MOVV', "0" + ', ' + "0"])

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
            time.sleep(0.03)
            send = str(self.Motor_Speed_spinBox.value())
            send = send + ", " + str(self.Acceleration_spinBox.value())
            send = send + ", " + str(self.Deceleration_spinBox.value())
            send = send + ", " + str(self.Microstep_mode_choos_spinBox.value())
            client.clientsendqueue.put(['MSET', send])
            time.sleep(0.03)
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

    def pyrpl_start(self):# TODO: Info aus Console in Textbox übertragen
        QMessageBox.about(self, "Pyrpl Info",
                          "Starting Pyrpl\nThis might take a while (up to 1min)")

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
            self.pyrpl_p=None
        finally:
            if not self.pyrpl_p is None:
                self.pyrpl_Connected_check(True)
                self.windowprintqueue.put(['printme', 'Pyrpl started !\n'])
            else:
                self.pyrpl_Connected_check(False)


class client(threading.Thread):
    #clientsendqueue = queue.Queue()
    #clientprintqueue = queue.Queue()
    def __init__(self, host, port, GUI):
        threading.Thread.__init__(self)
        self.sock = 0
        self.HOST = host
        self.PORT = int(port)
        self.GUI = GUI
        self.stopconnect = False
        self.connect()

    def connect(self):
        if self.sock == 0 or self.sock._closed == True:
            # HOST = 'localhost'
            # PORT = 54545
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                self.sock.connect((self.HOST, self.PORT))
                #client.clientprintqueue.put(['printme', 'connected to server'])#ToDO befor that the queue should be empty
                #client.clientprintqueue.put(['Standa_Connected_check', True])
                #client.clientsendqueue.put(["POSS", ""])

            except ConnectionRefusedError:
                self.GUI.windowprintqueue.put(['printme', 'Connection Refused! Server might not ready'])
                self.GUI.windowprintqueue.put(["printme", "Code to start on rp-f053d1:\n"
                                                          "cd /root/ximc/ximc-2.9.8\npython3 ximcServer.py"])
                self.GUI.standa_live_control = False
                self.GUI.Standa_Connected_check(False)
                self.GUI.standaclient = False
                self.stopconnect =True

            except OSError:
                self.GUI.windowprintqueue.put(['printme', 'Connection Refused! Server might not ready'])
                #self.QMessageBox.about(self, "Connect where to?", "Standa IP is seems invalid!")
                self.GUI.windowprintqueue.put(['printme', 'stopping....'])
                self.stopconnect = True
            finally:
                if self.stopconnect == False:
                    client.clientsendqueue = queue.Queue()
                    client.clientprintqueue = queue.Queue()
                    client.clientprintqueue.put(['printme', 'connected to server'])#ToDO befor that the queue should be empty
                    client.clientprintqueue.put(['Standa_Connected_check', True])
                    client.clientsendqueue.put(["STATE", ""])
                    self.GUI.Standa_Connected = True
                    self.handleThread=threading.Thread(target=self.handleClientQueue).start()
                    self.recvThread=threading.Thread(target=self.recv).start()
                else:
                    self.sock.close()


    def handleClientQueue(self):#TODO when will i arrive here?

        while True:
            if client.clientsendqueue.empty() == False:

                clientsend = client.clientsendqueue.get()

                string=str(clientsend[0]+clientsend[1])
                if clientsend[0]=="cclose":
                    break
                else:
                    if clientsend[0]=="close":
                        self.send(string)
                        break
                    self.send(string)
                    string=""
                    #time.sleep(0.03)
                client.clientsendqueue.task_done()
        print("handleClientQueue died")


    def recv(self):
        t = threading.currentThread()
        buff=""
        while getattr(t, "do_run", True):
            try:

                data = self.sock.recv(150)

                data = data.decode()
                if not data:
                    client.clientprintqueue.put(
                        ['printme', 'nothing received.\nseems to be an error on server\nnothing '
                                    'received.\nseems to be an error on server\nmight need to call'
                                    ' close socket here?'])
                    self.sock.close()
                    break
                if not data[:2] == "!+":
                    datasplit = data.split("+!")
                    data = datasplit[0]
                    data = buff + data
                    #datalist.append(data)
                    buff = datasplit[1]
                else:
                    datasplit = data.split("+!")
                    data = datasplit[0]
                    buff=datasplit[1]

                data = data[2:]

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
                    break
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
                elif data[:4] == "Mess":
                    client.clientprintqueue.put(['Mess', ""])
                    #client.clientprintqueue.put(['Mess', data[6:]])
                else:
                    client.clientprintqueue.put(['printme', data])

            except socket.error:
                client.clientprintqueue.put(['printme', 'Error Occured.->closing socket'])
                self.sock.close()
                client.clientprintqueue.put(['cclose', ""])
                break
        if not client.clientsendqueue.empty():
            while not client.clientsendqueue.empty():
                try:
                    client.clientsendqueue.get(False)
                except Empty:
                    continue
                client.clientsendqueue.task_done()
        client.clientprintqueue.put(['cclose', ""])

        self.sock.close()
        self.GUI.Standa_Connected = False
        print("clientprintqueue died")


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
                else:
                    message = message.encode()
                    self.sock.sendall(message)  # TODO  add case for timeout from server??

            except (ConnectionAbortedError, EOFError, AttributeError):
                client.clientprintqueue.put(
                    ['printme', 'Sending Error: seems to be an error on server->closing socket'])
                self.sock.close()

    def close(self):
        client.clientprintqueue.put(['printme', 'closing socket'])
        client.clientsendqueue.put(['close',""])
        #self.send("close")


def run():
    # sshshell.paramiko.util.log_to_file("paramikologsall.log")
    app = QApplication(sys.argv)
    GUI = Window()
    GUI._init_()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()

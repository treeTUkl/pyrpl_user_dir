from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QAction, QApplication, QFileDialog, QMessageBox
import random
import numpy
import sys
import time
import socket


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
        self.Standa_Connected_checkBox.setChecked(False)
        self.standa_live_control = False
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
        self.Standa_Connected_checkBox.stateChanged.connect(self.standa_check)
        self.standa_live_control_ButtonBox.accepted.connect(self.standa_live_control_start)
        self.standa_live_control_ButtonBox.rejected.connect(self.standa_live_control_stop)
        self.Go_right_Button.clicked.connect(self.standa_right)
        self.Stop_Button.clicked.connect(self.standa_stop)
        self.Go_left_Button.clicked.connect(self.standa_left)
        self.move_to_Button.clicked.connect(self.standa_move_to)
        self.Go_Home_Button.clicked.connect(self.standa_go_home)
        self.SetHome_Button.clicked.connect(self.standa_set_home)
        self.show()

    def sort_list(self):
        numbers = []
        for x in range(self.step_list.count()):
            numbers.append(float(self.step_list.item(x).text()))
        numbers.sort()
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

    def messung(self):
        name = self.filePath_Edit.text()
        if name == "":
            pass
        else:
            file = open(name, 'a')
            text = 'Postition in as' + str('\t') + 'Voltage' + str('\n')
            file.write(text)

        self.ac_messung = self.ac_checkBox.isChecked()
        self.completed = 0
        self.complete = 1 / self.step_list.count() * 100
        for self.x in range(self.step_list.count()):
            if self.run_messung:
                xitem = self.step_list.item(self.x).text()
                step = 'MOV' + xitem
                # standa_result=standaclient.send(step)#wie bekomm ich den Standa Client hier rein?
                # TODO: no standaclient lets just print the items from the list
                standa_result = xitem
                self.completed += self.complete
                self.progressBar.setValue(self.completed)
                self.print_list.addItem('POS' + standa_result)
                self.print_list.scrollToBottom()
                time.sleep(0.5)  # TODO just debugging delete me then done
                QApplication.processEvents()
                if self.ac_messung:
                    # result=diodenmessung(pyrplclient, 'bnc2')#wie bekomm ich den pyrpl Client hier rein?
                    # TODO: no pyrpl Client lets just print randoms
                    pyrpl_result = random.random()
                    text = str(standa_result) + str('\t') + str(pyrpl_result)
                    text = text + str('\n')
                    if not name == "":
                        file.write(text)

                if self.x == self.step_list.count() - 1:
                    self.messung_finished()
                    text = str('\n') + 'Messung finished\n'
                    if not name == "":
                        file.write(text)

            else:
                self.print_list.addItem(str('Canceled'))
                self.print_list.scrollToBottom()
                self.progressBar.setValue(0)
                text = str('\n') + 'Messung Canceled\n'
                if not name == "":
                    file.write(text)
                break

        if not name == "":
            file.close()

    def messung_finished(self):
        self.print_list.addItem(str('Messung Done'))

    def stop_messung(self):
        self.run_messung = False

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
        sys.exit()

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # aus standa&pyrpl_client.py
    #    pyrplclient = client('localhost', 54545)  # pyrpl_server läuft local auf dem selben rechner.
    # diodenmessung(pyrplclient, 'bnc1')
    # diodenmessung(pyrplclient, 'bnc2')
    # pyrplclient.close()
    #   standaclient= client('127.127.127.2', 22222)#standa_server über ssh auf redpitaya
    def Standa_Connect_to_Server(self):
        standa_ip = self.standa_connection_ip.text()
        standa_port = self.standa_connection_port.text()#TODO str? int? what?
        if standa_ip == "":
            QMessageBox.about(self, "Connect where to?", "Standa IP is missing. Trying to connect to localhost")
        if standa_port == "":
            QMessageBox.about(self, "Connect where to?", "Standa Port is missing")
            self.Standa_Connected_checkBox.setChecked(False)
            return False
        else:
            self.print_list.addItem("Connect to Standa_Server via:\n" + str(standa_ip) + ", " + str(standa_port))
            self.print_list.scrollToBottom()
            self.standaclient = client(standa_ip, standa_port)
            if self.standa_check():
                self.standa_pos(self)

    def Standa_Close_Connection_to_Server(self):
        if not self.standaclient == False:
            self.standaclient.close()
            self.standaclient = False
            self.Standa_Connected_checkBox.setChecked(False)

    def standa_check(self):
        if self.Standa_Connected_checkBox.isChecked():
            if not self.standaclient == False:
                return True
            else:
                return False
        else:
            return False

    def standa_live_control_start(self):
        if self.standa_check():
            self.standa_live_control = True
            self.Standa_live_control_widget.hide()
            while self.standa_live_control:
                QApplication.processEvents()
                self.standa_pos()
                QApplication.processEvents()
                if self.standa_live_control == False:
                    self.standa_live_control_stop()
                    break

    def standa_live_control_stop(self):
        if self.standa_check():
            result = self.standaclient.send("STOPMOVE")
            self.print_list.addItem(str(result))
            self.standa_live_control = False
            self.Standa_live_control_widget.show()
            self.Pos_Number.display('NaN')
            self.uPos_Number.display('NaN')

    def standa_pos(self):
        if self.standa_check():
            result = self.standaclient.send("POSS")
            result.split(', ')
            self.Pos_Number.display(float(result[0]))
            self.uPos_Number.display(float(result[0]))
        else:
            self.Pos_Number.display('NaN')
            self.uPos_Number.display('NaN')

    def standa_right(self):
        if self.standa_check() & self.standa_live_control:
            result = self.standaclient.send("RMOVE")
            self.print_list.addItem(str(result))

    def standa_left(self):
        if self.standa_check() & self.standa_live_control:
            result = self.standaclient.send("LMOVE")
            self.print_list.addItem(str(result))

    def standa_stop(self):
        if self.standa_check() & self.standa_live_control:
            result = self.standaclient.send("STOPMOVE")
            self.print_list.addItem(str(result))

    def standa_move_to(self):
        Window.QMessageBox.about(self, "not working", "yet..")  # TODO: add this

    def standa_go_home(self):
        if self.standa_check() & self.standa_live_control:
            result = self.standaclient.send("GOH")
            self.print_list.addItem(str(result))

    def standa_set_home(self):
        if self.standa_check() & self.standa_live_control:
            result = self.standaclient.send("DEH")
            self.print_list.addItem(str(result))


class client(object):#TODO: how to integreate client into the window-gui to make gui accessable through the client?
    def __init__(self, host, port):
        self.sock = 0
        #self.HOST = host
        #self.PORT = int(port)
        self.HOST = '127.0.0.1'
        #self.HOST = 'localhost'#TODO:why wont localhost dont work? got str but int excpected
        self.PORT = 54545
        self.connect()

    def connect(self):
        if self.sock == 0:
            # HOST = 'localhost'
            # PORT = 54545
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # self.sock.setblocking(0)
                self.sock.connect((self.HOST, self.PORT))
                object.print_list.addItem('connected to server')
                object.self.Standa_Connected_checkBox.setChecked(True)

            except ConnectionRefusedError:
                object.print_list.addItem('Connection Refused! Server might not ready')
                buttonReply = object.QMessageBox.question(self, 'Connection Refused!', "Do you want to try again?",
                                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if buttonReply == QMessageBox.Yes:  # TODO or is it Window.QMessageBox.Yes?
                    object.print_list.addItem("then, keep runnig.")
                    self.sock = 0
                    self.connect()
                else:
                    object.print_list.addItem("stopping....")
                    self.sock.close()

    def send(self, message):
        if self.sock == 0:
            object.print_list.addItem('no socked, try connect first..')
            object.QMessageBox.about(self, "no socked", "try connect first..")
        else:
            # Send data
            object.print_list.addItem('sending:' + message)
            message = message.encode()
            self.sock.sendall(message)
            message = message.decode()
            # reciveing
            if not message == "close":
                data = self.sock.recv(16)
                data = data.decode()
                object.print_list.addItem('received: ', data)

            elif message == " ":
                object.print_list.addItem('nothing received.\nseems to be an error on server')
                self.sock.close()

            elif message == "close":
                object.print_list.addItem('\nclosing socket')
                self.sock.close()
            return data

    def close(self):
        object.print_list.addItem('closing socket')
        self.send("close")


def diodenmessung(pyrplclient, bnc1o2):
    volt = False
    if bnc1o2 == "bnc1":
        volt = "voltage1"
    elif bnc1o2 == "bnc2":
        volt = "voltage2"
    else:
        print("\nKein gültiger Anschluß am redpitaya gewählt! Wählen Sie bnc1 oder bnc1")
        return False
    if not volt:
        print('\nSpannungsmessung an: ' + bnc1o2)
        diodendata = 0.0
        for i in range(10):
            diodendata = diodendata + pyrplclient.send(volt)
            time.sleep(.5)
        return diodendata / 10


def run():
    app = QApplication(sys.argv)
    GUI = Window()
    GUI._init_()
    sys.exit(app.exec_())
    #infoBox.exec_()


if __name__ == "__main__":
    run()

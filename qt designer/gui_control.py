from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QAction, QApplication, QFileDialog
import random
import numpy
import sys
import time


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
                #TODO: no standaclient lets just print the items from the list
                standa_result = xitem
                self.completed += self.complete
                self.progressBar.setValue(self.completed)
                self.print_list.addItem('POS' + standa_result)
                self.print_list.scrollToBottom()
                time.sleep(0.5)#TODO just debugging delete me then done
                QApplication.processEvents()
                if self.ac_messung:
                    # result=diodenmessung(pyrplclient, 'bnc2')#wie bekomm ich den pyrpl Client hier rein?
                    #TODO: no pyrpl Client lets just print randoms
                    pyrpl_result = random.random()
                    text = str(standa_result) + str('\t') + str(pyrpl_result)
                    text = text + str('\n')
                    if not name == "":
                        file.write(text)


                if self.x == self.step_list.count()-1:
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
        sys.exit()


def run():
    app = QApplication(sys.argv)
    GUI = Window()
    GUI._init_()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()

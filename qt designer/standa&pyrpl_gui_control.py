from PyQt5 import QtWidgets, uic, Qt
import numpy
import sys

app = QtWidgets.QApplication([])
dlg = uic.loadUi("standa_pyrpl_gui.ui")


def add_to_list():

    start = dlg.Start_SpinBox.value()
    end = dlg.End_SpinBox.value()
    stepsize = dlg.Stepsize_SpinBox.value()
    if stepsize == 0.0:
        pass
    else:
        if end<start:
            x=start
            start=end
            end=x
        for x in numpy.arange(start, end+stepsize, stepsize):
            value = str(x)
            dlg.step_list.addItem(value)

def clear_list():
    dlg.step_list.clear()
    
#TODO: dont know how to do files
"""def file_open():
    name = QtGui.QfileDialog.getOpenFileName()
    """
#TODO: dont know how to do events
"""def delete_list_item(event):
    if event.key() == Qt.QKeyEvent(key=QEvent::KeyPress,  ) Key_Delete:
        for x in range(dlg.step_list.selectedItems()):
            dlg.step_list.takeItem(x)
"""

#dlg.step_list.setSortingEnabled(True)
dlg.Add_to_list_Button.clicked.connect(add_to_list)
dlg.Clear_list_Button.clicked.connect(clear_list)

dlg.show()
app.exec()
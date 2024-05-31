# @Time  : 2024/4/16 17:22
# @Filename : main.py
from qgis.PyQt import QtCore
from qgis.core import QgsApplication
from PyQt5.QtCore import Qt
import os
import traceback
from mainWindow import MainWindow
from CartoGrapher_dialog_base import Ui_CartoGraphDialogBase



if __name__ == '__main__':

    QgsApplication.setPrefixPath('D:/QGIS/apps/qgis', True)
    QgsApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QgsApplication([], True)
    app.initQgis()
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()
    app.exitQgis()


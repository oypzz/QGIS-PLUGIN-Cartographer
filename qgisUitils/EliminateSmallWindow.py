# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EliminateSmallWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_EliminateSmall(object):
    def setupUi(self, EliminateSmall):
        EliminateSmall.setObjectName("EliminateSmall")
        EliminateSmall.resize(693, 533)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plugin/resources/m.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        EliminateSmall.setWindowIcon(icon)
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(EliminateSmall)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(431, 1, 251, 431))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.textEdit_2 = QtWidgets.QTextEdit(self.horizontalLayoutWidget_2)
        self.textEdit_2.setObjectName("textEdit_2")
        self.horizontalLayout_3.addWidget(self.textEdit_2)
        self.cancelBtn = QtWidgets.QPushButton(EliminateSmall)
        self.cancelBtn.setGeometry(QtCore.QRect(551, 451, 93, 28))
        self.cancelBtn.setObjectName("cancelBtn")
        self.runBtn = QtWidgets.QPushButton(EliminateSmall)
        self.runBtn.setGeometry(QtCore.QRect(241, 491, 93, 28))
        self.runBtn.setObjectName("runBtn")
        self.progressBar = QtWidgets.QProgressBar(EliminateSmall)
        self.progressBar.setGeometry(QtCore.QRect(71, 451, 471, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setOrientation(QtCore.Qt.Vertical)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setTextDirection(QtWidgets.QProgressBar.BottomToTop)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayoutWidget = QtWidgets.QWidget(EliminateSmall)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 431, 431))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tabWidget_2 = QtWidgets.QTabWidget(self.horizontalLayoutWidget)
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.Parameters_2 = QtWidgets.QWidget()
        self.Parameters_2.setObjectName("Parameters_2")
        self.label_5 = QtWidgets.QLabel(self.Parameters_2)
        self.label_5.setGeometry(QtCore.QRect(20, 10, 171, 16))
        self.label_5.setObjectName("label_5")
        self.mapLayerComboBox_2 = QgsMapLayerComboBox(self.Parameters_2)
        self.mapLayerComboBox_2.setGeometry(QtCore.QRect(20, 40, 201, 27))
        self.mapLayerComboBox_2.setShowCrs(True)
        self.mapLayerComboBox_2.setObjectName("mapLayerComboBox_2")
        self.select_checkBox_2 = QtWidgets.QCheckBox(self.Parameters_2)
        self.select_checkBox_2.setGeometry(QtCore.QRect(20, 80, 211, 31))
        self.select_checkBox_2.setObjectName("select_checkBox_2")
        self.label_6 = QtWidgets.QLabel(self.Parameters_2)
        self.label_6.setGeometry(QtCore.QRect(20, 120, 171, 16))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.Parameters_2)
        self.label_7.setGeometry(QtCore.QRect(20, 290, 91, 16))
        self.label_7.setObjectName("label_7")
        self.output_FileWidget_2 = QgsFileWidget(self.Parameters_2)
        self.output_FileWidget_2.setGeometry(QtCore.QRect(20, 310, 321, 27))
        self.output_FileWidget_2.setObjectName("output_FileWidget_2")
        self.output_checkBox_2 = QtWidgets.QCheckBox(self.Parameters_2)
        self.output_checkBox_2.setGeometry(QtCore.QRect(20, 350, 351, 19))
        self.output_checkBox_2.setChecked(True)
        self.output_checkBox_2.setObjectName("output_checkBox_2")
        self.threshold_Edit = QtWidgets.QLineEdit(self.Parameters_2)
        self.threshold_Edit.setGeometry(QtCore.QRect(20, 150, 291, 31))
        self.threshold_Edit.setObjectName("threshold_Edit")
        self.eliminateComboBox = QtWidgets.QComboBox(self.Parameters_2)
        self.eliminateComboBox.setGeometry(QtCore.QRect(20, 230, 271, 22))
        self.eliminateComboBox.setObjectName("eliminateComboBox")
        self.eliminateComboBox.addItem("")
        self.eliminateComboBox.addItem("")
        self.eliminateComboBox.addItem("")
        self.label_8 = QtWidgets.QLabel(self.Parameters_2)
        self.label_8.setGeometry(QtCore.QRect(20, 200, 191, 16))
        self.label_8.setObjectName("label_8")
        self.tabWidget_2.addTab(self.Parameters_2, "")
        self.Log_2 = QtWidgets.QWidget()
        self.Log_2.setObjectName("Log_2")
        self.tabWidget_2.addTab(self.Log_2, "")
        self.horizontalLayout_4.addWidget(self.tabWidget_2)
        self.closeBtn = QtWidgets.QPushButton(EliminateSmall)
        self.closeBtn.setGeometry(QtCore.QRect(361, 491, 93, 28))
        self.closeBtn.setObjectName("closeBtn")

        self.retranslateUi(EliminateSmall)
        self.tabWidget_2.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(EliminateSmall)

    def retranslateUi(self, EliminateSmall):
        _translate = QtCore.QCoreApplication.translate
        EliminateSmall.setWindowTitle(_translate("EliminateSmall", "Eliminate Small Polygons"))
        self.textEdit_2.setHtml(_translate("EliminateSmall", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Eliminate Small Polygons</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This algorithm is used to eliminate too small polygons to keep map beautiful, basically including three methods: </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">     Generalization directly: eliminate polygons that satisfy the elimination threshold;</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">     Generalized to the adjacent polygons that have the largest area;</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">     Generalize to the adjacent polygons that have the longest boundary</p></body></html>"))
        self.cancelBtn.setText(_translate("EliminateSmall", "Cancel"))
        self.runBtn.setText(_translate("EliminateSmall", "运行"))
        self.label_5.setText(_translate("EliminateSmall", "Input layer or shp"))
        self.select_checkBox_2.setText(_translate("EliminateSmall", "Selected features only"))
        self.label_6.setText(_translate("EliminateSmall", "Eliminate threshold:"))
        self.label_7.setText(_translate("EliminateSmall", "Eliminated"))
        self.output_checkBox_2.setText(_translate("EliminateSmall", "Open output file after running algorithm"))
        self.eliminateComboBox.setItemText(0, _translate("EliminateSmall", "generalization directly"))
        self.eliminateComboBox.setItemText(1, _translate("EliminateSmall", "generalized to the largest area"))
        self.eliminateComboBox.setItemText(2, _translate("EliminateSmall", "generalized to the largest common boudary"))
        self.label_8.setText(_translate("EliminateSmall", "Eliminate selection:"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.Parameters_2), _translate("EliminateSmall", "Parameters"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.Log_2), _translate("EliminateSmall", "Log"))
        self.closeBtn.setText(_translate("EliminateSmall", "关闭"))
from qgsfilewidget import QgsFileWidget
from qgsmaplayercombobox import QgsMapLayerComboBox
# import resources_rc
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SetlabelDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LabelDialog(object):
    def setupUi(self, LabelDialog):
        LabelDialog.setObjectName("LabelDialog")
        LabelDialog.resize(364, 367)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plugins/CartoGrapher/resources/m.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        LabelDialog.setWindowIcon(icon)
        self.layerCbmBox = QgsMapLayerComboBox(LabelDialog)
        self.layerCbmBox.setGeometry(QtCore.QRect(10, 50, 231, 27))
        self.layerCbmBox.setObjectName("layerCbmBox")
        self.label_5 = QtWidgets.QLabel(LabelDialog)
        self.label_5.setGeometry(QtCore.QRect(10, 20, 171, 16))
        self.label_5.setObjectName("label_5")
        self.FieldCmbBox = QgsFieldComboBox(LabelDialog)
        self.FieldCmbBox.setGeometry(QtCore.QRect(10, 140, 231, 27))
        self.FieldCmbBox.setObjectName("FieldCmbBox")
        self.label_6 = QtWidgets.QLabel(LabelDialog)
        self.label_6.setGeometry(QtCore.QRect(10, 110, 171, 16))
        self.label_6.setObjectName("label_6")
        self.mFontButton = QgsFontButton(LabelDialog)
        self.mFontButton.setGeometry(QtCore.QRect(10, 220, 240, 31))
        self.mFontButton.setObjectName("mFontButton")
        self.label_7 = QtWidgets.QLabel(LabelDialog)
        self.label_7.setGeometry(QtCore.QRect(10, 190, 171, 16))
        self.label_7.setObjectName("label_7")
        self.closeBtn = QtWidgets.QPushButton(LabelDialog)
        self.closeBtn.setGeometry(QtCore.QRect(180, 300, 93, 28))
        self.closeBtn.setAutoDefault(False)
        self.closeBtn.setObjectName("closeBtn")
        self.runBtn = QtWidgets.QPushButton(LabelDialog)
        self.runBtn.setGeometry(QtCore.QRect(60, 300, 93, 28))
        self.runBtn.setDefault(True)
        self.runBtn.setObjectName("runBtn")

        self.retranslateUi(LabelDialog)
        QtCore.QMetaObject.connectSlotsByName(LabelDialog)

    def retranslateUi(self, LabelDialog):
        _translate = QtCore.QCoreApplication.translate
        LabelDialog.setWindowTitle(_translate("LabelDialog", "Set label"))
        self.label_5.setText(_translate("LabelDialog", "Labelling layer:"))
        self.label_6.setText(_translate("LabelDialog", "Set label field:"))
        self.label_7.setText(_translate("LabelDialog", "Set label font:"))
        self.closeBtn.setText(_translate("LabelDialog", "关闭"))
        self.runBtn.setText(_translate("LabelDialog", "运行"))
from qgsfieldcombobox import QgsFieldComboBox
from qgsfontbutton import QgsFontButton
from qgsmaplayercombobox import QgsMapLayerComboBox
# import resources_rc

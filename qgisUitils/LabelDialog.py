# @Time  : 2024/5/23 19:12
# @Filename : LabelDialog.py

import os
# import pydevd_pycharm
import qgis
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog, QAction
from qgis._core import QgsProject, QgsMapLayer, QgsWkbTypes, Qgis, QgsVectorLayer, QgsPalLayerSettings, \
    QgsVectorLayerSimpleLabeling
from qgis.gui import QgisInterface
from .SetlabelDialog import Ui_LabelDialog
from .generalizer import Smoother
from .test.test_exaggerate import exaggerate
from .LayerUtils import readVectorFile

PROJECT = QgsProject.instance()
class SetlabelWindow(QDialog, Ui_LabelDialog):
    def __init__(self,layer,parent=None):
        super(SetlabelWindow,self).__init__()
        self.setupUi(self)
        self.layer: QgsVectorLayer = layer
        # self.iface = qgis.gui.QgisInterface
        self.parentWindow = parent
        self.initUI()
        self.connFunc()

    def initUI(self):
        """This function initialize  the window"""

        self.layerCbmBox.layerChanged.connect(self.FieldCmbBox.setLayer)

        self.mFontButton.setLayer(self.layer)  # 将控件与图层连接

    def connFunc(self):
        """This function controls the widgets interaction"""

        self.runBtn.clicked.connect(self.SetLabel)
        self.closeBtn.clicked.connect(self.exitWindow)

    def SetLabel(self):
        """label text setting"""

        layer_settings = QgsPalLayerSettings()
        text_format = self.mFontButton.textFormat()

        # text_format.setFont(QFont("Arial", 12))
        # text_format.setSize(12)

        # buffer_settings = QgsTextBufferSettings()
        # buffer_settings.setEnabled(True)
        # buffer_settings.setSize(1)
        # buffer_settings.setColor(QColor("white"))

        # text_format.setBuffer(buffer_settings)
        layer_settings.setFormat(text_format)

        layer_settings.fieldName = self.FieldCmbBox.currentField()
        # layer_settings.placement = 2

        layer_settings.enabled = True

        layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
        self.layer.setLabelsEnabled(True)
        self.layer.setLabeling(layer_settings)
        self.layer.triggerRepaint()

    def exitWindow(self):
        """This function is used to close the processing window"""
        self.close()
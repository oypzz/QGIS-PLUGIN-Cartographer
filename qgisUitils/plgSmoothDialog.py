# @Time  : 2024/5/23 10:43
# @Filename : plgSmoothDialog.py

import os
# import pydevd_pycharm
import qgis
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog, QAction
from qgis._core import QgsProject, QgsMapLayer, QgsWkbTypes, Qgis, QgsVectorLayer
from qgis.gui import QgisInterface
from .SmoothDialog import Ui_SmoothDialog
from .test.test_chaikin import Smooth
from .LayerUtils import readVectorFile
from .test.test_exaggerate import exaggerate

PROJECT = QgsProject.instance()
class polygonSmoothWindow(QDialog, Ui_SmoothDialog):
    def __init__(self,layer,iface,parent=None):
        super(polygonSmoothWindow,self).__init__()
        self.setupUi(self)
        self.layer: QgsVectorLayer = layer
        # self.iface = qgis.gui.QgisInterface
        self.parentWindow = parent
        self.iface = iface
        self.initUI()
        self.connFunc()

    def initUI(self):
        """This function initialize  the window"""
        self.edit_iteration.setText('3')
        self.output_file.setStorageMode(3)
        self.output_file.setFilePath('')

    def connFunc(self):
        """This function controls the widgets interaction"""
        self.runBtn.clicked.connect(self.SmoothPolygons)
        self.closeBtn.clicked.connect(self.exitWindow)

    def SmoothPolygons(self):
        layer: QgsVectorLayer = self.layerCbmBox.currentLayer()
        inputFile = layer.source()
        output_temp = self.output_file.filePath() + "_temp.shp"
        outputFile = self.get_outFile()
        # FIDS = layer.selectedFeatureIds()
        # new_FIDS = [FID + 2 for FID in FIDS]
        new_FIDS = list(range(366))
        num  = float(self.edit_iteration.text())
        exa_scale = 1.0000005
        # if len(layer.selectedFeatureIds()) == 0:
        #     QMessageBox.warning(self,'Parameter error','Please select at least one feature!')
        # else:
        Smooth(inputFile,output_temp,num,new_FIDS)
        exaggerate(output_temp, outputFile, exa_scale, new_FIDS)
        self.exitWindow()
        if self.output_checkBox_2.isChecked():
            myIface = MyIface()
            myIface.addVectorLayer(outputFile, layer.name() + "_smoothed:", "ogr")
            QMessageBox.information(self, 'Processing result', 'Smooth is finished!', QMessageBox.Ok)

    def exitWindow(self):
        """This function is used to close the processing window"""
        self.close()

    def get_outFile(self):
        """This function is to make sure the file has a .shp suffix"""
        file_dir = self.output_file.filePath()
        file_name = file_dir.split('\\')[-1]
        if len(file_name.split('.')) == 2 and file_name.split('.')[-1] == 'shp':
            return file_dir
        else:
            return file_dir + '.shp'



def addVectorLayer(uri, provider, name):
    vl = QgsVectorLayer(uri, name, provider)
    QgsProject.instance().addMapLayer(vl)
    return vl, name

class MyIface(QgisInterface):
    def __init__(self):
        QgisInterface.__init__(self)

    def addVectorLayer(self, path, name, provider):
        return addVectorLayer(path, provider, name)
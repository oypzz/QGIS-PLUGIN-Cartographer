# @Time  : 2024/5/23 11:03
# @Filename : plgExaggerateDialog.py

import os
# import pydevd_pycharm
import qgis
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog, QAction
from qgis._core import QgsProject, QgsMapLayer, QgsWkbTypes, Qgis, QgsVectorLayer
from qgis.gui import QgisInterface
from .ExaggerateDialog import Ui_ExaggerateDialog
from .generalizer import Smoother
from .test.test_exaggerate import exaggerate
from .LayerUtils import readVectorFile

PROJECT = QgsProject.instance()
class polygonExaggerateWindow(QDialog, Ui_ExaggerateDialog):
    def __init__(self,layer,parent=None):
        super(polygonExaggerateWindow,self).__init__()
        self.setupUi(self)
        self.layer: QgsVectorLayer = layer
        # self.iface = qgis.gui.QgisInterface
        self.parentWindow = parent
        self.initUI()
        self.connFunc()

    def initUI(self):
        """This function initialize  the window"""

        self.edit_scale.setText('1.005')
        self.output_file.setStorageMode(3)
        self.output_file.setFilePath('')

    def connFunc(self):
        """This function controls the widgets interaction"""
        self.runBtn.clicked.connect(self.ExaggeratePolygons)
        self.closeBtn.clicked.connect(self.exitWindow)

    def ExaggeratePolygons(self):
        layer: QgsVectorLayer = self.layerCbmBox.currentLayer()
        inputFile = layer.source()
        outputFile = self.get_outFile()
        exa_scale = float(self.edit_scale.text())
        if len(layer.selectedFeatureIds()) == 0:
            QMessageBox.warning(self,'Parameter error','Please select at least one feature!')
        else:
            FIDS = layer.selectedFeatureIds()
            new_FIDS = [FID + 2 for FID in FIDS]
            # FIDS = [345]
            # pydevd_pycharm.settrace('localhost', port=53111, stdoutToServer=True, stderrToServer=True)
            exaggerate(inputFile,outputFile,exa_scale,new_FIDS)
            self.exitWindow()
            if self.output_checkBox_2.isChecked():
                myIface = MyIface()
                myIface.addVectorLayer(outputFile, layer.name() + "_exaggerated:", "ogr")
                QMessageBox.information(self,'Processing result','Exaggeration is finished!',QMessageBox.Ok)



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
# @Time  : 2024/5/6 18:57
# @Filename : plgSimplifyDialog.py

import os
# import pydevd_pycharm
import qgis
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog, QAction
from qgis._core import QgsProject, QgsMapLayer, QgsWkbTypes, Qgis, QgsVectorLayer, QgsProcessingParameterField, \
    QgsProcessingFeedback, QgsProcessingContext, QgsFeature, QgsProcessingFeatureSourceDefinition, QgsFeatureRequest
from qgis import processing
from datetime import datetime
from qgis.gui import QgisInterface
from .SimplifyWindow import Ui_SimplifyWindow
from .LayerUtils import readVectorFile
from .test.test_dp import Douglas
from .test.test_visvalingam import Visvalingam

PROJECT = QgsProject.instance()
class polygonSimplifyWindow(QDialog, Ui_SimplifyWindow):
    def __init__(self,layer,parent=None):
        super(polygonSimplifyWindow,self).__init__()
        self.setupUi(self)
        self.layer: QgsVectorLayer = layer
        # self.iface = qgis.gui.QgisInterface
        self.parentWindow = parent
        self.initUI()
        self.connFunc()

    def initUI(self):
        """This function initialize  the window"""
        self.simplifyComboBox.setText = 'Simplification selections'
        self.output_FileWidget_3.setStorageMode(3)
        self.output_FileWidget_3.setFilePath('')

    def connFunc(self):
        """This function controls the widgets interaction"""
        self.runBtn.clicked.connect(self.SimplifyPolygons)
        self.closeBtn.clicked.connect(self.exitWindow)
        self.cancelBtn.clicked.connect(self.cancel_processing)


    def SimplifyPolygons(self):
        """The main function to realize the simplification processing """

        layer: QgsVectorLayer = self.mapLayerComboBox_3.currentLayer()
        if not layer:
            QMessageBox.warning(self,'Parameter error','Please put in vector layer!')
        source = layer.source()
        out_put = self.get_outFile()
        tolerance = self.tolerance_doubleSpinBox.value()
        #0-douglas 1-Visvalingam
        sim_type = self.simplifyComboBox.currentIndex()
        input_layer = QgsProcessingFeatureSourceDefinition(source,
                                                           selectedFeaturesOnly=True,
                                                           featureLimit=-1,
                                                        geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid)
        if self.select_checkBox_3.isChecked() and len(layer.selectedFeatureIds()) > 0:
            if sim_type == 0:
                self.progressBar.setValue(0)
                time_sta = datetime.now()
                runner = processing.run("native:simplifygeometries", {
                    'INPUT': input_layer,
                    'METHOD': 0,
                    'TOLERANCE':tolerance,
                    'OUTPUT': out_put
                })
                self.progressBar.setValue(100)
                time_end = datetime.now()
                print('delta_time:', time_end - time_sta)
            elif sim_type == 1:
                self.progressBar.setValue(0)
                time_sta = datetime.now()
                runner = processing.run("native:simplifygeometries", {
                    'INPUT': input_layer,
                    'METHOD': 2,
                    'TOLERANCE':tolerance,
                    'OUTPUT': out_put
                })
                self.progressBar.setValue(100)
                time_end = datetime.now()
                print('delta_time:', time_end - time_sta)
        elif not self.select_checkBox_3.isChecked() and sim_type == 0:
            self.progressBar.setValue(0)
            time_sta = datetime.now()
            # pydevd_pycharm.settrace('localhost', port=53111, stdoutToServer=True, stderrToServer=True)
            Douglas(source,out_put,tolerance)
            self.progressBar.setValue(100)
            time_end = datetime.now()
            print('Code running sim-01')
            print('delta_time:', time_end - time_sta)
        elif not self.select_checkBox_3.isChecked() and sim_type == 1:
            self.progressBar.setValue(0)
            time_sta = datetime.now()
            Visvalingam(source,out_put,tolerance)
            self.progressBar.setValue(100)
            time_end = datetime.now()
            print('delta_time:', time_end - time_sta)
        else:
            QMessageBox.warning(self,'Parameter error','Please select target feature(s)!')

        if self.output_checkBox_3.isChecked() :
           myIface = MyIface()
           myIface.addVectorLayer(out_put, layer.name()+"_simplified:", "ogr")
            # self.iface.addVectorLayer(output, layer.name()+"_generalized:", "ogr")


    def exitWindow(self):
        """This function is used to close the processing window"""
        self.close()

    def get_outFile(self):
        """This function is to make sure the file has a .shp suffix"""
        file_dir = self.output_FileWidget_3.filePath()
        file_name = file_dir.split('\\')[-1]
        if len(file_name.split('.')) == 2 and file_name.split('.')[-1] == 'shp':
            return file_dir
        else:
            return file_dir + '.shp'

    def cancel_processing(self):
        """When the cancel btn is clicked, the processing progress stops"""
        self.progressBar.setValue(0)
        if self.output_FileWidget_3.filePath() != '':
            file = self.output_FileWidget_3.filePath()
            print(file)
            filename = file.split('.')[0]
            # filename = filename.split('.')[0]
            # pydevd_pycharm.settrace('localhost', port=53100, stdoutToServer=True, stderrToServer=True)
            remove_filename = filename + '.dbf'
            print(remove_filename)
            os.remove(filename + '.dbf')
            os.remove(filename + '.prj')
            os.remove(filename + '.cpg')
            os.remove(filename + '.shx')
            os.remove(filename + '.shp')
            QMessageBox.warning(self, 'Cancel dialog', 'The processing progress has been stopped')
        else:
            QMessageBox.warning(self, 'warning', 'There is something wrong')

def addVectorLayer(uri, provider, name):
    vl = QgsVectorLayer(uri, name, provider)
    QgsProject.instance().addMapLayer(vl)
    return vl, name

class MyIface(QgisInterface):
    def __init__(self):
        QgisInterface.__init__(self)

    def addVectorLayer(self, path, name, provider):
        return addVectorLayer(path, provider, name)
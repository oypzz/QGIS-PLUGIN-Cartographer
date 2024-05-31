# @Time  : 2024/5/6 9:31
# @Filename : plgEliminateDialog.py

import os
# import pydevd_pycharm
import qgis
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog, QAction
from qgis._core import QgsProject, QgsMapLayer, QgsWkbTypes, Qgis, QgsVectorLayer, QgsProcessingParameterField, \
    QgsProcessingFeedback, QgsProcessingContext, QgsFeature, QgsProcessingFeatureSourceDefinition, QgsFeatureRequest
from qgis import processing
from datetime import datetime
from qgis.gui import QgisInterface
from .EliminateSmallWindow import Ui_EliminateSmall
from .LayerUtils import readVectorFile

PROJECT = QgsProject.instance()
class polygonEliminateWindow(QDialog, Ui_EliminateSmall):
    def __init__(self,layer,parent=None):
        super(polygonEliminateWindow,self).__init__()
        self.setupUi(self)
        self.layer: QgsVectorLayer = layer
        # self.iface = qgis.gui.QgisInterface
        self.parentWindow = parent
        self.initUI()
        self.connFunc()

    def initUI(self):
        """This function initialize  the window"""
        self.eliminateComboBox.setText = 'Elimination selections'
        self.output_FileWidget_2.setStorageMode(3)
        self.output_FileWidget_2.setFilePath('')

    def connFunc(self):
        """This function controls the widgets interaction"""
        self.runBtn.clicked.connect(self.EliminatePolygons)
        self.closeBtn.clicked.connect(self.exitWindow)
        self.cancelBtn.clicked.connect(self.cancel_processing)
        self.select_checkBox_2.clicked.connect(self.setReadOnly)

    def EliminatePolygons(self):
        """Main function to realize the elimination """
        layer: QgsVectorLayer = self.mapLayerComboBox_2.currentLayer()
        source = layer.source()
        out_put = self.get_outFile()
        #0-直接消除 1-合并到最大面积 2-合并到最长边界
        eli_type = self.eliminateComboBox.currentIndex() #当前选中的处理方式
        #这部分判断并选中要处理的多边形要素
        if len(layer.selectedFeatureIds()) != 0 and self.select_checkBox_2.isChecked(): #只处理当前选中的图层
            print("The code is running here")
            feat = layer.selectedFeatures()
        elif not self.select_checkBox_2.isChecked() and self.threshold_Edit.text() != '': #未勾选既按照阈值进行处理
           threshold = float(self.threshold_Edit.text())  # 获取输入的处理阈值
           layer.removeSelection()  # 取消当前图层的选中
           feat = layer.selectByExpression(f'"面积" <= {threshold}')
        elif not self.select_checkBox_2.isChecked() and self.threshold_Edit.text() == '': #既不勾选，也没有填阈值
            QMessageBox.warning(self,'Parameter error','Please enter the processing threshold!')
        input_layer = QgsProcessingFeatureSourceDefinition(source,
                                                           selectedFeaturesOnly=True,
                                                           featureLimit=-1,
                                                           geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid)
        if eli_type == 0: #选择直接消除多边形
            layer: QgsVectorLayer = self.mapLayerComboBox_2.currentLayer()
            self.progressBar.setValue(0)
            print(layer.selectedFeatureIds())
            runner = processing.run("qgis:eliminateselectedpolygons", {
                'INPUT': layer,
                'MODE': 1,
                'OUTPUT': out_put
            }, is_child_algorithm=False)
            # for id in layer.selectedFeatureIds():
            #     layer.deleteFeature(id)
            #     layer.commitChanges()
            # # layer.deleteSelectedFeatures()
            # # pydevd_pycharm.settrace('localhost', port=53111, stdoutToServer=True, stderrToServer=True)
            # print(len(layer.selectedFeatureIds()))
            # layer.invertSelection() #将图层反选
            # clone_layer_path = processing.run("native:saveselectedfeatures", {'INPUT': layer, 'OUTPUT': out_put})['OUTPUT']
            # clone_layer  = readVectorFile(clone_layer_path)
            # layer.removeSelection()

            # layer.rollBack() #原图层忽视修改
            # PROJECT.addMapLayer(clone_layer)
            self.progressBar.setValue(100)
            print("已删除选中的细小多边形")
            if self.output_checkBox_2.isChecked() and eli_type != 0:
                myIface = MyIface()
                myIface.addVectorLayer(out_put, layer.name() + "_eliminated:", "ogr")
                # self.iface.addVectorLayer(output, layer.name()+"_generalized:", "ogr")
        elif eli_type == 1 : #合并到临近最大面积
            self.progressBar.setValue(0)
            feedback: QgsProcessingFeedback = None
            context: QgsProcessingContext = None
            print(len(layer.selectedFeatureIds()))
            time_sta = datetime.now()
            # pydevd_pycharm.settrace('localhost', port=53111, stdoutToServer=True, stderrToServer=True)
            runner  = processing.run("qgis:eliminateselectedpolygons",{
                'INPUT':layer,
                'MODE':0,
                'OUTPUT': out_put
            },context=context, feedback=feedback, is_child_algorithm=False)
            self.progressBar.setValue(100)
            time_end = datetime.now()
            print('delta_time:', time_end - time_sta)
            if self.output_checkBox_2.isChecked() and eli_type != 0:
                myIface = MyIface()
                myIface.addVectorLayer(out_put, layer.name() + "_eliminated:", "ogr")
                # self.iface.addVectorLayer(output, layer.name()+"_generalized:", "ogr")
        elif eli_type == 2 : #合并至最长边
            self.progressBar.setValue(0)
            time_sta = datetime.now()
            runner = processing.run("qgis:eliminateselectedpolygons", {
                'INPUT': layer,
                'MODE': 2,
                'OUTPUT': out_put
            })
            self.progressBar.setValue(100)
            time_end = datetime.now()
            print('delta_time:', time_end - time_sta)
            if self.output_checkBox_2.isChecked() and eli_type != 0:
                myIface = MyIface()
                myIface.addVectorLayer(out_put, layer.name() + "_eliminated:", "ogr")
                # self.iface.addVectorLayer(output, layer.name()+"_generalized:", "ogr")

        else:
            QMessageBox.warning(self,'Parameter error','please choose one processing method!')



    def setReadOnly(self):
        """Connect the line edit"""
        self.threshold_Edit.setReadOnly(True)


    def exitWindow(self):
        """This function is used to close the processing window"""
        self.close()

    def get_outFile(self):
        """This function is to make sure the file has a .shp suffix"""
        file_dir = self.output_FileWidget_2.filePath()
        file_name = file_dir.split('\\')[-1]
        if len(file_name.split('.')) == 2 and file_name.split('.')[-1] == 'shp' :
            return file_dir
        else :
            return file_dir + '.shp'


    def cancel_processing(self):
        """When the cancel btn is clicked, the processing progress stops"""
        self.progressBar.setValue(0)
        if self.output_FileWidget_2.filePath() != '' :
            file = self.output_FileWidget_2.filePath()
            print(file)
            filename = file.split('.')[0]
            # filename = filename.split('.')[0]
            # pydevd_pycharm.settrace('localhost', port=53100, stdoutToServer=True, stderrToServer=True)
            remove_filename = filename + '.dbf'
            print(remove_filename)
            os.remove( filename + '.dbf')
            os.remove( filename + '.prj')
            os.remove( filename + '.cpg')
            os.remove( filename + '.shx')
            os.remove( filename + '.shp')
            QMessageBox.warning(self,'Cancel dialog','The processing progress has been stopped')
        else:
            QMessageBox.warning(self,'warning','There is something wrong')

def addVectorLayer(uri, provider, name):
    vl = QgsVectorLayer(uri, name, provider)
    QgsProject.instance().addMapLayer(vl)
    return vl, name

class MyIface(QgisInterface):
    def __init__(self):
        QgisInterface.__init__(self)

    def addVectorLayer(self, path, name, provider):
        return addVectorLayer(path, provider, name)